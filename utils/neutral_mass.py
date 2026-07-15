import math

PROTON_MASS = 1.007276
AMMONIUM_MASS = 18.033823

ADDUCT_SHIFTS = {
    "[M+H]+": PROTON_MASS,
    "[M+NH4]+": AMMONIUM_MASS,
    "[M-H]-": PROTON_MASS,
}

ADDUCT_SIGNS = {
    "[M+H]+": -1,
    "[M+NH4]+": -1,
    "[M-H]-": 1,
}

def adduct(raw_adduct) -> str:
    """
    Validate and normalize a raw adduct value into one of the standard adduct strings. The adduct is required for the neutral mass calculation 
    and the completion of the "Adduct" column in the output table.

    :param raw_adduct: raw value to resolve
    :raises ValueError: if raw_adduct is missing or not a recognized adduct.
    :return: standard adduct string
    :rtype: str
    """
    if (
        raw_adduct is None
        or (isinstance(raw_adduct, float) and math.isnan(raw_adduct))
        or str(raw_adduct).strip() == ""
    ):
        raise ValueError(f"Adduct is required. Accepted values : {', '.join(ADDUCT_SHIFTS)}.")

    value = str(raw_adduct).strip()
    normalized = {a.upper(): a for a in ADDUCT_SHIFTS}.get(value.upper())
    if normalized is None:
        raise ValueError(
            f"Unsupported adduct '{raw_adduct}'. Accepted values : {', '.join(ADDUCT_SHIFTS)}."
        )
    return normalized

def _mz(Precursor_MZ: float) -> float:
    """
    Validate and normalize a precursor m/z value.

    :param Precursor_MZ: m/z ratio of the precursor to validate.
    :type Precursor_MZ: float
    :raises ValueError: if Precursor_MZ cannot be converted to float, is NaN, or is not
        strictly positive.
    :return: the validated m/z value, as a float.
    :rtype: float
    """
    mz = float(Precursor_MZ)

    if math.isnan(mz):
        raise ValueError("Precursor_MZ cannot be NaN")

    if mz <= 0:
        raise ValueError(f"Precursor_MZ must be strictly positive : {mz}")

    return mz

def _validate_adduct(adduct: str) -> str:
    """
    Validate that an adduct string is one of the known standard adducts.

    :param adduct: adduct string to validate
    :type adduct: str
    :raises ValueError: if adduct is not a string or is not a recognized adduct.
    :return: the validated adduct string, unchanged.
    :rtype: str
    """
    if not isinstance(adduct, str) or adduct not in ADDUCT_SHIFTS:
        raise ValueError(
            f"adduct unknown : {adduct!r}. Accepted values : {list(ADDUCT_SHIFTS)}."
        )

    return adduct

def neutral_mass(Precursor_MZ: float, adduct: str) -> float:
    """
    Calculate the neutral mass from the precursor m/z ratio and the precursor adduct.

    :param Precursor_MZ: m/z ratio of the precursor.
    :type Precursor_MZ: float
    :param adduct: precursor adduct
    :type adduct: str
    :return: neutral mass in Daltons, rounded to 6 decimal places.
    :rtype: float
    """
    mz = _mz(Precursor_MZ)
    adduct = _validate_adduct(adduct)

    shift = ADDUCT_SHIFTS[adduct]
    sign = ADDUCT_SIGNS[adduct]

    return round(mz + sign * shift, 6)