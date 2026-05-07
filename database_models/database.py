import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from partial_model import Base

# Chemin vers la base de données SQLite
DB_PATH = "sqlite:////home/liliacls/Documents/Stage/Database/BacLipidDB.db"

# ============================================================
# Connexion à la base de données SQLite et création des tables
# ============================================================

def main():
    # Création de l'engine SQLAlchemy
    engine = create_engine(DB_PATH, echo=True)
    try:
        # Vérification de la connexion
        with engine.connect():
            print("Connexion réussie")

        # Création de toutes les tables définies dans partial_model.py
        Base.metadata.create_all(bind=engine)
        print("Tables créées avec succès !")

    except Exception as ex:
        print(f"Erreur : {ex}")

if __name__ == "__main__":
    main()