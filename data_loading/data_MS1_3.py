import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database_models.partial_model import Lipid, Detection, Annotation
from config import DB_PATH

##############################################################################
# Script d'intégration de la base de données avec toutes les lignes du tableur
##############################################################################

CSV_INPUT = Path('/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv')

engine = create_engine(DB_PATH, echo=False)

def load_all(csv_input: Path) -> None:
    df = pd.read_csv(csv_input)
    if df.empty:
        raise ValueError(f"Le fichier CSV est vide : {csv_input}")

    with Session(engine) as session:
        try:
            for i, ligne in df.iterrows():

                lipid = Lipid(
                    Lipid_name=ligne['Name'],
                    Formula=ligne['Formula']
                )
                session.add(lipid)
                session.flush()

                detection = Detection(
                    Precursor_MZ=ligne['Precursor_MZ'],
                    Exact_mass=ligne['masse_experimentale']
                )
                session.add(detection)
                session.flush()

                annotation = Annotation(
                    Lipid_id=lipid.Lipid_ID,
                    Detection_id=detection.Detection_ID
                )
                session.add(annotation)

            session.commit()
            print(f"Intégration terminée — {len(df)} lignes insérées.")

        except Exception as e:
            session.rollback()
            print(f"Erreur à la ligne {i} ({ligne.get('Name', '?')}) : {e}")
            raise

if __name__ == "__main__":
    load_all(CSV_INPUT)