import csv
import io
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.model import Detection, Fragment, Lipid, Annotation
from config import get_engine
from utils.db_backup import backup_database
from utils.history import append_history
from utils.exceptions import PostIntegrationError

logger = logging.getLogger(__name__)

SCAN = "Scan #"
FRAGMENT_HEADER = ("m/z", "Intensity")

# Libellés de champs attendus dans chaque bloc de scan
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

def ms2_parsing(source, delimiter: str | None = None) -> list[dict]:
    """
    Parse un fichier MS2 (.csv/.tsv) organisé en blocs empilés et retourne une liste d'entrées sous forme de dictionnaires.

    :param source: objet fichier-like
    :type source: objet fichier-like
    :param delimiter: séparateur de colonnes. Si None, déduit de l'extension/du nom du fichier ("\\t" pour .tsv, "," sinon).
    :type delimiter: str ou None
    :raises ValueError: si un bloc de scan est mal formé (champ requis manquant, RT/CCS non numérique, en-tête de fragments manquant, aucun fragment trouvé, ou nombre de fragments incohérent avec Num_peaks) ou si aucun scan n'est trouvé dans le fichier.
    :return: liste de dictionnaires avec les clés "scan_id", "precursor_mz", "formula","lipid_name", "fa_composition", "adduct", "lipid_category", "lipid_class","lipid_subclass", "rt", "ccs", "num_peaks" et "fragments" (liste de tuples (mz, intensity)).
    :rtype: list[dict]
    """

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

        if not first_cell.startswith(SCAN):
            i += 1
            continue

        scan_id = first_cell[len(SCAN):].strip()
        i += 1

        fields = {}
        while i < n and tuple(c.strip() for c in rows[i][:2]) != FRAGMENT_HEADER:
            row = rows[i]
            if not row or not row[0].strip():
                i += 1
                continue
            label = row[0].strip()
            value = row[1].strip() if len(row) > 1 else ""
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
        while i < n:
            row = rows[i]
            if row and row[0].strip().startswith(SCAN):
                break
            if not row or not row[0].strip():
                i += 1
                continue
            if len(row) < 2:
                raise ValueError(
                    f"Malformed fragment row {row!r} for scan '{first_cell}': "
                    "expected 'm/z' and 'Intensity' columns."
                )
            try:
                mz, intensity = float(row[0]), float(row[1])
            except ValueError:
                raise ValueError(
                    f"Invalid fragment row {row!r} for scan '{first_cell}': "
                    "'m/z' and 'Intensity' must be numeric."
                )
            fragments.append((mz, intensity))
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
    Insère des scans MS2 dans la base de données. Pour chaque scan, crée et insère un enregistrement dans les tables Lipid, Detection (+ ses Fragments) et Annotation.

    :param scans: liste de dictionnaires (voir :func:`ms2_parsing`), où chaque scan doit aussi porter les champs dérivés "molecular_weight", "monoisotopic_mass", "neutral_mass" et "ion_mode" (calculés/renseignés par l'appelant).
    :type scans: list[dict]
    :param filename: nom du fichier intégré.
    :type filename: str
    :param integrator: nom de la personne réalisant l'intégration.
    :type integrator: str
    :param file_row_name: nom du fichier ayant fourni les annotations.
    :type file_row_name: str
    :raises Exception: exception d'origine relevée (rollback implicite via la fermeture de la session) si une erreur survient pendant l'insertion.
    :raises PostIntegrationError: si les scans ont été validés (commit) avec succès mais que la sauvegarde ou l'écriture de l'historique post-commit a échoué.
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
