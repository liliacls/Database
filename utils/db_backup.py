import re
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_FILE, BACKUP_DIR

def backup_database(label: str) -> Path:
    """Create a timestamped snapshot of the SQLite database.

    :param label: identifier appended to the snapshot filename.
    :type label: str
    :return: path to the created backup file.
    :rtype: Path
    """
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = re.sub(r"[^A-Za-z0-9_-]+", "_", label).strip("_")
    suffix = f"_{label}" if label else ""
    backup_path = BACKUP_DIR / f"BacLipidDB_{timestamp}{suffix}.db"

    source = sqlite3.connect(DB_FILE)
    try:
        dest = sqlite3.connect(backup_path)
        try:
            source.backup(dest)
        finally:
            dest.close()
    finally:
        source.close()

    return backup_path
