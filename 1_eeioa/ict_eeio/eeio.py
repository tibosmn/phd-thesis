import pymrio

from ict_eeio.mrio import get_all_industries, get_leontief_flow

# COE2_NAME = "GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)"
COE2_NAME = "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"


def get_cba_impact(
    base: pymrio.IOSystem,
    industry: str,
    impact_category: str = COE2_NAME,
    country: str = "global",
) -> float:
    """
    Retrieve the CBA chosen impact for a given industry and country
    Consumption based = including imports

    D_cba = Consumption based environmental footprint

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
        The cba impact for impact_category
    """
    # Retrive the TOTAL impact from D_cba
    res = base.impacts.D_cba[(country, industry)][impact_category]
    return res


def get_pba_impact(
    base: pymrio.IOSystem,
    industry: str,
    impact_category: str = COE2_NAME,
    country: str = "global",
) -> float:
    """
    Retrieve the PBA impacts for a given industry and country
    Production based = excluding imports

    D_pba = Production based environmental footprint

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
        The pba impact for impact_category
    """
    # Retrive the TOTAL impact from D_pba
    return get_pba_impacts(base, industry, country)[impact_category]


def get_pba_impacts(
    base: pymrio.IOSystem,
    industry: str,
    country: str = "global",
):
    """
    Retrieve ALL PBA impacts CATEGORIES for a given industry and country
    Production based = excluding imports

    D_pba = Production based environmental footprint

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
    """
    # Retrive the TOTAL impact from D_pba
    res = base.impacts.D_pba[(country, industry)]
    return res


def get_impact_unit(base: pymrio.IOSystem, impact: str) -> str:
    """
    Retrieve an impact unit in a given eeio base

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    impact: str
        String of the impact

    Returns
    -------
    str
        impact unit as a string, such as 'kg CO2 eq.'
    """
    return str(base.impacts.unit.loc[impact]["unit"].strip("'"))


def get_total_direct_impact(
    base: pymrio.IOSystem,
    industry: str,
    impact_category: str = COE2_NAME,
    country: str = "global",
) -> float:
    """
    Retrieve the total DIRECT impact and its unit for a given impact category,
    industry and country

    Matrix F: total direct impacts

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    impact: str
        String of the impact, such as
        GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)
    industry: str
        Chosen industry, such as
        'Cattle farming'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The total DIRECT impact
    """

    # Retrive the direct TOTAL impact from matrix F

    if impact_category != "F-gases":
        res = base.impacts.F[(country, industry)][impact_category]
    else:
        ghg = base.impacts.F[(country, industry)][
            "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
        ]
        # Convert to gigagrams to kilograms
        co2 = base.impacts.F[(country, industry)][
            "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)"
        ]
        ch4 = base.impacts.F[(country, industry)][
            "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)"
        ]
        n20 = base.impacts.F[(country, industry)][
            "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)"
        ]
        # Compute the diff between aggregegated GHG and available categories
        res = ghg - (co2 + ch4 + n20)
    return float(res)  # , unit


def get_direct_impact_coefficient(
    base: pymrio.IOSystem,
    industry: str,
    impact_category: str = COE2_NAME,
    country: str = "global",
) -> float:
    """
    Retrieve the direct impact COEFFICIENT for a given impact category,
    industry and country

    Matrix S = normalised output

    Parameters
    ----------
    base : pymrio.IOSystem
        eeio base to work with
    impact : str
        String of the impact, such as
        GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)
    industry: str
        Chosen industry, such as
        'Cattle farming'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The impact COEFFICIENT
    """
    # # Retrive the industry output unit, such as M.EUR
    # ind_out_unit = get_industry_output_unit(base, industry, country)
    # # Retrieve the impact unit
    # unit = get_impact_unit(base, impact_category)
    # # Impact is thus divided by industry output unit
    # res_unit = unit + "/" + ind_out_unit

    # Retrieve the direct impact COEFFICIENT from matrix S
    res = base.impacts.S[(country, industry)][impact_category]

    return float(res)


