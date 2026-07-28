from molmass import Formula

def monoisotopic_mass(formula: str | None) -> float | None:
    """
    Calcule la masse monoisotopique du lipide à partir de sa formule chimique.
    Utilise molmass.Formula.monoisotopic_mass pour le calcul.
    Retourne None sans lever d'exception si la formule est nulle, vide ou invalide.

    :param formula: formule chimique
    :type formula: str or None
    :return: masse monoisotopique arrondie à 6 décimales, ou None si invalide.
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
