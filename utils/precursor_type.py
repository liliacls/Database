def precursor_type(neutral_mass: float, precursor_mz: float) -> str:
    """
    Déduit le type de précurseur à partir de la masse neutre et du rapport m/z du précurseur.

    :param neutral_mass: masse neutre calculée (Daltons).
    :type neutral_mass: float
    :param precursor_mz: rapport m/z du précurseur.
    :type precursor_mz: float
    :return: "[M-H]-" si mode négatif, "[M+H]+" si mode positif.
    :rtype: str
    """
    return "[M-H]-" if neutral_mass > precursor_mz else "[M+H]+"