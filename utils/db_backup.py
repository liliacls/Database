import re
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_FILE, BACKUP_DIR, BACKUP_COUNT

def backup_database(label: str) -> Path:
    """
    Crée une sauvegarde horodaté de la base de données SQLite.
    Crée BACKUP_DIR s'il n'existe pas encore, nettoie le label
    (caractères non alphanumériques/"_" remplacés par "_") avant
    de l'utiliser dans le nom de fichier de la sauvegarde. Supprime aussi
    les enregistrements les plus anciens au-delà de BACKUP_COUNT afin que
    BACKUP_DIR ne grossisse pas indéfiniment. Si la création de la sauvegarde échoue,
    le fichier partiel est supprimé.

    :param label: identifiant ajouté au nom de fichier de la sauvegarde.
    :type label: str
    :raises sqlite3.Error: si la base de données source ne peut pas être lue ou
        si l'instantané ne peut pas être écrit.
    :return: chemin vers le fichier de sauvegarde créé.
    :rtype: Path
    """
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = re.sub(r"[^A-Za-z0-9_]+", "_", label).strip("_")
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
    """
    Supprime les sauvegardes BacLipidDB_*.db les plus anciens dans
    BACKUP_DIR au-delà de BACKUP_COUNT.
    """
    backups = sorted(
        BACKUP_DIR.glob("BacLipidDB_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old_backup in backups[BACKUP_COUNT:]:
        old_backup.unlink(missing_ok=True)
