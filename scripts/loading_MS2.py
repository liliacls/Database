"""
load_MS2_msp.py
---------------
Lit un fichier .msp MS2 et insère les données dans BacLipidDB.

Structure d'un fichier .msp attendu :
    PrecursorMZ: <valeur>
    Num Peaks: <n>
    <mz1> <intensity1>
    <mz2> <intensity2>
    ...

Tables alimentées :Detection, Fragment, Lipid et Annotation

Usage :
    python scripts/load_MS2_msp.py
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.model import Detection, Fragment, Lipid, Annotation
from utils.neutral_mass import neutral_mass_cal
from config import DB_PATH

MSP_INPUT = Path("/home/liliacls/Documents/Stage/Data/mzmine/716_negatif_minimal.msp")
ION_MODE  = "Negative"

def parse_msp(path: Path) -> dict:
    """
    Parse un fichier .msp et retourne les données sous forme de dictionnaire.

    :param path: chemin vers le fichier .msp.
    :type path: Path
    :return: dictionnaire avec les clés "precursor_mz", "num_peaks" et "fragments" (liste de tuples (mz, intensity)).
    :rtype: dict
    :raises ValueError: si PrecursorMZ ou Num Peaks sont absents du fichier.
    """

    precursor_mz = None
    num_peaks    = None
    fragments    = []

    with open(path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        
        if line.startswith("PrecursorMZ:"):
            precursor_mz = float(line.split(":")[1].strip())
       
        elif line.startswith("Num Peaks:"):
            num_peaks = int(line.split(":")[1].strip())
        
        elif line and line[0].isdigit():
            mz, intensity = line.split()
            fragments.append((float(mz), float(intensity)))

    if precursor_mz is None:
        raise ValueError("PrecursorMZ introuvable dans le fichier .msp.")
    if num_peaks is None:
        raise ValueError("Num Peaks introuvable dans le fichier .msp.")

    return {
        "precursor_mz": precursor_mz,
        "num_peaks":    num_peaks,
        "fragments":    fragments,
    }

def load_MS2_msp(path: Path) -> None:
    """
    Insère les données d'un fichier .msp MS2 dans la base de données.

    :param path: chemin vers le fichier .msp.
    :type path: Path
    :raises Exception: rollback SQLAlchemy et affichage de l'erreur en cas de problème lors de l'insertion.
    """
    
    data = parse_msp(path)
    engine = create_engine(DB_PATH, echo=False)

    with Session(engine) as session:
        try:
            lipid = Lipid(
                Lipid_name       = "Unknown_MS2_716",
                Formula          = "Unknown",
                Molecular_weight = 0.0,
                Lipid_class      = None,
                Lipid_category   = None,
            )
            session.add(lipid)
            session.flush()

            detection = Detection(
                Precursor_MZ = data["precursor_mz"],
                Neutral_mass = neutral_mass_cal(data["precursor_mz"], ION_MODE),
                MS_level     = "MS2",
                Num_Peaks    = data["num_peaks"],
            )
            session.add(detection)
            session.flush()

            for mz, intensity in data["fragments"]:
                fragment = Fragment(
                    Detection_id = detection.Detection_ID,
                    MZ           = mz,
                    Intensity    = intensity,
                )
                session.add(fragment)

            annotation = Annotation(
                Lipid_id     = lipid.Lipid_ID,
                Detection_id = detection.Detection_ID,
            )
            session.add(annotation)

            session.commit()
            print(f"Intégration terminée.")
            print(f"  Detection  : Precursor_MZ={data['precursor_mz']}, Num_Peaks={data['num_peaks']}")
            print(f"  Fragments  : {len(data['fragments'])} insérés")

        except Exception as e:
            print(f"Erreur lors de l'intégration : {e}")
            raise


if __name__ == "__main__":
    load_MS2_msp(MSP_INPUT)
