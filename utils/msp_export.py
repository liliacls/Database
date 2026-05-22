"""
msp_export.py
-------------
Génère le contenu d'un fichier .msp à partir des annotations MS2 filtrées.
"""

from sqlalchemy.orm import Session, joinedload
from utils.precursor_type import precursor_type

from models.model import Annotation, Detection


def generate_msp(engine, categories: list, classes: list, sub_classes: list, mz_range: tuple) -> str:
    """
    Retourne une chaîne au format .msp pour les détections MS2 correspondant aux filtres.

    :param engine: moteur SQLAlchemy connecté à la base de données.
    :param categories: liste de catégories lipidiques sélectionnées (vide = toutes).
    :param classes: liste de classes lipidiques sélectionnées (vide = toutes).
    :param sub_classes: liste de sous-classes lipidiques sélectionnées (vide = toutes).
    :param mz_range: tuple (mz_min, mz_max) pour filtrer sur le Precursor_MZ.
    :return: fichier .msp prêt à être téléchargé.
    :rtype: str
    """
    
    with Session(engine) as session:
        annotations = (
            session.query(Annotation)
            .join(Annotation.detection)
            .filter(Detection.MS_level == "MS2")
            .filter(Detection.Precursor_MZ >= mz_range[0])
            .filter(Detection.Precursor_MZ <= mz_range[1])
            .options(
                joinedload(Annotation.lipid),
                joinedload(Annotation.detection).joinedload(Detection.fragments),
            )
            .all()
        )

    lines = []
    for a in annotations:
        d = a.detection
        l = a.lipid

        if categories and l.Lipid_category not in categories:
            continue
        if classes and l.Lipid_class not in classes:
            continue
        if sub_classes and l.Lipid_subclass not in sub_classes:
            continue
        if not d.fragments:
            continue

        ptype = precursor_type(d.Neutral_mass, d.Precursor_MZ)

        lines.append(f"Name: {l.Lipid_name}")
        lines.append(f"PrecursorMZ: {d.Precursor_MZ}")
        lines.append(f"Precursor_type: {ptype}")
        lines.append(f"MW: {int(l.Molecular_weight)}")
        lines.append(f"ExactMass: {d.Neutral_mass}")
        lines.append(f"Num Peaks: {d.Num_Peaks}")
        
        for frag in d.fragments:
            lines.append(f"{frag.MZ} {int(frag.Intensity)}")
        lines.append("")

    return "\n".join(lines)
