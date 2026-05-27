import logging
import pandas as pd
from sqlalchemy.orm import Session
from models.model import Detection, Lipid, Annotation
from config import get_engine

logger = logging.getLogger(__name__)
def database_loading_MS1(df, confidence_level):
    """
    Insère les données d'annotation MS1 dans la base de données.
    Pour chaque ligne du DataFrame, crée et insère un enregistrement dans les trois tables : Detection, Lipid et Annotation

    :param df: DataFrame contenant les colonnes Lipid_Name, Formula, Precursor_MZ, Neutral_mass, Molecular_weight, MS_level, Num_Peaks, Lipid_category, Lipid_class, Lipid_subclass
               et optionnellement RT et CCS.
    :type df: pandas.DataFrame
    :param confidence_level: niveau de confiance de l'annotation (1 à 4)
    :type confidence_level: int
    :raises Exception: en cas d'erreur aucune ligne n'est commitée (ROLLBACK automatique) et l'erreur est loggée.
    """
    logger.info(f"Début de l'intégration - {len(df)} lignes à insérer.")
    with Session(get_engine()) as session:
        try:
            for _, row in df.iterrows():
                detection = Detection(
                    Precursor_MZ     = row.get("Precursor_MZ"),
                    MS_level         = row.get("MS_level"),
                    Num_Peaks        = row.get("Num_Peaks"),
                    Neutral_mass     = row.get("Neutral_mass"),
                    RT               = row.get("RT") if pd.notna(row.get("RT")) else None,
                    CCS              = row.get("CCS") if pd.notna(row.get("CCS")) else None,
                )
                session.add(detection)
                session.flush()

                lipid = Lipid(
                    Lipid_name       = row.get("Lipid_Name"),
                    Lipid_category   = row.get("Lipid_category") if pd.notna(row.get("Lipid_category")) else None,
                    Lipid_class      = row.get("Lipid_class") if pd.notna(row.get("Lipid_class")) else None,
                    Lipid_subclass   = row.get("Lipid_subclass") if pd.notna(row.get("Lipid_subclass")) else None,
                    Formula          = row.get("Formula"),
                    Molecular_weight = row.get("Molecular_weight"),
                )
                session.add(lipid)
                session.flush()

                annotation = Annotation(
                    Lipid_id         = lipid.Lipid_ID,
                    Detection_id     = detection.Detection_ID,
                    Confidence_level = confidence_level,
                )
                session.add(annotation)

            session.commit()
            logger.info(f"Intégration terminée - {len(df)} lignes insérées avec succès.")

        except Exception as e:
            logger.error(f"Erreur durant l'intégration : {e}")
            raise
