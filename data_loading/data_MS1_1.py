import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys
sys.path.insert(0, '/home/liliacls/Documents/Stage/Database')
from database_models.partial_model import Lipid, Detection, Annotation

##################################################################################
# Premier test d'intégration de la base de données avec une seule ligne du tableur
##################################################################################

# Chemins
DB_PATH = "sqlite:///BacLipidDB.db"
CSV_INPUT = '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv'
CSV_OUTPUT = '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/annotation_MS1.csv'

# Création de l'engine SQLAlchemy
engine = create_engine(DB_PATH, echo=True)

# Lecture du fichier CSV et sélection de la ligne correspondant à 'PE 34:1'
df = pd.read_csv(CSV_INPUT)
ligne = df[df['Name'] == 'PE 34:1'].iloc[0]

###############################################
# Insertion des données dans la base de données
################################################

with Session(engine) as session:
    try:
        # Insertion dans la table Lipid
        lipid = Lipid(
            Lipid_name=ligne['Name'],
            Formula=ligne['Formula']
        )
        session.add(lipid)
        session.flush()
        print(f"Lipid_ID généré : {lipid.Lipids_ID}")

        # Insertion dans la table Detection
        detection = Detection(
            Precursor_MZ=ligne['Precursor_MZ'],
            Exact_mass=ligne['masse_experimentale']
        )
        session.add(detection)
        session.flush()
        print(f"Detection_ID généré : {detection.Detection_ID}")

        # Insertion dans la table Annotation
        annotation = Annotation(
            Lipid_id=lipid.Lipids_ID,
            Detection_id=detection.Detection_ID
        )
        session.add(annotation)
        session.commit()
        print("Insertion réussie !")

    # En cas d'erreur, rollback de la transaction
    except Exception as e:
        session.rollback()
        print(f"Erreur : {e}")
        raise

###########
# Export 
###########

with Session(engine) as session:

    # Extraction des données nécessaires pour réaliser l'annotation MS1 en utilisant les relations entre les tables
    annotations = session.query(Annotation).all()
    
    # Création d'une liste de dictionnaires pour stocker les résultats de l'annotation
    resultats = []

    for annotation in annotations:
        resultats.append({
            'formula'   : annotation.lipid.Formula,
            'mz'        : annotation.detection.Precursor_MZ,
            'name'      : annotation.lipid.Lipid_name
        })
    
    # Conversion de la liste de dictionnaires en DataFrame pour faciliter l'exportation
    df_export = pd.DataFrame(resultats)
    print(df_export)
    
    # Exportation des données de la base vers un fichier CSV
    df_export.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding='utf-8',
        lineterminator='\r\n'  
    )

    print("Fichier créé !")