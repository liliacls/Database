"""
export_MS2_msp.py
-----------------
Exporte les données MS2 de BacLipidDB vers un fichier .msp.

Format .msp généré par entrée :
    Name: <Lipid_name>
    PrecursorMZ: <Precursor_MZ>
    Precursor_type: [M-H]- ou [M+H]+
    MW: <Molecular_weight>
    ExactMass: <Neutral_mass>
    Num Peaks: <Num_Peaks>
    <mz1> <intensity1>
    ...
    (ligne vide entre chaque entrée)

Le Precursor_type est déduit depuis Neutral_mass et Precursor_MZ :
    Neutral_mass > Precursor_MZ → mode négatif [M-H]-
    Neutral_mass < Precursor_MZ → mode positif [M+H]+

Usage :
    python scripts/export_MS2_msp.py
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload

from models.model import Annotation, Detection
from config import DB_PATH

MSP_OUTPUT = Path("/home/liliacls/Documents/Stage/Data/mzmine/export_MS2.msp")


def precursor_type(neutral_mass: float, precursor_mz: float) -> str:
    """
    Déduit le type de précurseur à partir de la masse neutre et du m/z.

    :param neutral_mass: masse neutre calculée (Daltons).
    :type neutral_mass: float
    :param precursor_mz: rapport m/z mesuré.
    :type precursor_mz: float
    :return: "[M-H]-" si mode négatif, "[M+H]+" si mode positif.
    :rtype: str
    """
    return "[M-H]-" if neutral_mass > precursor_mz else "[M+H]+"

def export_MS2_msp(msp_output: Path) -> None:
    """
    Exporte toutes les détections MS2 de la base vers un fichier .msp.

    :param msp_output: chemin du fichier .msp à générer.
    :type msp_output: Path
    :raises Exception: si la requête ou l'écriture du fichier échoue.
    """

    engine = create_engine(DB_PATH, echo=False)

    with Session(engine) as session:
        annotations = (
            session.query(Annotation)
            .join(Annotation.detection)
            .filter(Detection.MS_level == "MS2")
            .options(
                joinedload(Annotation.lipid),
                joinedload(Annotation.detection).joinedload(Detection.fragments),
            )
            .all()
        )

    msp_output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(msp_output, "w", encoding="utf-8") as f:
        for a in annotations:
            detection = a.detection
            lipid     = a.lipid

            if not detection.fragments:
                continue

            precursor_type = precursor_type(detection.Neutral_mass, detection.Precursor_MZ)

            f.write(f"Name: {lipid.Lipid_name}\n")
            f.write(f"PrecursorMZ: {detection.Precursor_MZ}\n")
            f.write(f"Precursor_type: {precursor_type}\n")
            f.write(f"MW: {int(lipid.Molecular_weight)}\n")
            f.write(f"ExactMass: {detection.Neutral_mass}\n")
            f.write(f"Num Peaks: {detection.Num_Peaks}\n")

            for fragment in detection.fragments:
                f.write(f"{fragment.MZ} {int(fragment.Intensity)}\n")

            f.write("\n")
            count += 1

    print(f"Fichier créé : {msp_output} - {count} entrée(s) exportée(s).")


if __name__ == "__main__":
    export_MS2_msp(MSP_OUTPUT)
    