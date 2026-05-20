"""
reset_db.py
-----------
Supprime tous les enregistrements de BacLipidDB sans supprimer les tables.

L'ordre de suppression respecte les contraintes de clés étrangères :
    1. Annotation  (références vers Lipid et Detection)
    2. Fragment    (référence vers Detection)
    3. Detection
    4. Lipid

Usage :
    python scripts/reset_db.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.model import Annotation, Fragment, Detection, Lipid
from config import DB_PATH


def reset_db():
    engine = create_engine(DB_PATH, echo=False)

    with Session(engine) as session:
        session.query(Annotation).delete()
        session.query(Fragment).delete()
        session.query(Detection).delete()
        session.query(Lipid).delete()
        session.commit()


if __name__ == "__main__":
    confirm = input("Vider toute la base de données ? (oui/non) : ").strip().lower()
    if confirm == "oui":
        reset_db()
        print("Base de données vidée avec succès.")
    else:
        print("Opération annulée.")
