import json
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from models.model import Detection, Lipid, Annotation
from config import get_engine, HISTORY_PATH
logger = logging.getLogger(__name__)


def _history(entry: dict) -> None:
    """
    Append an entry to the integration history file (creates it if missing).

    :param entry: history entry to append.
    :type entry: dict
    """
    history = []
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(entry)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def database_loading_MS1(df: pd.DataFrame, confidence_level: int, filename: str, integrator: str = None) -> None:
    """
    Insert MS1 annotation data into the database.
    For each row of the DataFrame, creates and inserts a record into the three tables: Detection, Lipid and Annotation.

    :param df: DataFrame containing the columns Lipid_Name, Formula, Precursor_MZ, Neutral_mass, Molecular_weight, MS_level, Num_Peaks, Lipid_category, Lipid_class, Lipid_subclass
               and optionally RT and CCS.
    :type df: pandas.DataFrame
    :param confidence_level: confidence level of the annotation (1 to 4).
    :type confidence_level: int
    :param filename: name of the file being integrated, recorded in the history.
    :type filename: str
    :param integrator: name of the person performing the integration.
    :type integrator: str
    :raises Exception: on error no row is committed (automatic ROLLBACK) and the error is logged.
    """
    logger.info(f"Starting integration - {len(df)} rows to insert.")
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
                    Lipid_name        = row.get("Lipid_Name"),
                    Lipid_category    = row.get("Lipid_category") if pd.notna(row.get("Lipid_category")) else None,
                    Lipid_class       = row.get("Lipid_class") if pd.notna(row.get("Lipid_class")) else None,
                    Lipid_subclass    = row.get("Lipid_subclass") if pd.notna(row.get("Lipid_subclass")) else None,
                    Formula           = row.get("Formula"),
                    Molecular_weight  = row.get("Molecular_weight"),
                    Monoisotopic_mass = row.get("Monoisotopic_mass"),
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
            logger.info(f"Integration completed: {len(df)} rows inserted successfully.")

        except Exception as e:
            logger.error(f"Error during integration: {e}")
            raise

    first_row = df.iloc[0]
    _history({
        "filename":         filename,
        "inserted":         datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ms_level":         first_row.get("MS_level"),
        "ionisation_mode":  first_row.get("Ionisation_mode"),
        "num_rows":         len(df),
        "detection_ids":    detection_ids,
        "integrator":       integrator,
    })
