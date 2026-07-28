import json
from config import HISTORY_PATH

def load_history() -> list[dict]:
    """
    Charge l'historique des imports via HISTORY_PATH et retourne son contenu sous forme d'une liste de dictionnaires.

    :return: liste des enregistrements d'import, ou une liste vide si le fichier n'existe pas ou est vide.
    :rtype: list[dict]
    """
    if not HISTORY_PATH.exists():
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []

def save_history(history: list[dict]) -> None:
    """
    Écrase le fichier d'historique des imports avec la liste donnée.
    Utilisée en interne par append_history() et remove_history() pour persister leurs modifications ;
    ne fait qu'écrire, sans logique d'ajout ou de suppression.

    :param history: liste complète des enregistrements d'import à écrire.
    :type history: list[dict]
    """
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def append_history(entry: dict) -> None:
    """
    Charge l'historique existant, ajoute une seule entrée à la liste en mémoire, puis réécrit tout le fichier d'historique des imports.

    :param entry: entrée d'historique à ajouter.
    :type entry: dict
    :raises TypeError: si entry n'est pas un dict.
    """
    if not isinstance(entry, dict):
        raise TypeError(f"entry doit être un dict, reçu {type(entry).__name__}")
    history = load_history()
    history.append(entry)
    save_history(history)

def remove_history(index: int) -> None:
    """
    Supprime une seule entrée de l'historique des imports par index de liste.

    :param index: index de l'entrée à supprimer, tel que retourné par load_history().
    :type index: int
    :raises IndexError: si index est hors limites de l'historique chargé.
    """
    history = load_history()
    if not (0 <= index < len(history)):
        raise IndexError(f"index {index} hors limites (historique de taille {len(history)})")
    history.pop(index)
    save_history(history)