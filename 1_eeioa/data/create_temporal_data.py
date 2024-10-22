import pandas as pd
import datetime
from ict_eeio.eeio import (
    COE2_NAME,
    get_all_impact_categories,
    get_all_satellites_stressors,
    get_supplier_impact,
    get_supplier_impact_stressor,
    get_supplier_impacts,
    get_supplier_impact_stressors,
)
from ict_eeio.mrio import (
    aggregate_sectors,
    get_all_industries,
    get_total_final_demand,
    load_base,
    simplify_divisions,
    simplify_sections,
)
from ict_eeio.industries import ict_industries, energy_industries
from ict_eeio.satellites import mineral_stressors
import os


def create_temporal_data(
    from_year: int,
    to_year: int,
    wanted_impacts: list[str],
    wanted_stressors: list[str],
    file_prefix: str,
    reduce_sectors=False,
    wanted_industries: list[str] = [],
    aggregate_industries: list[str] = [],
    aggregate_name: str = "Aggregate",
    classification: str = "ixi",
) -> None:
    """


    Parameters
    ----------
    from_year: int
        Year to start temporal computations, such as 1995
    to_year: int
        Year to end temporal computations, such as 2022
    wanted_impacts:
        List of impact categories to include in the calculations
    file_prefix: str
        The prefix for the saved file
    reduce_sectors: bool
        Wether to lessen the number of ISIC sectors or not (False by default)
    wanted_industries:
        List of industries to include in the calculations.
        If empty, all industries will be considered
    aggregate_industries
         A list of industry strings to aggregate
    aggregate_name
        If aggregated, specify the name
    """

    # Prepare file names
    file_name = (
        file_prefix
        + ("_agg" if aggregate_industries else "")
        + "_"
        + str(from_year)
        + "_"
        + str(to_year)
        + ("_simplified" if reduce_sectors else "")
        + ".csv"
    )
    pba_file = "./data/new/" + classification + "/pba/" + file_name
    cba_file = "./data/new/" + classification + "/cba/" + file_name
    upstream_file = "./data/new/" + classification + "/upstream/" + file_name
    cba_stressor_file = "./data/new/" + classification + "/cba_stressor/" + file_name
    upstream_stressor_file = (
        "./data/new/" + classification + "/upstream_stressor/" + file_name
    )
    y_file = "./data/new/" + classification + "/Y/" + file_name
    s_file = "./data/new/" + classification + "/S/" + file_name
    s_stressors_file = "./data/new/" + classification + "/S_stressors/" + file_name
    l_file = "./data/new/" + classification + "/L/" + file_name
    x_file = "./data/new/" + classification + "/x/" + file_name

    # Delete existing files
    os.remove(pba_file) if os.path.exists(pba_file) else None
    os.remove(cba_file) if os.path.exists(cba_file) else None
    os.remove(upstream_file) if os.path.exists(upstream_file) else None
    os.remove(cba_stressor_file) if os.path.exists(cba_stressor_file) else None
    (
        os.remove(upstream_stressor_file)
        if os.path.exists(upstream_stressor_file)
        else None
    )
    os.remove(y_file) if os.path.exists(y_file) else None
    os.remove(s_file) if os.path.exists(s_file) else None
    os.remove(s_stressors_file) if os.path.exists(s_stressors_file) else None
    os.remove(l_file) if os.path.exists(l_file) else None
    os.remove(x_file) if os.path.exists(x_file) else None

    # Prepare years rangech
    years = range(from_year, to_year + 1)
    # To fill the data, iterate through all years
    for year in years:
        print("--------------------YEAR " + str(year) + "--------------------")
        print(datetime.datetime.now())
        print()

        # Load base for one year
        exio = load_base(str(year), classification=classification)
        print("Base loaded: " + str(datetime.datetime.now()))

        if aggregate_industries:
            # Aggregate industries if needed
            aggregate_sectors(
                exio, industries=aggregate_industries, aggregation_name=aggregate_name
            )

        if reduce_sectors:
            # Reduce industries number if needed
            simplify_divisions(exio)

        # Retrieve all industries if wanted ones are not specified
        if not wanted_industries:
            wanted_industries = get_all_industries(exio)

        # We create our tuples which we'll create ou row MultiIndex from
        # Multi index format is (year, industry)
        # We purposedly create one df per year to append it at the end of the csv file,
        # in order to update it rather than writing it all at once
        index_tuples = []

        # Create one tuple per industry
        for industry in get_all_industries(exio):
            index_tuples.append((str(year), industry))

        # Create index accordingly
        index = pd.MultiIndex.from_tuples(index_tuples)

        # W create DataFrames with wanted formats
        pba_df = pd.DataFrame(columns=exio.impacts.D_pba.index, index=index)
        cba_df = pd.DataFrame(columns=exio.impacts.D_cba.index, index=index)
        s_df = pd.DataFrame(columns=exio.impacts.S.index, index=index)
        s_stressors_df = pd.DataFrame(columns=exio.satellite.S.index, index=index)
        y_df = pd.DataFrame(columns=exio.Y.index.levels[1], index=index)
        l_df = pd.DataFrame(columns=exio.L.columns.levels[1], index=index)
        cba_stressors_df = pd.DataFrame(columns=exio.satellite.D_cba.index, index=index)
        x_df = pd.DataFrame(
            columns=["Intermediate demand", "Final demand", "x"], index=index
        )

        # Upstream impacts
        upstream_industry_tuples = []

        for category in wanted_impacts:
            for industry in get_all_industries(exio):
                upstream_industry_tuples.append((industry, category))

        upstream_df = pd.DataFrame(
            columns=pd.MultiIndex.from_tuples(upstream_industry_tuples), index=index
        )

        # Upstream stressors
        stressor_industry_tuples = []

        for stressor in wanted_stressors:
            for industry in get_all_industries(exio):
                stressor_industry_tuples.append((industry, stressor))

        upstream_stressors_df = pd.DataFrame(
            columns=pd.MultiIndex.from_tuples(stressor_industry_tuples), index=index
        )

        # For S, we retrieve it for all industries
        for industry in get_all_industries(exio):
            s_df.loc[(str(year), industry)] = exio.impacts.S[("global", industry)]
            s_stressors_df.loc[(str(year), industry)] = exio.satellite.S[
                ("global", industry)
            ]
            l_df.loc[(str(year), industry)] = exio.L[("global", industry)]["global"]

        print("Starting upstream computation: " + str(datetime.datetime.now()))
        # Iterate through all industries to retrieve data
        # If some industries are aggregated, get_all_industries wil return the right ones
        for industry in wanted_industries:
            # Impacts
            pba_df.loc[(str(year), industry)] = exio.impacts.D_pba[("global", industry)]
            cba_df.loc[(str(year), industry)] = exio.impacts.D_cba[("global", industry)]

            y_df.loc[(str(year), industry)] = exio.Y.sum(axis=1)["global"]
            cba_stressors_df.loc[(str(year), industry)] = exio.satellite.D_cba[
                ("global", industry)
            ]

            # Industry output
            x_df.loc[(str(year), industry)]["Intermediate demand"] = exio.Z.sum(axis=1)[
                ("global", industry)
            ]
            x_df.loc[(str(year), industry)]["Final demand"] = exio.Y.sum(axis=1)[
                ("global", industry)
            ]
            x_df.loc[(str(year), industry)]["x"] = exio.x.loc["global", industry][
                "indout"
            ]

            # Compute the final demand for the industry considered
            Y = get_total_final_demand(exio, industry)

            # Assess the immpact from each supplier
            for supplier in get_all_industries(exio):
                for impact_category in wanted_impacts:
                    upstream_df.loc[(str(year), industry)][
                        supplier, impact_category
                    ] = get_supplier_impact(
                        exio,
                        buyer=industry,
                        supplier=supplier,
                        impact_category=impact_category,
                        final_demand=Y,
                    )
                for stressor in wanted_stressors:
                    upstream_stressors_df.loc[(str(year), industry)][
                        (supplier, stressor)
                    ] = get_supplier_impact_stressor(
                        exio,
                        buyer=industry,
                        supplier=supplier,
                        stressor=stressor,
                        final_demand=Y,
                    )

        print("Upstream computation done: " + str(datetime.datetime.now()))

        # Finally we append data to the csv file
        pba_df.to_csv(pba_file, mode="a", header=not os.path.exists(pba_file))
        cba_df.to_csv(cba_file, mode="a", header=not os.path.exists(cba_file))
        upstream_df.to_csv(cba_file, mode="a", header=not os.path.exists(upstream_file))
        cba_stressors_df.to_csv(
            cba_stressor_file, mode="a", header=not os.path.exists(cba_stressor_file)
        )
        upstream_stressors_df.to_csv(
            upstream_stressor_file,
            mode="a",
            header=not os.path.exists(upstream_stressor_file),
        )
        s_df.to_csv(s_file, mode="a", header=not os.path.exists(s_file))
        x_df.to_csv(x_file, mode="a", header=not os.path.exists(x_file))

        s_stressors_df.to_csv(
            s_stressors_file, mode="a", header=not os.path.exists(s_stressors_file)
        )
        y_df.to_csv(y_file, mode="a", header=not os.path.exists(y_file))
        l_df.to_csv(l_file, mode="a", header=not os.path.exists(l_file))
        print("Written to files: " + str(datetime.datetime.now()))


