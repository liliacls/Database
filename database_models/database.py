"""
database.py
-----------
Script d'initialisation de la base de données "BacLipidDB.db"
Execution une seule fois pour créer les tables SQLite définies dans partial_model.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from partial_model import Base

DB_PATH = "sqlite:////home/liliacls/Documents/Stage/Database/BacLipidDB.db"

def main():
    """Crée la base de données et toutes les tables si elles n'existent pas encore"""
    engine = create_engine(DB_PATH, echo=True)
    try:
        with engine.connect():
            print("Connexion réussie")
        Base.metadata.create_all(engine)
        print("Tables créées avec succès !")
    
    except Exception as ex:
        print(f"Erreur : {ex}")


if __name__ == "__main__":
    main()