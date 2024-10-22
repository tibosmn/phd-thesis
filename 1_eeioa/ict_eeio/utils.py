def kg_to_Mt(value: float) -> float:
    """
    Convert a float in kilograms to megaton

    Parameters
    ----------
    value: float
        The kg to convert

    Returns
    -------
    float
        value converted in megaton
    """
    return value * 1e-9


def kg_to_Gt(value: float) -> float:
    """
    Convert a float in kilograms to Gigatons

    Parameters
    ----------
    value: float
        The kg to convert

    Returns
    -------
    float
        value converted in Gigatons
    """
    return value * 1e-12


def Mt_to_Gt(value: float) -> float:
    """
    Convert a float in Megatons to Gigatons

    Parameters
    ----------
    value: float
        The Mt to convert

    Returns
    -------
    float
        value converted in Gigatons
    """
    return value / 1000


def Mm3_to_m3(value: float) -> float:
    """
    Convert a cubic megametre Mm3 value to Gigatons

    Parameters
    ----------
    value: float
        The kg to convert

    Returns
    -------
    float
        value converted in Gigatons
    """
    return value / 1e18
