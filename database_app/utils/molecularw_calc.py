from molmass import Formula

def molecularw_calc(formula):
    """Calcule le poids moléculaire à partir de la formule brute."""
    try:
        f = Formula(formula)
        return int(round(f.mass, 0))
    except Exception:
        return None