from molmass import Formula

def molecularw_calculation(formula):
    """Calcule le poids moléculaire moyen du lipide à partir de la formule brute chimique.
    Utilise molmass.Formula.mass pour le calcul, puis arrondit à l'entier le plus proche.
    Retourne None sans lever d'exception si la formule est nulle, vide ou invalide.

    :param formula: formule brute chimique
    :type formula: str
    :return: poids moléculaire moyen arrondi à l'entier le plus proche, ou None si invalide.
    :rtype: int or None
    """
    if formula is None:
        return None
    
    try:
        s = str(formula).strip()
        f = Formula(s)
        return int(round(f.mass, 0))
    except (ValueError, TypeError):
        return None