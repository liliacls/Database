from molmass import Formula


def monoisotopic_mass(formula: str | None) -> float | None:
    """
    Compute the monoisotopic mass of the lipid from its chemical formula.
    Uses molmass.Formula.monoisotopic_mass for the calculation.
    Returns None without raising an exception if the formula is null, empty, or invalid.

    :param formula: chemical formula
    :type formula: str or None
    :return: monoisotopic mass rounded to 6 decimal places, or None if invalid.
    :rtype: float or None
    """
    if formula is None:
        return None

    try:
        s = str(formula).strip()
        if not s:
            return None
        f = Formula(s)
        return round(float(f.monoisotopic_mass), 6)
    except (ValueError, TypeError):
        return None
