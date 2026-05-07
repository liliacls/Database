import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys
sys.path.insert(0, '/home/liliacls/Documents/Stage/Database')
from database_models.partial_model import Lipid, Detection, Annotation

##############################################################################
# Script d'intégration de la base de données avec toutes les lignes du tableur
##############################################################################

# Chemins
DB_PATH = "sqlite:////home/liliacls/Documents/Stage/Database/BacLipidDB"
CSV_INPUT = '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv'

# Création de l'engine SQLAlchemy
engine = create_engine(DB_PATH, echo=True)

# Lecture du csv d'entrée
df = pd.read_csv(CSV_INPUT)
if df.empty:
    raise ValueError(f"Le fichier CSV est vide : {CSV_INPUT}")

###############################################
# Insertion des données dans la base de données
###############################################

with Session(engine) as session:
    try:
        for i, ligne in df.iterrows():
            
            # Insertion dans la table Lipid
            lipid = Lipid(
                Lipid_name=ligne['Name'],
                Formula=ligne['Formula']
            )
            session.add(lipid)
            session.flush()
        
            # Insertion dans la table Detection
            detection = Detection(
                Precursor_MZ=ligne['Precursor_MZ'],
                Exact_mass=ligne['masse_experimentale']
            )   
            session.add(detection)
            session.flush()

            # Insertion dans la table Annotation
            annotation = Annotation(
                Lipid_id=lipid.Lipids_ID,
                Detection_id=detection.Detection_ID
            )
            session.add(annotation)
        session.commit()

    # En cas d'erreur, rollback de la transaction et affichage de l'erreur
    except Exception as e:
        session.rollback()
        print(f"Erreur à la ligne {i} ({ligne.get('Name', '?')}) : {e}")
        raise