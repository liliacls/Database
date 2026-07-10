from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    """Declarative base class for all BacLipidDB ORM models.

    All mapped classes (:class:`Detection`, :class:`Fragment`, :class:`Lipid`,
    :class:`Annotation`) inherit from this class so SQLAlchemy can collect
    their metadata and generate the corresponding database tables.
    """
    

class Detection(Base):
    """A single MS1 or MS2 detection (ion observed in a run).

    Stores the precursor m/z, ionisation mode, adduct, retention time and
    CCS. Linked to zero or more :class:`Fragment` rows when ``MS_level`` is
    "MS2", and to one :class:`Annotation`.
    """

    __tablename__ = "Detection"
    Detection_ID: Mapped[int] = mapped_column(primary_key=True)

    Precursor_MZ: Mapped[float] = mapped_column()       # m/z of the ion (Da) - called "precursor" for consistency with MS2, but in MS1 it's not a true precursor since there is no fragmentation
    MS_level: Mapped[str] = (mapped_column)           # "MS1" (precursor only) or "MS2" (with fragment spectrum)
    Ionisation_mode: Mapped[str] = mapped_column()      # "Positive" or "Negative"
    Adduct: Mapped[str] = mapped_column()               # precursor adduct
    Num_Peaks: Mapped[int | None] = (mapped_column)   # number of fragment (MS2 only)
    Neutral_mass: Mapped[float] = (mapped_column)     # neutral mass derived from Precursor_MZ and Adduct (Da)
    RT: Mapped[float | None] = mapped_column()          # retention time (minutes)
    CCS: Mapped[float | None] = mapped_column()         # collision cross section (Ų)

    # Relationship 1→N: a detection can be associated with several fragments (MS2 only)
    fragments: Mapped[list["Fragment"]] = relationship(back_populates="detection")

    # Relationship 1→1: a detection is associated with a single annotation
    annotation: Mapped["Annotation"] = relationship(back_populates="detection")

    def __repr__(self):
        return f"Detection(Detection_ID={self.Detection_ID}, Precursor_MZ={self.Precursor_MZ}, MS_level={self.MS_level}, Ionisation_mode={self.Ionisation_mode}, Adduct={self.Adduct}, Num_Peaks={self.Num_Peaks}, Neutral_mass={self.Neutral_mass}, RT={self.RT}, CCS={self.CCS})"


class Fragment(Base):
    """A fragment ion peak (m/z, intensity) belonging to an MS2 spectrum.

    Each row is attached to the :class:`Detection` it was measured in.
    """

    __tablename__ = "Fragment"
    Fragment_ID: Mapped[int] = mapped_column(primary_key=True)
    Detection_id: Mapped[int] = mapped_column(ForeignKey("Detection.Detection_ID"))

    MZ: Mapped[float | None] = mapped_column()          # m/z of the fragment ion (Da)
    Intensity: Mapped[float | None] = mapped_column()   # fragment peak intensity

    # Relationship N→1: a fragment is attached to a single detection
    detection: Mapped["Detection"] = relationship(back_populates="fragments")

    def __repr__(self):
        return f"Fragment(Fragment_ID={self.Fragment_ID}, Detection_id={self.Detection_id}, MZ={self.MZ}, Intensity={self.Intensity})"


class Lipid(Base):
    """A lipid entity identified by name, formula and LIPID MAPS classification.

    Independent of any given detection; linked to the :class:`Detection` it
    was identified in through a single :class:`Annotation`.
    """

    __tablename__ = "Lipid"
    Lipid_ID: Mapped[int] = mapped_column(primary_key=True)

    Lipid_name: Mapped[str] = mapped_column()
    Lipid_category: Mapped[str | None] = mapped_column()  # LIPID MAPS category
    Lipid_class: Mapped[str | None] = mapped_column()     # LIPID MAPS class
    Lipid_subclass: Mapped[str | None] = mapped_column()  # LIPID MAPS subclass
    Formula: Mapped[str] = mapped_column()
    FA_composition: Mapped[str | None] = mapped_column()  # fatty acyl composition
    Molecular_weight: Mapped[float] = mapped_column()     # average molecular weight (Da)
    Monoisotopic_mass: Mapped[float] = mapped_column()    # monoisotopic mass (Da)

    # Relationship 1→1: a lipid is associated with a single annotation
    annotation: Mapped["Annotation"] = relationship(back_populates="lipid")

    def __repr__(self):
        return f"Lipid(Lipid_ID={self.Lipid_ID}, Lipid_name='{self.Lipid_name}', Lipid_category='{self.Lipid_category}', Lipid_class='{self.Lipid_class}', Lipid_subclass='{self.Lipid_subclass}', Formula='{self.Formula}', FA_composition='{self.FA_composition}', Molecular_weight={self.Molecular_weight}, Monoisotopic_mass={self.Monoisotopic_mass})"


class Annotation(Base):
    """Join table linking one :class:`Lipid` to one :class:`Detection`.

    Represents the identification of a detected ion as a given lipid.
    """

    __tablename__ = "Annotation"
    Annotation_ID: Mapped[int] = mapped_column(primary_key=True)
    Lipid_id: Mapped[int] = mapped_column(ForeignKey("Lipid.Lipid_ID"), unique=True)
    Detection_id: Mapped[int] = mapped_column(
        ForeignKey("Detection.Detection_ID"), unique=True
    )

    # Relationship N→1: an annotation is attached to a single lipid
    lipid: Mapped["Lipid"] = relationship(back_populates="annotation")

    # Relationship N→1: an annotation is attached to a single detection
    detection: Mapped["Detection"] = relationship(back_populates="annotation")

    def __repr__(self):
        return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id})"