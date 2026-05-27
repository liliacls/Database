"""
model.py
----------------
Définition des modèles SQLAlchemy de BacLipidDB.

Contient les 4 tables de la base de données :
    - Detection  : signal détecté par le spectromètre de masse.
    - Fragment   : ions fragments associés à une détection (MS2 uniquement)
    - Lipid      : lipide de référence (nom, classe, catégorie, formule)
    - Annotation : association entre une détection et un lipide candidat, avec un niveau de confiance sur l'identification

Relations :
    - Detection  1→N  Fragment    (un signal peut produire plusieurs fragments, MS2 uniquement)
    - Detection  1→N  Annotation  (un signal peut correspondre à plusieurs lipides candidats)
    - Lipid      1→N  Annotation  (un lipide peut être détecté dans plusieurs expériences)

Conventions :
    - Les clés primaires sont nommées avec le suffixe "_ID"
    - Les clés étrangères sont nommées avec le suffixe "_id"
    - Chaque classe définit un __repr__ pour afficher lisiblement un objet lors du débogage
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class Detection(Base):
    __tablename__ = 'Detection'
    Detection_ID : Mapped[int] = mapped_column(primary_key=True)

    Precursor_MZ : Mapped[float] = mapped_column()
    MS_level : Mapped[str] = mapped_column()
    Num_Peaks : Mapped[int] = mapped_column()
    Neutral_mass : Mapped[float] = mapped_column()
    RT : Mapped[Optional[float]] = mapped_column()
    CCS : Mapped[Optional[float]] = mapped_column()

    # Relation 1→N : une détection peut être associée à plusieurs fragments (MS2 uniquement)
    fragments: Mapped[List["Fragment"]] = relationship(back_populates="detection")

    # Relation 1→N : une détection peut être associée à plusieurs annotations
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="detection")

    def __repr__(self):
        return f"Detection(Detection_ID={self.Detection_ID}, Precursor_MZ={self.Precursor_MZ}, MS_level={self.MS_level}, Num_Peaks={self.Num_Peaks}, Neutral_mass={self.Neutral_mass}, RT={self.RT}, CCS={self.CCS})"

class Fragment(Base):
    __tablename__ = 'Fragment'
    Fragment_ID : Mapped[int] = mapped_column(primary_key=True)
    Detection_id : Mapped[int] = mapped_column(ForeignKey('Detection.Detection_ID'))
    
    MZ : Mapped[Optional[float]] = mapped_column()
    Intensity : Mapped[Optional[float]] = mapped_column()

    # Relation N→1 : un fragment est rattaché à une seule détection
    detection: Mapped["Detection"] = relationship(back_populates="fragments")

    def __repr__(self):
        return f"Fragment(Fragment_ID={self.Fragment_ID}, Detection_id={self.Detection_id}, MZ={self.MZ}, Intensity={self.Intensity})"

class Lipid(Base):
    __tablename__ = 'Lipid'
    Lipid_ID : Mapped[int] = mapped_column(primary_key=True)

    Lipid_name : Mapped[str] = mapped_column()
    Lipid_category : Mapped[Optional[str]] = mapped_column()
    Lipid_class : Mapped[Optional[str]] = mapped_column()
    Lipid_subclass : Mapped[Optional[str]] = mapped_column()
    Formula : Mapped[str] = mapped_column()
    Molecular_weight : Mapped[float] = mapped_column()

    # Relation 1→N : un lipide peut être associé à plusieurs annotations
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="lipid")

    def __repr__(self):
        return f"Lipid(Lipid_ID={self.Lipid_ID}, Lipid_name='{self.Lipid_name}', Lipid_category='{self.Lipid_category}', Lipid_class='{self.Lipid_class}', Lipid_subclass='{self.Lipid_subclass}', Formula='{self.Formula}', Molecular_weight={self.Molecular_weight})"

class Annotation(Base):
    __tablename__ = 'Annotation'
    __table_args__ = (UniqueConstraint('Lipid_id', 'Detection_id'),)
    Annotation_ID : Mapped[int] = mapped_column(primary_key=True)
    Lipid_id : Mapped[int] = mapped_column(ForeignKey('Lipid.Lipid_ID'))
    Detection_id : Mapped[int] = mapped_column(ForeignKey('Detection.Detection_ID'))
    
    Confidence_level : Mapped[Optional[int]] = mapped_column()

    # Relation N→1 : une annotation est rattachée à un seul lipide
    lipid: Mapped["Lipid"] = relationship(back_populates="annotations")

    # Relation N→1 : une annotation est rattachée à une seule détection
    detection: Mapped["Detection"] = relationship(back_populates="annotations")

    def __repr__(self):
        return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id}, Confidence_level={self.Confidence_level})"