def get_final_demand_impact(
    base: pymrio.IOSystem,
    demand_category: str,
    impact_category: str = COE2_NAME,
    country: str = "global",
) -> float:
    """
    Retrieve the final demand impact and its unit for a given impact category,
    demand category and country

    Matrix F_Y: Total impact by demand category

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    impact_category: str
        String of the impact category, such as
        GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)
    demand_category: str
        Chosen final demand category, such as
        'Final consumption expenditure by households'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The final demand impact
    """
    # Retrive the final demand impact from matrix F_Y
    res = base.impacts.F_Y[(country, demand_category)][impact_category]
    # Retrieve the impact associated unit
    # unit = get_impact_unit(base, impact)
    return float(res)  # , unit


def get_final_demand_impact_coefficient(
    base: pymrio.IOSystem,
    impact_category: str,
    demand_category: str,
    country: str = "global",
) -> float:
    """
    Retrieve the final demand impact COEFFICIENT for a given impact category,
    demand category and country

    Matrix S_Y = final demand impact coefficients

    Parameters
    ----------
    base : pymrio.IOSystem
        eeio base to work with
    impact_category : str
        String of the impact category, such as
        GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)
    demand_category: str
        Chosen final demand category, such as
        'Final consumption expenditure by households'
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The final demand impact COEFFICIENT
    """
    # # Retrieve the impact unit
    # unit = get_impact_unit(base, impact)
    # # Impact is thus divided by industry output unit
    # res_unit = unit + "/" + ind_out_unit

    # Retrieve the direct impact COEFFICIENT from matrix S
    res = base.impacts.S_Y[(country, demand_category)][impact_category]

    return float(res)


def get_all_impact_categories(base: pymrio.IOSystem) -> list[str]:
    """
    Return a list of all impact categories available within a pymrio database

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with

    Returns
    -------
    list[str]
        Impact category list as str
    """
    return list(base.impacts.S.index)


def get_all_satellites_stressors(base: pymrio.IOSystem) -> list[str]:
    """
    Return a list of all satellite stressos available within a pymrio database

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with

    Returns
    -------
    list[str]
        Stressos list as str
    """
    return list(base.satellite.S.index)


def compute_udd_impacts(
    base: pymrio.IOSystem,
    industry: str,
    country: str = "global",
) -> tuple[float, float, float, float]:
    """
    Compute upstream, direct and downstream impacts for a specified industry
    and return them with the total for all impact categories

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
            industry: str
    Chosen industry, such as
        'Cattle farming'
    impact_category: str
        String of the impact category, such as
        GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The total upstream + direct + downstream impact
    float
        The upstream impact
    float
        The direct impact
    float
        The downstream impact
    """
    sum_y = base.Y.sum(axis=1)
    S = base.impacts.S[(country, industry)]

    downstream = 0
    for buyer in get_all_industries(base):
        if buyer != industry:  # Already accounted for as direct impact
            downstream += (
                base.L[(country, buyer)][(country, industry)] * sum_y[(country, buyer)]
            )

    direct = (
        base.L[(country, industry)][(country, industry)] * sum_y[(country, industry)]
    )

    # Multiply by industry impact factor
    downstream *= S
    direct *= S

    upstream = 0
    for supplier in get_all_industries(base):
        if supplier != industry:
            upstream += (
                base.L[(country, industry)][(country, supplier)]
                * sum_y[(country, industry)]
                * base.impacts.S[(country, supplier)]
            )
    return upstream + direct + downstream, upstream, direct, downstream


def compute_udd_stressors(
    base: pymrio.IOSystem,
    industry: str,
    country: str = "global",
) -> tuple[float, float, float, float]:
    """
    Compute upstream, direct and downstream stressors for a specified industry
    and return them with the total for all impact categories

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
            industry: str
    Chosen industry, such as
        'Cattle farming'
    impact_category: str
        String of the impact category, such as
        GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The total upstream + direct + downstream stressors
    float
        The upstream stressors
    float
        The direct stressors
    float
        The downstream stressors
    """
    downstream = 0
    sum_y = base.Y.sum(axis=1)

    S = get_direct_impact_coefficient(
        base=base, industry=industry, impact_category=impact_category
    )
    for buyer in get_all_industries(base):
        if buyer != industry:
            downstream += (
                base.L[("global", buyer)][("global", industry)]
                * sum_y[("global", buyer)]
            )

    direct = (
        base.L[("global", industry)][("global", industry)] * sum_y[("global", industry)]
    )

    downstream *= S
    direct *= S

    upstream = 0
    for supplier in get_all_industries(base):
        if supplier != industry:
            upstream += (
                base.L[("global", industry)][("global", supplier)]
                * base.Y.sum(axis=1)[("global", industry)]
                * get_direct_impact_coefficient(
                    base, supplier, impact_category=impact_category
                )
            )
    return upstream + direct + downstream, upstream, direct, downstream


