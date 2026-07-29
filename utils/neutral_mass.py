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

# ── Persistance des adduits personnalisés ────────────────────────────────────────────────────────────────────

def _json_adducts() -> dict:
    """
    Charge les adduits ajoutés depuis le fichier JSON situé via le chemin ADDUCTS_PATH.

    :return: correspondance entre le nom de l'adduit et {"shift": float, "sign": int}, ou un dictionnaire vide si le fichier n'existe pas ou est vide.
    :rtype: dict

    Exemple::

        >>> _json_adducts()
        {'[M+Na]+': {'shift': 22.989221, 'sign': -1}}
    """
    if not ADDUCTS_PATH.exists():
        return {}
    with open(ADDUCTS_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}

def _build() -> None:
    """
    Réinitialise ADDUCT_SHIFTS et ADDUCT_SIGNS avec les adduits natifs (BUILTIN_ADDUCT_SHIFTS et BUILTIN_ADDUCT_SIGNS), puis y ajoute les adduits personnalisés lus depuis le JSON via _json_adducts().
    """

    added = _json_adducts()

    ADDUCT_SHIFTS.clear()
    ADDUCT_SHIFTS.update(BUILTIN_ADDUCT_SHIFTS)
    ADDUCT_SIGNS.clear()
    ADDUCT_SIGNS.update(BUILTIN_ADDUCT_SIGNS)

    for name, data in added.items():
        ADDUCT_SHIFTS[name] = data["shift"]
        ADDUCT_SIGNS[name] = data["sign"]

def _save_adducts(added: dict) -> None:
    """
    Écrase le fichier JSON via ADDUCTS_PATH avec les adduits ajoutés donnés.

    :param added: correspondance entre le nom de l'adduit et {"shift": float, "sign": int}.
    :type added: dict
    """
    with open(ADDUCTS_PATH, "w", encoding="utf-8") as f:
        json.dump(added, f, ensure_ascii=False, indent=2)

_build()

# ── API de gestion des adduits ────────────────────────────────────────────────────────────────────

def list_adducts() -> dict:
    """
    Retourne les adduits personnalisés présent dans le JSON.

    :return: correspondance entre le nom de l'adduit et {"shift": float, "sign": int}.
    :rtype: dict

    Exemple::

        >>> list_adducts()
        {'[M+Na]+': {'shift': 22.989221, 'sign': -1}}
    """
    return _json_adducts()

