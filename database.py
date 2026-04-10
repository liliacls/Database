from sqlalchemy import create_engine
from models import Base, Organism, Experiment, Method, File, Adduct, Detection, Fragment, Lipid, Annotation

# ============================================================
# Connexion à la base de données SQLite et création des tables
# ============================================================

# Chemin vers la base de données SQLite
db_path = "sqlite:///lipids.db"


engine = create_engine(db_path, echo=False)

try:
    # Connexion à la base de données
    conn = engine.connect()
    print("Connexion réussie")

    # Création de toutes les tables définies dans models.py
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

except Exception as ex:
    # Affichage de l'erreur en cas de problème
    print(f"Erreur : {ex}")