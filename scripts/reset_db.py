import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy.orm import Session
from models.model import Annotation, Fragment, Detection, Lipid
from config import get_engine
from config import HISTORY_PATH

def _reset_db():
    """
    Supprime tous les enregistrements de BacLipidDB sans supprimer les tables.

    L'ordre de suppression respecte les contraintes de clés étrangères :
    1. Annotation  (références vers Lipid et Detection)
    2. Fragment    (référence vers Detection)
    3. Detection
    4. Lipid

    Usage :
        python scripts/reset_db.py

    :raises Exception: en cas d'échec de la suppression, aucune ligne n'est validée (ROLLBACK automatique à la fermeture de la session).
    """

    engine = get_engine()

    with Session(engine) as session:
        session.query(Annotation).delete()
        session.query(Fragment).delete()
        session.query(Detection).delete()
        session.query(Lipid).delete()
        session.commit()

if __name__ == "__main__":
    confirm = input("Clear all records from the database ? (yes/no) : ").strip().lower()
    if confirm == "yes":
        try:
            _reset_db()
        except Exception as ex:
            print(f"Error: {ex}")
            sys.exit(1)

        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
        except Exception as ex:
            print(f"Database cleared, but failed to reset history file: {ex}")
            sys.exit(1)

        print("Database cleared successfully.")
    else:
        print("Operation cancelled.")