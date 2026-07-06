from molmass import Formula


def molecular_weight(formula: str) -> float | None:
    """
    Compute the average molecular weight of the lipid from its chemical formula.
    Uses molmass.Formula.mass for the calculation, then rounds to 6 decimal places.
    Returns None without raising an exception if the formula is None, empty, or invalid.

    :param formula: chemical formula
    :type formula: str
    :return: average molecular weight rounded to 6 decimal places, or None if invalid.
    :rtype: float or None
    """
    if formula is None:
        return None

    try:
        s = str(formula).strip()
        if not s:
            return None
        f = Formula(s)
        return round(float(f.mass), 6)
    except (ValueError, TypeError):
        return None
