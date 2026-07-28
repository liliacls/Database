from molmass import Formula

def molecular_weight(formula: str) -> float | None:
    """
    Calcule la masse moléculaire moyenne du lipide à partir de sa formule chimique.
    Utilise molmass.Formula.mass pour le calcul, puis arrondit à 6 décimales.
    Retourne None sans lever d'exception si la formule est None, vide ou invalide.

    :param formula: formule chimique
    :type formula: str
    :return: masse moléculaire moyenne arrondie à 6 décimales, ou None si invalide.
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
