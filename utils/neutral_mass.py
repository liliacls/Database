import math

def neutral_mass(Precursor_MZ: float, ion_mode: str) -> float:
    """
    Calculate the neutral mass from the precursor m/z ratio and the ionization mode specified in step 1 of Integration page

    :param Precursor_MZ: m/z ratio of the precursor.
    :type Precursor_MZ: float
    :param ion_mode: ionization mode "Positive" or "Negative"
    :type ion_mode: str
    :raises TypeError: if Precursor_MZ cannot be converted to a float.
    :raises ValueError: if Precursor_MZ is NaN or not strictly positive, or if ion_mode is neither "Positive" nor "Negative".
    :return: neutral mass in Daltons, rounded to 6 decimal places.
    :rtype: float
    """
    try:
        mz = float(Precursor_MZ)
    except (TypeError, ValueError):
        raise TypeError("Precursor_MZ must be a numeric value")

    if math.isnan(mz):
        raise ValueError("Precursor_MZ cannot be NaN")
    
    if mz <= 0:
        raise ValueError(f"Precursor_MZ can be strictly positive : {mz}")

    if not isinstance(ion_mode, str):
        raise ValueError(f"ion_mode unknown : {ion_mode!r}. Accepted values : 'Positive' or 'Negative'.")

    mode = ion_mode.strip().capitalize()

    # Proton mass in Da
    masse_proton = 1.007276

    # In positive mode, the molecule has gained a proton, so subtract it to get the neutral mass
    # [M+H]+ : M = MZ - proton
    if mode == "Positive":
        return round(mz - masse_proton, 6)
    # In negative mode, the molecule has lost a proton, so add it to get the neutral mass
    # [M-H]- : M = MZ + proton
    elif mode == "Negative":
        return round(mz + masse_proton, 6)
    else:
        raise ValueError(f"ion_mode unknown : {ion_mode!r}. Accepted values : 'Positive' or 'Negative'.")