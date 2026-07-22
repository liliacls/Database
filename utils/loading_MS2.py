import csv
import io
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from models.model import Detection, Fragment, Lipid, Annotation
from config import get_engine
from utils.db_backup import backup_database
from utils.history import append_history
from utils.exceptions import PostIntegrationError

logger = logging.getLogger(__name__)

SCAN_PREFIX = "Scan #"
FRAGMENT_HEADER = ("m/z", "Intensity")

# Field labels expected in each scan block (as the first cell of a "Label;Value" row).
REQUIRED_SCAN_FIELDS = [
    "Lipid_Name",
    "Precursor_MZ",
    "Formula",
    "Adduct",
    "Lipid_category",
    "Lipid_class",
    "Lipid_subclass",
    "Num_peaks",
]
OPTIONAL_SCAN_FIELDS = ["FA_composition", "RT", "CCS"]

def _empty(row: list[str]) -> bool:
    """Returns True if the row is empty or contains only empty cells."""
    return not row or not row[0].strip()

def ms2_parsing(source, delimiter: str | None = None) -> list[dict]:
    """
    Parse an MS2 file (.csv/.tsv) organized into stacked blocks and returns a list
    of entries as dictionaries.

    :param source: path to the .csv or .tsv file
    :type source: Path or str or file-like object
    :param delimiter: column separator. If None, inferred from the file's
        extension/name ("\\t" for .tsv, "," otherwise).
    :type delimiter: str or None
    :return: list of dictionaries with the keys "scan_id", "precursor_mz", "formula",
        "lipid_name", "fa_composition", "adduct", "lipid_category", "lipid_class",
        "lipid_subclass", "rt", "ccs", "num_peaks" and "fragments" (list of (mz, intensity) tuples).
    :rtype: list[dict]
    :raises ValueError: if a scan block is malformed (missing required field, non-numeric
        RT/CCS, missing fragment header, no fragments found, or fragment count
        inconsistent with Num_peaks) or if no scan is found in the file.
    """

    if isinstance(source, (str, Path)):
        path = Path(source)
        if delimiter is None:
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        with open(path, "r", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f, delimiter=delimiter))
    else:
        name = getattr(source, "name", "")
        if delimiter is None:
            delimiter = "\t" if str(name).lower().endswith(".tsv") else ","
        raw = source.getvalue() if hasattr(source, "getvalue") else source.read()
        text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))

    scans = []
    i = 0
    n = len(rows)

    while i < n:
        row = rows[i]
        first_cell = row[0].strip() if row else ""

        if not first_cell.startswith(SCAN_PREFIX):
            i += 1
            continue

        scan_id = first_cell[len(SCAN_PREFIX):].strip()
        i += 1

        fields = {}
        while i < n and tuple(c.strip() for c in rows[i][:2]) != FRAGMENT_HEADER:
            if _empty(rows[i]):
                raise ValueError(
                    f"'m/z' / 'Intensity' header not found before an empty row in block '{first_cell}'."
                )
            label = rows[i][0].strip()
            value = rows[i][1].strip() if len(rows[i]) > 1 else ""
            fields[label] = value
            i += 1

        if i >= n:
            raise ValueError(f"'m/z' / 'Intensity' header expected for scan '{first_cell}'.")
        i += 1

        missing = [f for f in REQUIRED_SCAN_FIELDS if not fields.get(f)]
        if missing:
            raise ValueError(
                f"Missing field(s) for scan '{first_cell}': {', '.join(missing)}."
            )

        try:
            precursor_mz = float(fields["Precursor_MZ"])
        except ValueError:
            raise ValueError(
                f"Invalid Precursor_MZ for scan '{first_cell}': '{fields['Precursor_MZ']}'."
            )

        try:
            num_peaks = int(fields["Num_peaks"])
        except ValueError:
            raise ValueError(
                f"Invalid Num_peaks for scan '{first_cell}': '{fields['Num_peaks']}'."
            )

        rt = None
        if fields.get("RT"):
            try:
                rt = float(fields["RT"])
            except ValueError:
                raise ValueError(f"Invalid RT for scan '{first_cell}': '{fields['RT']}'.")

        ccs = None
        if fields.get("CCS"):
            try:
                ccs = float(fields["CCS"])
            except ValueError:
                raise ValueError(f"Invalid CCS for scan '{first_cell}': '{fields['CCS']}'.")

        fragments = []
        while i < n and not _empty(rows[i]):
            mz, intensity = rows[i][0], rows[i][1]
            fragments.append((float(mz), float(intensity)))
            i += 1

        if not fragments:
            raise ValueError(f"No fragments found for '{first_cell}'.")

        if len(fragments) != num_peaks:
            raise ValueError(
                f"'Num_peaks'={num_peaks} does not match the number of fragments "
                f"found ({len(fragments)}) for '{first_cell}'."
            )

        scans.append(
            {
                "scan_id": scan_id,
                "precursor_mz": precursor_mz,
                "formula": fields["Formula"],
                "lipid_name": fields["Lipid_Name"],
                "fa_composition": fields.get("FA_composition") or None,
                "adduct": fields["Adduct"],
                "lipid_category": fields["Lipid_category"],
                "lipid_class": fields["Lipid_class"],
                "lipid_subclass": fields["Lipid_subclass"],
                "rt": rt,
                "ccs": ccs,
                "num_peaks": num_peaks,
                "fragments": fragments,
            }
        )

    if not scans:
        raise ValueError("No scan found in the file.")

    return scans


