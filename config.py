from pathlib import Path
import streamlit as st
from sqlalchemy import create_engine, event

# Définit le répertoire racine du projet
PROJECT_ROOT = Path(__file__).parent

# Chemin de la base de données
DB_FILE = PROJECT_ROOT / "BacLipidDB.db"
DB_PATH = f"sqlite:///{DB_FILE}"

# Chemin du fichier d'historique
HISTORY_PATH = PROJECT_ROOT / "history.json"

# Chemin du fichier des adduits personnalisés
ADDUCTS_PATH = PROJECT_ROOT / "adducts.json"

# Répertoire où sont stockés les sauvegardes de la base de données
BACKUP_DIR = PROJECT_ROOT / "backups"

# Nombre de sauvegardes à conserver dans le dossier /backups
BACKUP_COUNT = 20

@st.cache_resource
def get_engine():
    """
    Crée et met en cache le moteur SQLAlchemy pour la connexion à la base de données SQLite.

    Grâce à ``st.cache_resource``, le moteur n'est instancié qu'une seule fois par
    session Streamlit puis réutilisé, évitant de rouvrir une connexion à chaque rerun.
    La fonction `enable_foreign_key` est attaché à ``connect`` pour activer la pragma SQLite
    ``foreign_keys`` (désactivée par défaut) afin que les contraintes de clé étrangère
    soient bien appliquées sur chaque nouvelle connexion.

    :return: moteur SQLAlchemy connecté à la base de données du projet (voir :data:`DB_PATH`).
    :rtype: sqlalchemy.engine.Engine
    """
    engine = create_engine(DB_PATH, echo=False)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine