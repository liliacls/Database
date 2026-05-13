import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database_models.partial_model import Detection, Lipid, Annotation
from config import DB_PATH

engine = create_engine(DB_PATH, echo=False)
logger = logging.getLogger(__name__)

def database_loading_MS1(df, confidence_level):
    """Insère les lignes d'un DataFrame MS1 dans les tables Detection, Lipid et Annotation."""
    logger.info(f"Début de l'intégration — {len(df)} lignes à insérer.")
    with Session(engine) as session:
        try:
            for _, row in df.iterrows():
                detection = Detection(
                    Precursor_MZ     = row.get("Precursor_MZ"),
                    MS_level         = row.get("MS_level"),
                    Num_Peaks        = row.get("Num_Peaks"),
                    Exact_mass       = row.get("Exact_mass"),
                    Molecular_weight = row.get("Molecular_weight"),
                    RT               = row.get("RT") if "RT" in row else None,
                    CCS              = row.get("CCS") if "CCS" in row else None,
                )
                session.add(detection)
                session.flush()

                lipid = Lipid(
                    Lipid_name     = row.get("Lipid_Name"),
                    Lipid_class    = row.get("Lipid_class"),
                    Lipid_category = row.get("Lipid_category"),
                    Formula        = row.get("Formula"),
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
            logger.info(f"Intégration terminée — {len(df)} lignes insérées avec succès.")

        except Exception as e:
            logger.error(f"Erreur durant l'intégration : {e}")
            raise
