import json
from config import HISTORY_PATH

def load_history() -> list[dict]:
    """Load the import history.

    :return: list of import records, or an empty list if the file does not exist or is empty.
    :rtype: list[dict]
    """
    if not HISTORY_PATH.exists():
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []

def save_history(history: list[dict]) -> None:
    """Overwrite the import history file with the given list of entries.

    :param history: full list of import records to write.
    :type history: list[dict]
    """
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def append_history(entry: dict) -> None:
    """Append a single entry to the import history file.

    :param entry: history entry to append.
    :type entry: dict
    """
    history = load_history()
    history.append(entry)
    save_history(history)

def remove_history(index: int) -> None:
    """Remove a single entry from the import history by index.

    :param index: index of the entry to remove, as returned by load_history().
    :type index: int
    """
    history = load_history()
    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)