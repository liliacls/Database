import json
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from models.model import Detection, Lipid, Annotation
from config import get_engine, HISTORY_PATH

logger = logging.getLogger(__name__)


def _history(entry: dict):
    history = []
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(entry)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def database_loading_MS1(df, confidence_level, filename):
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
    detection_ids = []
    with Session(get_engine()) as session:
        try:
            for _, row in df.iterrows():
                detection = Detection(
                    Precursor_MZ     = row.get("Precursor_MZ"),
                    MS_level         = row.get("MS_level"),
                    Ionisation_mode  = row.get("Ionisation_mode"),
                    Num_Peaks        = row.get("Num_Peaks"),
                    Neutral_mass     = row.get("Neutral_mass"),
                    RT               = row.get("RT") if pd.notna(row.get("RT")) else None,
                    CCS              = row.get("CCS") if pd.notna(row.get("CCS")) else None,
                )
                session.add(detection)
                session.flush()
                detection_ids.append(detection.Detection_ID)

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
            logger.info(f"Intégration terminée : {len(df)} lignes insérées avec succès.")

        except Exception as e:
            logger.error(f"Erreur durant l'intégration : {e}")
            raise

    first_row = df.iloc[0]
    _history({
        "filename":         filename,
        "inserted":         datetime.now(),
        "ms_level":         first_row.get("MS_level"),
        "ionisation_mode":  first_row.get("Ionisation_mode"),
        "num_rows":         len(df),
        "detection_ids":    detection_ids,
    })