def DB_MS2(
    scans: list[dict],
    filename: str,
    integrator: str,
    file_row_name: str,
) -> None:
    """
    Inserts MS2 scans into the database.
    For each scan, creates and inserts a record in the Lipid, Detection
    (+ its Fragments) and Annotation tables.

    :param scans: list of dictionaries (see :func:`parse_ms2_file`), where each scan must
        also carry the derived fields "molecular_weight", "monoisotopic_mass" and
        "neutral_mass" (computed by the caller).
    :type scans: list[dict]
    :param filename: name of the integrated file.
    :type filename: str
    :param integrator: name of the person performing the integration.
    :type integrator: str
    :param file_row_name: name of the file that provided the annotations.
    :type file_row_name: str
    :raises Exception: SQLAlchemy rollback if an insertion error occurs.
    :raises PostIntegrationError: if the scans were committed successfully but the post-commit
        backup or history logging failed - the data is already in the database.
    """
    logger.info(f"Starting MS2 integration - {len(scans)} scans to insert.")
    detections = []

    with Session(get_engine()) as session:
        try:
            for scan in scans:
                lipid = Lipid(
                    Lipid_name=scan["lipid_name"],
                    Lipid_category=scan.get("lipid_category"),
                    Lipid_class=scan.get("lipid_class"),
                    Lipid_subclass=scan.get("lipid_subclass"),
                    Formula=scan["formula"],
                    FA_composition=scan["fa_composition"],
                    Molecular_weight=scan["molecular_weight"],
                    Monoisotopic_mass=scan["monoisotopic_mass"],
                )

                detection = Detection(
                    Precursor_MZ=scan["precursor_mz"],
                    Neutral_mass=scan["neutral_mass"],
                    Ionisation_mode=scan["ion_mode"],
                    Adduct=scan["adduct"],
                    MS_level="MS2",
                    Num_Peaks=scan["num_peaks"],
                    RT=scan.get("rt"),
                    CCS=scan.get("ccs"),
                )

                annotation = Annotation(lipid=lipid, detection=detection)

                session.add(lipid)
                session.add(detection)
                session.add(annotation)
                detections.append(detection)

                for mz, intensity in scan["fragments"]:
                    fragment = Fragment(
                        detection=detection,
                        MZ=mz,
                        Intensity=intensity,
                    )
                    session.add(fragment)

            session.flush()
            detection_ids = [detection.Detection_ID for detection in detections]

            session.commit()
            logger.info(f"MS2 integration completed: {len(scans)} scans inserted.")

        except Exception as e:
            logger.error(f"Error during MS2 integration: {e}")
            raise

    try:
        backup_path = backup_database(label=filename)

        append_history(
            {
                "filename": filename,
                "row_file": file_row_name,
                "inserted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ms_level": "MS2",
                "ionisation_mode": scans[0]["ion_mode"],
                "num_rows": len(scans),
                "detection_ids": detection_ids,
                "integrator": integrator,
                "backup": backup_path.name,
            }
        )
    except Exception as e:
        logger.error(f"Scans were committed but post-integration housekeeping failed: {e}")
        raise PostIntegrationError(
            f"Scans were committed but backup/history logging failed: {e}",
            detection_ids,
        ) from e
