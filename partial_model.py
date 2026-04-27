from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from typing import List, Optional


class Base(DeclarativeBase):
    pass

class Detection(Base):
    __tablename__ = 'Detection'
    Detection_ID : Mapped[int] = mapped_column(primary_key=True)

    Precursor_MZ : Mapped[float] = mapped_column()
    Scan : Mapped[Optional[int]] = mapped_column()
    MS_level : Mapped[Optional[int]] = mapped_column()
    Num_Peaks : Mapped[Optional[int]] = mapped_column()
    Energie_collision : Mapped[Optional[float]] = mapped_column()
    Exact_mass : Mapped[Optional[float]] = mapped_column()
    Molecular_weight : Mapped[Optional[float]] = mapped_column()
    RT : Mapped[Optional[float]] = mapped_column()
    CCS : Mapped[Optional[float]] = mapped_column()

    # Une détection peut avoir plusieurs fragments (1 -> N)
    fragments: Mapped[List["Fragment"]] = relationship(back_populates="detection")
    # Une détection peut avoir plusieurs annotations (1 -> N)
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="detection")

def __repr__(self):
    return f"Detection(Detection_ID={self.Detection_ID}, Precursor_MZ={self.Precursor_MZ}, Scan={self.Scan}, MS_level={self.MS_level}, Num_Peaks={self.Num_Peaks}, Energie_collision={self.Energie_collision}, Exact_mass={self.Exact_mass}, Molecular_weight={self.Molecular_weight}, RT={self.RT}, CCS={self.CCS})" 

class Fragment(Base):
    __tablename__ = 'Fragment'
    Fragment_ID : Mapped[int] = mapped_column(primary_key=True)

    Detection_id : Mapped[Optional[int]] = mapped_column(ForeignKey('Detection.Detection_ID'))
    MZ : Mapped[Optional[float]] = mapped_column()
    Intensity : Mapped[Optional[float]] = mapped_column()

    # Un fragment appartient à une seule détection (N -> 1)
    detection: Mapped["Detection"] = relationship(back_populates="fragments")


def __repr__(self):
    return f"Fragment(Fragment_ID={self.Fragment_ID}, Detection_id={self.Detection_id}, MZ={self.MZ}, Intensity={self.Intensity})"  

class Lipid(Base):
    __tablename__ = 'Lipid'
    Lipids_ID : Mapped[int] = mapped_column(primary_key=True)

    Lipid_name : Mapped[Optional[str]] = mapped_column()
    Lipid_class : Mapped[Optional[str]] = mapped_column()
    Lipid_category : Mapped[Optional[str]] = mapped_column()
    Formula : Mapped[Optional[str]] = mapped_column()

    # Un lipide peut être associé à plusieurs annotations (1 -> N)
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="lipid")

def __repr__(self):
    return f"Lipid(Lipids_ID={self.Lipids_ID}, Lipid_name='{self.Lipid_name}', Lipid_class='{self.Lipid_class}', Lipid_category='{self.Lipid_category}', Formula='{self.Formula}')"

class Annotation(Base):
    __tablename__ = 'Annotation'
    Annotation_ID : Mapped[int] = mapped_column(primary_key=True)
    
    Lipid_id : Mapped[Optional[int]] = mapped_column(ForeignKey('Lipid.Lipids_ID'))
    Detection_id : Mapped[Optional[int]] = mapped_column(ForeignKey('Detection.Detection_ID'))
    Confidence_level : Mapped[Optional[int]] = mapped_column()

    # Une annotation pointe vers un seul lipide (N -> 1)
    lipid: Mapped["Lipid"] = relationship(back_populates="annotations")
    # Une annotation pointe vers une seule détection (N -> 1)
    detection: Mapped["Detection"] = relationship(back_populates="annotations")

def __repr__(self):
    return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id}, Confidence_level={self.Confidence_level})"