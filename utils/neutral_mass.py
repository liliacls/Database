def neutral_mass_cal(Precursor_MZ, ion_mode):
    """Calcule la masse neutre à partir du rapport m/z du précurseur et du mode d'ionisation.

    :param Precursor_MZ: rapport m/z du précurseur mesuré par le spectromètre de masse.
    :type Precursor_MZ: float
    :param ion_mode: mode d'ionisation "Positive" ou "Negative".
    :type ion_mode: str
    :raises TypeError: si Precursor_MZ ne peut pas être converti en float.
    :raises ValueError: si ion_mode n'est ni "Positive" ni "Negative".
    :return: masse neutre en Daltons, arrondie à 6 décimales.
    :rtype: float
    """
    try:
        mz = float(Precursor_MZ)
    except (TypeError, ValueError):
        raise TypeError("Precursor_MZ must be a numeric value")
    
    # Masse du proton en Da
    masse_proton = 1.007276

    # En mode positif, la molécule a gagné un proton donc retrait pour obtenir la masse neutre
    # [M+H]+ : M = MZ - proton
    if ion_mode == "Positive":
        return round(mz - masse_proton, 6)
    # En mode négatif, la molécule a perdu un proton donc ajout pour obtenir la masse neutre
    # [M-H]- : M = MZ + proton
    elif ion_mode == "Negative":
        return round(mz + masse_proton, 6)
    else:
        raise ValueError(f"ion_mode inconnu : {ion_mode!r}. Valeurs acceptées : 'Positive' ou 'Negative'.")