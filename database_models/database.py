from sqlalchemy import create_engine
from partial_model import Base
# ============================================================
# Connexion à la base de données SQLite et création des tables
# ============================================================

# Chemin vers la base de données SQLite
db_path = "sqlite:////home/liliacls/Documents/Stage/Database/BacLipidDB.db"

# Création de l'engine SQLAlchemy
engine = create_engine(db_path, echo=True)

try:
    # Connexion à la base de données
    conn = engine.connect()
    print("Connexion réussie")

    # Création de toutes les tables définies dans partial_model.py
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

except Exception as ex:
    # Affichage de l'erreur en cas de problème
    print(f"Erreur : {ex}")