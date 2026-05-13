import pandas as pd
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import create_engine
from models.model import Annotation
from config import DB_PATH

CSV_OUTPUT = '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/annotation_MS1.csv'

# Création de l'engine SQLAlchemy
engine = create_engine(DB_PATH, echo=True)

###########
# Export 
###########

with Session(engine) as session:
    # Extraction des données nécessaires pour réaliser l'annotation MS1 en utilisant les relations entre les tables
    rows = session.query(Annotation).options(
        joinedload(Annotation.lipid),
        joinedload(Annotation.detection),
    ).all()

    resultats = []
    for annotation in rows:
        resultats.append({
            'formula': annotation.lipid.Formula,
            'mz': annotation.detection.Precursor_MZ,
            'name': annotation.lipid.Lipid_name
        })
    
    # Conversion de la liste de dictionnaires en DataFrame pour faciliter l'exportation
    df_export = pd.DataFrame(resultats)

    # Exportation des données de la base vers un fichier CSV, lineterminator='\r\n' sinon fichier pas accepté par MZmine
    df_export.to_csv(CSV_OUTPUT, index=False, encoding='utf-8',lineterminator='\r\n')

    print("Fichier créé !")