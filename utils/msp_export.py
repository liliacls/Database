from sqlalchemy.orm import Session, joinedload
from models.model import Annotation, Detection

def generate_msp(
    engine,
    categories: list,
    classes: list,
    sub_classes: list,
    mz_range: tuple,
) -> str:
    """ Returns a string in .msp format for MS2 detections matching the filters.

    :param engine: engine: SQLAlchemy engine connected to the database.
    :param categories: selected lipid category list (empty = all).
    :param classes: selected lipid class list (empty = all).
    :param sub_classes: selected lipid subclass list (empty = all).
    :param mz_range: tuple (mz_min, mz_max) for filtering on Precursor_MZ.
    :return: .msp file ready to be downloaded.
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

        lines.append(f"Name: {l.Lipid_name}")
        lines.append(f"PrecursorMZ: {d.Precursor_MZ}")
        lines.append(f"MW: {int(l.Molecular_weight)}")
        lines.append(f"ExactMass: {d.Neutral_mass}")
        lines.append(f"Num Peaks: {d.Num_Peaks}")

        for frag in d.fragments:
            lines.append(f"{frag.MZ} {int(frag.Intensity)}")
        lines.append("")

    return "\n".join(lines)