def compute_udd_impact(
    base: pymrio.IOSystem,
    industry: str,
    impact_category: str = COE2_NAME,
    country: str = "global",
) -> tuple[float, float, float, float]:
    """
    Compute upstream, direct and downstream impacts for a specified industry
    and return them with the total for a given impact category

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    industry: str
    Chosen industry, such as
        'Cattle farming'
    impact_category: str
        String of the impact category, such as
        GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)
    country: str
        Chosen country abbrevation code, such as
        'FR'

    Returns
    -------
    float
        The total upstream + direct + downstream impact
    float
        The upstream impact
    float
        The direct impact
    float
        The downstream impact
    """
    udd, upstream, direct, downstream = compute_udd_impacts(base, industry=industry)
    return (
        udd[impact_category],
        upstream[impact_category],
        direct[impact_category],
        downstream[impact_category],
    )


def get_stressor_unit(base: pymrio.IOSystem, stressor: str) -> str:
    """
    Return a stressor's unit

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    """
    return base.satellite.unit.loc[stressor]["unit"]


def get_supplier_impacts(
    base: pymrio.IOSystem, buyer: str, supplier: str, final_demand: float
) -> str:
    """
    For a chosen industry, ie the buyer, get stressor's impact from a
    suplying industry from the spcified demand
    The sum of these impacts is thus the cba impact.

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    buyer: str
        The buying industry, such as
        'Cattle farming'
    buyer: str
        The supplying industry, such as
        'Cattle farming'
    final_demand:
        Final demand for the buying industry, can be computed using
        mrio.get_total_final_demand()

    final demand Y
    """
    s = base.impacts.S[("global", supplier)]
    leontief = get_leontief_flow(base, buyer=buyer, supplier=supplier)
    total = s * leontief * final_demand
    return total


def get_supplier_impact(
    base: pymrio.IOSystem,
    buyer: str,
    supplier: str,
    final_demand: float,
    impact_category: str,
) -> str:
    """
    For a chosen industry, ie the buyer, get stressor's impact from a
    suplying industry from the spcified demand
    The sum of these impacts is thus the cba impact.

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    buyer: str
        The buying industry, such as
        'Cattle farming'
    buyer: str
        The supplying industry, such as
        'Cattle farming'
    final_demand:
        Final demand for the buying industry, can be computed using
        mrio.get_total_final_demand()

    final demand Y
    """
    s = base.impacts.S[("global", supplier)].loc[impact_category]
    leontief = get_leontief_flow(base, buyer=buyer, supplier=supplier)
    total = s * leontief * final_demand
    return total


def get_supplier_impact_stressors(
    base: pymrio.IOSystem, buyer: str, supplier: str, final_demand: float
) -> str:
    """
    For a chosen industry, ie the buyer, get stressor's impact from a
    suplying industry from the spcified demand
    The sum of these impacts is thus the cba impact.

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    buyer: str
        The buying industry, such as
        'Cattle farming'
    buyer: str
        The supplying industry, such as
        'Cattle farming'
    final_demand:
        Final demand for the buying industry, can be computed using
        mrio.get_total_final_demand()

    final demand Y
    """
    s = base.satellite.S[("global", supplier)]
    leontief = get_leontief_flow(base, buyer=buyer, supplier=supplier)
    total = s * leontief * final_demand
    return total


def get_supplier_impact_stressor(
    base: pymrio.IOSystem, buyer: str, supplier: str, final_demand: float, stressor: str
) -> str:
    """
    For a chosen industry, ie the buyer, get stressor's impact from a
    suplying industry from the spcified demand
    The sum of these impacts is thus the cba impact.

    Parameters
    ----------
    base: pymrio.IOSystem
        eeio base to work with
    buyer: str
        The buying industry, such as
        'Cattle farming'
    buyer: str
        The supplying industry, such as
        'Cattle farming'
    final_demand:
        Final demand for the buying industry, can be computed using
        mrio.get_total_final_demand()

    final demand Y
    """
    s = base.satellite.S[("global", supplier)][stressor]
    leontief = get_leontief_flow(base, buyer=buyer, supplier=supplier)
    total = s * leontief * final_demand
    return total
