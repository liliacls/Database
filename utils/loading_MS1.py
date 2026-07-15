import logging
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from models.model import Detection, Lipid, Annotation
from config import get_engine
from utils.db_backup import backup_database
from utils.history import append_history

logger = logging.getLogger(__name__)

def DB_MS1(
    df: pd.DataFrame,
    filename: str,
    integrator: str,
    file_row_name: str,
) -> None:
    """
    Insert MS1 annotation data into the database.
    For each row of the DataFrame, creates and inserts a record into the three tables: Detection, Lipid and Annotation.

    :param df: DataFrame containing the columns Lipid_Name, Formula, Precursor_MZ, Neutral_mass, Adduct, Molecular_weight, MS_level, Num_Peaks, Lipid_category, Lipid_class, Lipid_subclass
               and optionally RT and CCS.
    :type df: pandas.DataFrame
    :param filename: name of the file being integrated.
    :type filename: str
    :param integrator: name of the person performing the integration.
    :type integrator: str
    :param file_row_name: name of the file that provided the annotations.
    :type file_row_name: str
    :raises Exception: on error no row is committed (automatic ROLLBACK) and the error is logged.
    """
    logger.info(f"Starting integration - {len(df)} rows to insert.")
    detections = []
    with Session(get_engine()) as session:
        try:
            for _, row in df.iterrows():
                detection = Detection(
                    Precursor_MZ=row.get("Precursor_MZ"),
                    MS_level=row.get("MS_level"),
                    Ionisation_mode=row.get("Ionisation_mode"),
                    Adduct=row.get("Adduct"),
                    Num_Peaks=row.get("Num_Peaks"),
                    Neutral_mass=row.get("Neutral_mass"),
                    RT=row.get("RT") if pd.notna(row.get("RT")) else None,
                    CCS=row.get("CCS") if pd.notna(row.get("CCS")) else None,
                )

                lipid = Lipid(
                    Lipid_name=row.get("Lipid_Name"),
                    Lipid_category=(
                        row.get("Lipid_category")
                        if pd.notna(row.get("Lipid_category"))
                        else None
                    ),
                    Lipid_class=(
                        row.get("Lipid_class")
                        if pd.notna(row.get("Lipid_class"))
                        else None
                    ),
                    Lipid_subclass=(
                        row.get("Lipid_subclass")
                        if pd.notna(row.get("Lipid_subclass"))
                        else None
                    ),
                    Formula=row.get("Formula"),
                    Molecular_weight=row.get("Molecular_weight"),
                    Monoisotopic_mass=row.get("Monoisotopic_mass"),
                )

                annotation = Annotation(lipid=lipid, detection=detection)

                session.add(detection)
                session.add(lipid)
                session.add(annotation)
                detections.append(detection)

            session.flush()
            detection_ids = [detection.Detection_ID for detection in detections]

            session.commit()
            logger.info(f"Integration completed: {len(df)} rows inserted successfully.")

        except Exception as e:
            logger.error(f"Error during integration: {e}")
            raise

    backup_path = backup_database(label=filename)

    first_row = df.iloc[0]
    append_history(
        {
            "filename": filename,
            "row_file": file_row_name,
            "inserted": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ms_level": first_row.get("MS_level"),
            "ionisation_mode": first_row.get("Ionisation_mode"),
            "num_rows": len(df),
            "detection_ids": detection_ids,
            "integrator": integrator,
            "backup": backup_path.name,
        }
    )
