import re
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_FILE, BACKUP_DIR, BACKUP_COUNT

def backup_database(label: str) -> Path:
    """
    Create a timestamped snapshot of the SQLite database.
    Creates BACKUP_DIR if it does not exist yet, clean label
    (non alphanumeric/"_"/"-" characters replaced with "_") before
    using it in the snapshot filename. Also deletes the oldest
    snapshots beyond BACKUP_COUNT so BACKUP_DIR does not grow without
    bound. If the snapshot itself fails, the partial file is removed.

    :param label: identifier appended to the snapshot filename.
    :type label: str
    :return: path to the created backup file.
    :rtype: Path
    :raises sqlite3.Error: if the source database cannot be read or
        the snapshot cannot be written.
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
    except Exception:
        backup_path.unlink(missing_ok=True)
        raise
    finally:
        source.close()

    _delete_backups()

    return backup_path

def _delete_backups() -> None:
    """Delete the oldest BacLipidDB_*.db snapshots in BACKUP_DIR beyond BACKUP_COUNT."""
    backups = sorted(
        BACKUP_DIR.glob("BacLipidDB_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old_backup in backups[BACKUP_COUNT:]:
        old_backup.unlink(missing_ok=True)
