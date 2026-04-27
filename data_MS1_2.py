import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from partial_model import Lipid, Detection, Annotation

# Second test avec un 10 lipides tirés au hasard dans le tableur

db_path = "sqlite:///lipids.db"
engine = create_engine(db_path, echo=True)

df = pd.read_csv('/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv')
lignes = df.sample(10)
print(lignes)

with Session(engine) as session:
    try:
        for _, ligne in lignes.iterrows():
            
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
        print("10 lignes insérées avec succès !")

    # En cas d'erreur, rollback de la transaction
    except Exception as e:
        session.rollback()
        print(f"Erreur : {e}")

with Session(engine) as session:
    # Extraction des données nécessaires pour réaliser l'annotation MS1 en utilisant les relations entre les tables
    annotations = session.query(Annotation).all()
    
    resultats = []
    for annotation in annotations:
        resultats.append({
            'formula': annotation.lipid.Formula,
            'mz': annotation.detection.Precursor_MZ,
            'name': annotation.lipid.Lipid_name
        })
    
    df_export = pd.DataFrame(resultats)
    print(df_export)
    
    # Exportation des données de la base vers un fichier CSV
    df_export.to_csv(
    '/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/annotation_MS1_V2.csv',
    index=False,
    encoding='utf-8',
    lineterminator='\r\n'  
    )

    print("Fichier créé !")