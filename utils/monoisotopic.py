from molmass import Formula

def molecularw_calculation(formula):
    """
    Calcule la masse monoisotopique du lipide à partir de la formule brute chimique.
    Utilise molmass.Formula.monoisotopic_mass pour le calcul.
    Retourne None sans lever d'exception si la formule est nulle, vide ou invalide.

    :param formula: formule brute chimique
    :type formula: str
    :return: masse monoisotopique arrondie à 6 décimales, ou None si invalide.
    :rtype: float or None
    """
    if formula is None:
        return None

    try:
        s = str(formula).strip()
        f = Formula(s)
        return round(float(f.monoisotopic_mass), 6)
    except (ValueError, TypeError):
        return None