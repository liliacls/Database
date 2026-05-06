from molmass import Formula

def molecularw_calculation(formula):
    """Calcule le poids moléculaire à partir de la formule brute."""
    if formula is None:
        return None
    
    try:
        s = str(formula).strip()
        f = Formula(s)
        return int(round(f.mass, 0))
    except (ValueError, TypeError):
        return None