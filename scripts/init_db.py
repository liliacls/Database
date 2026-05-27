"""
init_db.py
-----------
Script d'initialisation de la base de données "BacLipidDB.db"
Execution une seule fois pour créer les tables SQLite définies dans models/model.py
"""

from sqlalchemy import create_engine
from models.model import Base
from config import DB_PATH

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