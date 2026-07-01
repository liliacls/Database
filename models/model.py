"""
model.py
----------------
Definition of BacLipidDB's SQLAlchemy models.

Contains the 4 tables of the database:
    - Detection  : signal detected by the mass spectrometer.
    - Fragment   : fragment ions associated with a detection (MS2 only)
    - Lipid      : reference lipid (name, class, category, formula)
    - Annotation : association between a detection and a candidate lipid, with a confidence level on the identification

Relationships:
    - Detection  1→N  Fragment    (a signal can produce several fragments, MS2 only)
    - Detection  1→1  Annotation  (a signal corresponds to a single annotation)
    - Lipid      1→1  Annotation  (a lipid is associated with a single annotation)

Conventions:
    - Primary keys are named with the "_ID" suffix
    - Foreign keys are named with the "_id" suffix
    - Each class defines a __repr__ to display an object legibly when debugging

Documentation : 
    - DeclarativeBase : https://docs.sqlalchemy.org/en/21/orm/declarative_styles.html
    - Mapped : https://docs.sqlalchemy.org/en/21/orm/mapping_styles.html#orm-mapping-styles
    - mapped_column : https://docs.sqlalchemy.org/en/21/orm/mapping_api.html#sqlalchemy.orm.Mapper.columns
    - relationship, ForeignKey : https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

class Detection(Base):
    __tablename__ = 'Detection'
    Detection_ID : Mapped[int] = mapped_column(primary_key=True)

    Precursor_MZ : Mapped[float] = mapped_column()  # m/z of the precursor ion (Da)
    MS_level : Mapped[str] = mapped_column()  # "MS1" (precursor only) or "MS2" (with fragment spectrum)
    Ionisation_mode : Mapped[str] = mapped_column()  # "Positive" or "Negative"
    Num_Peaks : Mapped[int | None] = mapped_column()  # number of fragment peaks (MS2 only)
    Neutral_mass : Mapped[float] = mapped_column()  # neutral mass derived from Precursor_MZ and Ionisation_mode (Da)
    RT : Mapped[float | None] = mapped_column()  # retention time (minutes)
    CCS : Mapped[float | None] = mapped_column()  # collision cross section (Ų)

    # Relationship 1→N: a detection can be associated with several fragments (MS2 only)
    fragments: Mapped[list["Fragment"]] = relationship(back_populates="detection")

    # Relationship 1→1: a detection is associated with a single annotation
    annotation: Mapped["Annotation | None"] = relationship(back_populates="detection")

    def __repr__(self):
        return f"Detection(Detection_ID={self.Detection_ID}, Precursor_MZ={self.Precursor_MZ}, MS_level={self.MS_level}, Ionisation_mode={self.Ionisation_mode}, Num_Peaks={self.Num_Peaks}, Neutral_mass={self.Neutral_mass}, RT={self.RT}, CCS={self.CCS})"

class Fragment(Base):
    __tablename__ = 'Fragment'
    Fragment_ID : Mapped[int] = mapped_column(primary_key=True)
    Detection_id : Mapped[int] = mapped_column(ForeignKey('Detection.Detection_ID'))
    
    MZ : Mapped[float | None] = mapped_column()  # m/z of the fragment ion (Da)
    Intensity : Mapped[float | None] = mapped_column()  # fragment peak intensity

    # Relationship N→1: a fragment is attached to a single detection
    detection: Mapped["Detection"] = relationship(back_populates="fragments")

    def __repr__(self):
        return f"Fragment(Fragment_ID={self.Fragment_ID}, Detection_id={self.Detection_id}, MZ={self.MZ}, Intensity={self.Intensity})"

class Lipid(Base):
    __tablename__ = 'Lipid'
    Lipid_ID : Mapped[int] = mapped_column(primary_key=True)

    Lipid_name : Mapped[str] = mapped_column()
    Lipid_category : Mapped[str | None] = mapped_column()  # LIPID MAPS category
    Lipid_class : Mapped[str | None] = mapped_column()  # LIPID MAPS class
    Lipid_subclass : Mapped[str | None] = mapped_column()  # LIPID MAPS subclass
    Formula : Mapped[str] = mapped_column()
    Molecular_weight : Mapped[float] = mapped_column()  # average molecular weight (Da)
    Monoisotopic_mass : Mapped[float] = mapped_column()  # monoisotopic mass (Da)

    # Relationship 1→1: a lipid is associated with a single annotation
    annotation: Mapped["Annotation | None"] = relationship(back_populates="lipid")

    def __repr__(self):
        return f"Lipid(Lipid_ID={self.Lipid_ID}, Lipid_name='{self.Lipid_name}', Lipid_category='{self.Lipid_category}', Lipid_class='{self.Lipid_class}', Lipid_subclass='{self.Lipid_subclass}', Formula='{self.Formula}', Molecular_weight={self.Molecular_weight}, Monoisotopic_mass={self.Monoisotopic_mass})"

class Annotation(Base):
    __tablename__ = 'Annotation'
    Annotation_ID : Mapped[int] = mapped_column(primary_key=True)
    Lipid_id : Mapped[int] = mapped_column(ForeignKey('Lipid.Lipid_ID'), unique=True)
    Detection_id : Mapped[int] = mapped_column(ForeignKey('Detection.Detection_ID'), unique=True)
    
    Confidence_level : Mapped[int | None] = mapped_column()  # annotation confidence, from 1 (highest) to 4 (lowest)

    # Relationship N→1: an annotation is attached to a single lipid
    lipid: Mapped["Lipid"] = relationship(back_populates="annotation")

    # Relationship N→1: an annotation is attached to a single detection
    detection: Mapped["Detection"] = relationship(back_populates="annotation")

    def __repr__(self):
        return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id}, Confidence_level={self.Confidence_level})"