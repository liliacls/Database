import json
import math

from config import ADDUCTS_PATH

PROTON_MASS = 1.007276

BUILTIN_ADDUCT_SHIFTS = {
    "[M+H]+": PROTON_MASS,
    "[M-H]-": PROTON_MASS,
}

BUILTIN_ADDUCT_SIGNS = {
    "[M+H]+": -1,
    "[M-H]-": 1,
}

ADDUCT_SHIFTS: dict[str, float] = {}
ADDUCT_SIGNS: dict[str, int] = {}

def json_adducts() -> dict:
    """
    Load the custom adducts persisted in the JSON file at ADDUCTS_PATH.

    :return: mapping of adduct name to {"shift": float, "sign": int}, or an empty
        dict if the file does not exist or is empty.
    :rtype: dict

    Example::

        >>> json_adducts()
        {'[M+Na]+': {'shift': 22.989221, 'sign': -1}}
    """
    if not ADDUCTS_PATH.exists():
        return {}
    with open(ADDUCTS_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}

def _save_adducts(custom: dict) -> None:
    """
    Overwrite ADDUCTS_PATH with the given custom adducts.

    :param custom: mapping of adduct name to {"shift": float, "sign": int}.
    :type custom: dict
    """
    with open(ADDUCTS_PATH, "w", encoding="utf-8") as f:
        json.dump(custom, f, ensure_ascii=False, indent=2)

def _refresh() -> None:
    """Rebuild ADDUCT_SHIFTS and ADDUCT_SIGNS from the built-ins plus the persisted custom adducts."""
    custom = json_adducts()

    ADDUCT_SHIFTS.clear()
    ADDUCT_SHIFTS.update(BUILTIN_ADDUCT_SHIFTS)
    ADDUCT_SIGNS.clear()
    ADDUCT_SIGNS.update(BUILTIN_ADDUCT_SIGNS)

    for name, data in custom.items():
        ADDUCT_SHIFTS[name] = data["shift"]
        ADDUCT_SIGNS[name] = data["sign"]

_refresh()

def list_adducts() -> dict:
    """
    Return the currently persisted custom adducts.

    :return: mapping of adduct name to {"shift": float, "sign": int}.
    :rtype: dict

    Example::

        >>> list_adducts()
        {'[M+Na]+': {'shift': 22.989221, 'sign': -1}}
    """
    return json_adducts()

def add_adduct(name: str, shift: float, sign: int) -> None:
    """
    Validate and add a new custom adduct.

    :param name: adduct name. Comparison against existing adducts is
        case-insensitive, matching the lookup done by adduct().
    :type name: str
    :param shift: mass shift in Daltons, must be strictly positive.
    :type shift: float
    :param sign: -1 if the adduct is formed by addition to the neutral molecule
        (shift is subtracted to recover the neutral mass), +1 if formed by loss
        (shift is added back).
    :type sign: int
    :raises ValueError: if name is empty or already used (case-insensitively),
        sign is not -1/1, or shift is not a strictly positive number.

    Example::

        >>> # [M+Na]+ is formed by addition of sodium, so sign=-1 (the shift is
        >>> # subtracted back to recover the neutral mass from the precursor m/z).
        >>> add_adduct("[M+Na]+", shift=22.989221, sign=-1)
        >>> list_adducts()
        {'[M+Na]+': {'shift': 22.989221, 'sign': -1}}
    """
    name = str(name).strip()
    if not name:
        raise ValueError("Adduct name is required.")
    if name.upper() in (existing.upper() for existing in ADDUCT_SHIFTS):
        raise ValueError(f"Adduct '{name}' already exists.")
    if sign not in (-1, 1):
        raise ValueError("Sign must be -1 or +1.")

    shift = float(shift)
    if math.isnan(shift) or shift <= 0:
        raise ValueError("Mass shift must be strictly positive.")

    custom = json_adducts()
    custom[name] = {"shift": shift, "sign": sign}
    _save_adducts(custom)
    _refresh()

def remove_adduct(name: str) -> None:
    """
    Remove a previously added custom adduct. Built-in adducts cannot be removed.

    :param name: name of the custom adduct to remove.
    :type name: str
    :raises ValueError: if name is not a persisted custom adduct.

    Example::

        >>> remove_adduct("[M+Na]+")
        >>> list_adducts()
        {}
    """
    custom = json_adducts()
    if name not in custom:
        raise ValueError(f"'{name}' is not a custom adduct and cannot be removed.")

    del custom[name]
    _save_adducts(custom)
    _refresh()

def adduct(raw_adduct) -> str:
    """
    Validate and normalize a raw adduct value into one of the standard adduct strings. The adduct is required for the neutral mass calculation 
    and the completion of the "Adduct" column in the output table.

    :param raw_adduct: raw value to resolve
    :raises ValueError: if raw_adduct is missing or not a recognized adduct.
    :return: standard adduct string
    :rtype: str

    Example::

        >>> # Case and surrounding spaces are ignored, only the standard form is returned.
        >>> adduct("  [m+h]+ ")
        '[M+H]+'
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