def add_adduct(name: str, shift: float, sign: int) -> None:
    """
    Valide et ajoute un nouvel adduit aux adduits ajoutés.

    :param name: nom de l'adduit. La comparaison avec les adduits existants ne distingue pas majuscules et minuscules.
    :type name: str
    :param shift: décalage de masse en Daltons, doit être strictement positif.
    :type shift: float
    :param sign: -1 si l'adduit est formé par addition à la molécule neutre (le décalage est soustrait pour retrouver la masse neutre), +1 s'il est formé par perte (le décalage est réajouté).
    :type sign: int
    :raises ValueError: si name est vide ou déjà utilisé (indépendamment de la casse), si sign n'est pas -1/1, ou si shift n'est pas un nombre strictement positif.

    Exemple::

        >>> # [M+Na]+ est formé par addition de sodium, donc sign=-1 (le décalage est soustrait pour retrouver la masse neutre à partir du m/z du précurseur).
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

    custom = _json_adducts()
    custom[name] = {"shift": shift, "sign": sign}
    _save_adducts(custom)
    _build()

def remove_adduct(name: str) -> None:
    """
    Supprime un adduit personnalisé ajouté précédemment. Les adduits intégrés ne peuvent pas être supprimés.

    :param name: nom de l'adduit personnalisé à supprimer.
    :type name: str
    :raises ValueError: si name n'est pas un adduit personnalisé.

    Exemple::

        >>> remove_adduct("[M+Na]+")
        >>> list_adducts()
        {}
    """
    custom = _json_adducts()
    if name not in custom:
        raise ValueError(f"'{name}' is not a custom adduct and cannot be removed.")

    del custom[name]
    _save_adducts(custom)
    _build()

# ── Résolution et validation d'un adduit ────────────────────────────────────────────────────────────────────

def _adduct(raw_adduct) -> str:
    """
    Valide et normalise une valeur brute d'adduit en l'une des chaînes d'adduit standard connues
    (adduits intégrés ou personnalisés ajoutés via add_adduct()). La comparaison ignore la casse
    et les espaces environnants. L'adduit est nécessaire pour le calcul de la masse neutre
    et pour compléter la colonne "Adduct" du tableau de sortie.

    :param raw_adduct: valeur brute à résoudre.
    :type raw_adduct: str or float or None
    :raises ValueError: si raw_adduct est manquant ou ne correspond à aucun adduit reconnu.
    :return: chaîne d'adduit standard, dans sa casse de référence.
    :rtype: str

    Exemple::

        >>> # La casse et les espaces environnants sont ignorés, seule la forme standard est retournée.
        >>> _adduct("  [m+h]+ ")
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
    Valide et normalise une valeur de m/z du précurseur.

    :param Precursor_MZ: rapport m/z du précurseur à valider.
    :type Precursor_MZ: float
    :raises ValueError: si Precursor_MZ est une chaîne non convertible en float, est NaN, ou n'est pas strictement positif.
    :raises TypeError: si Precursor_MZ est d'un type non convertible en float.
    :return: la valeur de m/z validée, sous forme de float.
    :rtype: float
    """
    mz = float(Precursor_MZ)

    if math.isnan(mz):
        raise ValueError("Precursor_MZ cannot be NaN")

    if mz <= 0:
        raise ValueError(f"Precursor_MZ must be strictly positive : {mz}")

    return mz

# ── Calcul de la masse neutre ────────────────────────────────────────────────────────────────────

def _neutral_mass(Precursor_MZ: float, adduct_name: str) -> float:
    """
    Calcule la masse neutre à partir du rapport m/z du précurseur et de l'adduit du précurseur.

    :param Precursor_MZ: rapport m/z du précurseur.
    :type Precursor_MZ: float
    :param adduct_name: adduit du précurseur, déjà validé/normalisé via _adduct().
    :type adduct_name: str
    :raises ValueError: si adduct_name n'est pas un adduit reconnu, ou si Precursor_MZ est NaN ou n'est pas strictement positif (voir _mz()).
    :raises TypeError: si Precursor_MZ est d'un type non convertible en float (voir _mz()).
    :return: masse neutre en Daltons, arrondie à 6 décimales.
    :rtype: float
    """
    mz = _mz(Precursor_MZ)

    if not isinstance(adduct_name, str) or adduct_name not in ADDUCT_SHIFTS:
        raise ValueError(
            f"adduct unknown : {adduct_name!r}. Accepted values : {list(ADDUCT_SHIFTS)}."
        )

    shift = ADDUCT_SHIFTS[adduct_name]
    sign = ADDUCT_SIGNS[adduct_name]

    return round(mz + sign * shift, 6)

def resolve_adducts(records) -> tuple[list, list, list[str]]:
    """
    Résout l'adduit et la masse neutre pour un lot d'enregistrements (label, lipid_name, precursor_mz, raw_adduct).

    :param records: itérable de tuples (label, lipid_name, precursor_mz, raw_adduct)
    :type records: iterable[tuple]
    :return: listes (adducts, masses, error_messages)
    :rtype: tuple[list, list, list[str]]
    """
    adducts, masses, errors = [], [], []
    for label, lipid_name, precursor_mz, raw_adduct in records:
        try:
            resolved_adduct = _adduct(raw_adduct)
            mass = _neutral_mass(precursor_mz, resolved_adduct)
        except ValueError as e:
            errors.append(f"{label} ({lipid_name}) : {e}")
            resolved_adduct, mass = None, None
        adducts.append(resolved_adduct)
        masses.append(mass)
    return adducts, masses, errors
