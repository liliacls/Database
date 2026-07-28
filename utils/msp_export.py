from sqlalchemy.orm import Session, joinedload
from models.model import Annotation, Detection

ION_MODE = {"Positive": "P", "Negative": "N"}

def generate_msp(
    engine,
    categories: list,
    classes: list,
    sub_classes: list,
    mz_range: tuple,
    ionisation_modes: list | None = None,
) -> str:
    """
    Retourne une chaîne au format .msp pour les détections MS2 correspondant aux filtres.

    :param engine: moteur SQLAlchemy connecté à la base de données.
    :param categories: liste des catégories de lipides sélectionnées (vide = toutes).
    :type categories: list
    :param classes: liste des classes de lipides sélectionnées (vide = toutes).
    :type classes: list
    :param sub_classes: liste des sous-classes de lipides sélectionnées (vide = toutes).
    :type sub_classes: list
    :param mz_range: tuple (mz_min, mz_max) pour filtrer sur Precursor_MZ.
    :type mz_range: tuple
    :param ionisation_modes: liste des modes d'ionisation sélectionnés, "Positive"/"Negative" (None = tous).
    :type ionisation_modes: list | None
    :return: contenu du fichier .msp prêt à être téléchargé.
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
        if ionisation_modes and d.Ionisation_mode not in ionisation_modes:
            continue
        if not d.fragments:
            continue

        lines.append(f"Name: {l.Lipid_name}")
        lines.append(f"PrecursorMZ: {d.Precursor_MZ}")
        lines.append(f"MW: {round(l.Molecular_weight)}")
        lines.append(f"ExactMass: {d.Neutral_mass}")
        lines.append(f"Ion_mode: {ION_MODE.get(d.Ionisation_mode, d.Ionisation_mode)}")
        if d.RT is not None:
            lines.append(f"RT: {d.RT}")
        if d.CCS is not None:
            lines.append(f"CCS: {d.CCS}")
        lines.append(f"Num Peaks: {len(d.fragments)}")

        for frag in d.fragments:
            lines.append(f"{frag.MZ} {int(frag.Intensity)}")
        lines.append("")

    return "\n".join(lines)
