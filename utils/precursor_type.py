def precursor_type(neutral_mass: float, precursor_mz: float) -> str:
    """
    Deduce the precursor type from the neutral mass and the precursor m/z ratio.

    :param neutral_mass: calculate neutral mass (Daltons).
    :type neutral_mass: float
    :param precursor_mz: precursor m/z ratio (Daltons).
    :type precursor_mz: float
    :return: "[M-H]-" if neutral_mass > precursor_mz, "[M+H]+" otherwise
    :rtype: str
    """
    return "[M-H]-" if neutral_mass > precursor_mz else "[M+H]+"