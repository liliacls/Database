import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys
sys.path.insert(0, '/home/liliacls/Documents/Stage/Database')
from database_model.partial_model import Lipid, Detection, Annotation

##############################################################################
# Script d'intégration de la base de données avec toutes les lignes du tableur
##############################################################################

# Chemins
DB_PATH = "sqlite:////home/liliacls/Documents/Stage/Database/lipids.db"
CSV_INPUT = '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv'
CSV_OUTPUT = '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/annotation_MS1.csv'

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

###########
# Export 
###########

with Session(engine) as session:
    # Extraction des données nécessaires pour réaliser l'annotation MS1 en utilisant les relations entre les tables
    rows = session.query(Annotation).all()

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