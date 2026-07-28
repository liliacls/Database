import sys
from models.model import Base
from config import get_engine

def main() -> None:
    """
    Initialise la base de données BacLipidDB en créant toutes les tables
    définies dans models/model.py si elles n'existent pas encore.

    Teste d'abord la connexion au moteur SQLAlchemy, puis crée les tables.
    En cas d'échec, affiche l'erreur et quitte le script avec le code 1.

    Usage :
    python scripts/init_db.py

    :return: aucune valeur de retour.
    :rtype: None
    """
    engine = get_engine()
    try:
        with engine.connect():
            print("Connection successful")
        Base.metadata.create_all(engine)
        print("Tables created successfully!")

    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    main()
