def exact_mass_calculation(Precursor_MZ, ion_mode):
    """exact_mass_calculation _summary_

    :param Precursor_MZ: _description_
    :type Precursor_MZ: _type_
    :param ion_mode: _description_
    :type ion_mode: _type_
    :raises TypeError: _description_
    :return: _description_
    :rtype: _type_
    """
    try:
        mz = float(Precursor_MZ)
    except (TypeError, ValueError):
        raise TypeError("Precursor_MZ must be a numeric value")
    
    # Masse du proton en Da
    masse_proton = 1.007276

    # En mode positif, la molécule a gagné un proton donc retrait pour obtenir la masse neutre
    if ion_mode == "Positive":
        return round(mz - masse_proton, 6)
    elif ion_mode == "Negative":
        return round(mz + masse_proton, 6)
    else:
        raise ValueError(f"ion_mode inconnu : {ion_mode!r}. Valeurs acceptées : 'Positive' ou 'Negative'.")