start = 1995
end = 2022

# ICT aggregated sectors not simplified
create_temporal_data(
    from_year=start,
    to_year=end,
    wanted_industries=["ICT"],
    wanted_impacts=[COE2_NAME],
    wanted_stressors=mineral_stressors,
    file_prefix="ict",
    reduce_sectors=False,
    aggregate_name="ICT",
    aggregate_industries=ict_industries,
    classification="ixi",
)

# ICT aggregated sectors simplified
create_temporal_data(
    from_year=start,
    to_year=end,
    wanted_industries=[],
    wanted_impacts=[COE2_NAME],
    wanted_stressors=mineral_stressors,
    file_prefix="ict",
    reduce_sectors=True,
    aggregate_name="ICT",
    aggregate_industries=ict_industries,
    classification="ixi",
)


# Energy aggregated sectors not simplified
create_temporal_data(
    from_year=start,
    to_year=end,
    wanted_industries=["energy"],
    wanted_impacts=[COE2_NAME],
    wanted_stressors=mineral_stressors,
    file_prefix="energy",
    reduce_sectors=False,
    aggregate_name="energy",
    aggregate_industries=energy_industries,
    classification="ixi",
)


# Energy aggregated sectors simplified
create_temporal_data(
    from_year=start,
    to_year=end,
    wanted_industries=["energy"],
    wanted_impacts=[COE2_NAME],
    wanted_stressors=mineral_stressors,
    file_prefix="energy",
    reduce_sectors=True,
    aggregate_name="energy",
    aggregate_industries=energy_industries,
    classification="ixi",
)

# All sectors not simplified
create_temporal_data(
    from_year=start,
    to_year=end,
    wanted_industries=[],
    wanted_impacts=[COE2_NAME],
    wanted_stressors=mineral_stressors,
    file_prefix="all",
    reduce_sectors=False,
    classification="ixi",
)
