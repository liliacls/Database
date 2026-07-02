"""
reset_db.py
-----------
Delete all records from BacLipidDB without dropping the tables.

The deletion order respects foreign key constraints:
    1. Annotation  (references to Lipid and Detection)
    2. Fragment    (reference to Detection)
    3. Detection
    4. Lipid

Usage :
    python scripts/reset_db.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.model import Annotation, Fragment, Detection, Lipid
from config import DB_PATH
from config import HISTORY_PATH
import os


def reset_db():

    engine = create_engine(DB_PATH, echo=False)

    with Session(engine) as session:
        session.query(Annotation).delete()
        session.query(Fragment).delete()
        session.query(Detection).delete()
        session.query(Lipid).delete()
        session.commit()


if __name__ == "__main__":
    confirm = input("Clear all records from the database ? (yes/no) : ").strip().lower()
    if confirm == "yes":
        reset_db()
        if os.path.exists(HISTORY_PATH):
            os.remove(HISTORY_PATH)
        print("Database cleared successfully.")
    else:
        print("Operation cancelled.")
