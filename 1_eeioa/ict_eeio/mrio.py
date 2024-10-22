import warnings
import pymrio
from ict_eeio.industries import isic_sections, isic_divisions


def load_base(
    year: str,
    classification: str = "ixi",
    aggregate_countries: bool = True,
) -> pymrio.IOSystem:
    """
    Load an exio base for a given year and classification
    Aggregate all regions into a single one, 'global'
    Compute missing tables (A, L...)

    Parameters
    ----------
    year: str
        chosen year to load, i.e. '2015'
    classification: str
        Classification to load, 'ixi' (default, by industry)
         or 'pxp' (by product)=
    aggregate_countries: bool
        Wether to aggregate all countries into a single one or not

    Returns
    -------
    pymrio.IOSystem
        The loaded base, aggregated into 'global' regions
         with missing tables computed
    """
    with warnings.catch_warnings():
        # We hide pandas future warning due to pymrio
        warnings.simplefilter(action="ignore", category=FutureWarning)
        # Load chosen year and format
        base = pymrio.parse_exiobase3(
            path="./exio3/IOT_" + str(year) + "_" + classification + ".zip"
        )

        if aggregate_countries:
            # Aggregate regions into a single one
            base = base.aggregate(region_agg="global")

        # Compute missing tables
        base.calc_all()
        return base


def aggregate_sectors(
    base: pymrio.IOSystem,
    industries: list[str],
    aggregation_name: str,
) -> None:
    """
    Aggregate multiple industries into a single one for an mrio databse
    Update directly within the given base

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    industries: list[str]
        List of industries name to aggregate
    aggregation_name: str
        The name of the single aggregated industry, such as
        'ICT'
    classification: str
        EXIOBASE classification, wether 'ixi' or 'pxp'
    """
    # Create a dict with entries 'sector': 'AGGREGATE_NAME'
    # which will be used to rename them all
    aggregates = {}
    for sector in industries:
        aggregates[sector] = aggregation_name

    # Following https://pymrio.readthedocs.io/en/latest/notebooks/aggregation_examples.html
    with warnings.catch_warnings():
        # We hide pandas future warning due to pymrio
        warnings.simplefilter(action="ignore", category=FutureWarning)
        base.rename_sectors(aggregates).aggregate_duplicates()

        # Computation working weirdly after sectors aggregation,
        # reseting all computed tables before computing again fixes the problem
        base.reset_all_full()
        # Compute missing tables
        base.calc_all()


def simplify_divisions(base: pymrio.IOSystem) -> None:
    """
    Simplify sector's to ISIC divisions to lower their number

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    """
    for aggregate_name in isic_divisions:
        aggregate_sectors(
            base,
            industries=isic_divisions[aggregate_name],
            aggregation_name=aggregate_name,
        )


def simplify_sections(base: pymrio.IOSystem) -> None:
    """
    Simplify sector's to ISIC sections to lower their number

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    """
    for aggregate_name in isic_sections:
        aggregate_sectors(
            base,
            industries=isic_sections[aggregate_name],
            aggregation_name=aggregate_name,
        )


def get_monetary_flow(
    base: pymrio.IOSystem, supplier: str, buyer: str, country: str = "global"
) -> float:
    """
    Return the total monetary flow between two industries
    From input towards output
    To produce column, buy from row, so monetary flow from column to row
    i -> j, where i = row -> j = column

    We want supplier -> buyer

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    supplier: str
        Input industry, to get the dependency from
    buyer: str
        Output industry, which we want to see the dependency to input

    Returns
    -------
    float
        Monetary flows between two sectors
    """
    column = buyer
    line = supplier

    return base.Z[(country, column)][(country, line)]


def get_leontief_flow(
    base: pymrio.IOSystem, supplier: str, buyer: str, country: str = "global"
) -> float:
    """
    Return the LEONTIEF matrix value between to industries
    From input towards output
    To produce column, buy from row, so monetary flow from column to row
    i -> j, where i = row -> j = column

    We want supplier -> buyer

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    supplier: str
        Input industry, to get the dependency from
    buyer: str
        Output industry, which we want to see the dependency to input

    Returns
    -------
    float
        Leontief flows between two sectors
    """
    column = buyer
    line = supplier

    return base.L[(country, column)][(country, line)]


def get_factor_input_per_Y_unit(
    base: pymrio.IOSystem,
    supplier: str,
    buyer: str,
    country: str = "global",
) -> float:
    """
    Return the amount of input required per unit of output

    Return the factor input required per unit(often $) of final demand Y
    Retrieved from A, the normalised version of industry flows Z

    i.e. for one unit of demand Y for source, how much target is required

    A, is a square table with elements Aij,
     representing the amount of input i required per unit of output j
     where i = lines and j = columns

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    supplier: str
        Supplier, to get the dependency from
    buyer: str
        Buyer, which we want to see the dependency to input
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        Output value
    """
    column = buyer
    line = supplier

    return base.A[(country, column)][(country, line)]


def get_industry_output_unit(
    base: pymrio.IOSystem, industry: str, country: str = "global"
) -> str:
    """
    Retrieve the unit for and industry output

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    industry: str
        String of the industry, such as 'Cattle farming'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    str
        Output UNIT as a string, such as 'M.EUR'
    """
    return base.unit.loc[country].loc[industry]["unit"]


def get_industry_output(
    base: pymrio.IOSystem, industry: str, country: str = "global"
) -> float:
    """
    Retrieve the output for a single industry and cuntry inside an mrio database

    column x = industry output
        sum_columns(Z) + sum_columns(Y)

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    industry: str
        Chosen industry, such as
        'Cattle farming'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The industry output
    str
        The output unit, such as M.EUR
    """
    # Retrieve industry output from column x
    res = base.x.loc[country, industry]["indout"]
    # # Retrieve this output unit
    # ind_out_unit = get_industry_output_unit(base, industry, country)

    return float(res)  # , ind_out_unit


def get_total_final_demand(
    base: pymrio.IOSystem, industry: str, country: str = "global"
) -> float:
    """
    Retrieve the final demand for a chosen sector

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    industry: str
        Chosen industry, such as
        'Cattle farming'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The final demand
    """
    return base.Y.sum(axis=1)[("global", industry)]


def get_global_intermediate_demand(
    base: pymrio.IOSystem, industry: str, country: str = "global"
) -> float:
    """
    Retrieve the intermediate demand or inter-industry demand for a chosen sector

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    industry: str
        Chosen industry, such as
        'Cattle farming'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The intermediate demand or inter-industry demand
    """
    return base.Z.sum(axis=1)[("global", industry)]


def get_all_industries(base: pymrio.IOSystem) -> list[str]:
    """
    Return a list of all industries names within a pymrio database

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with

    Returns
    -------
    list[str]
        Industry names as str
    """
    return list(base.Z["global"].columns)


def get_demand_categories(base: pymrio.IOSystem) -> list[str]:
    """
    Return a list of all demand category names within a pymrio database

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with

    Returns
    -------
    list[str]
        Demand category names as str
    """
    return list(base.Y["global"].columns)
