"""
complete_model.py
-----------------
Définition des modèles SQLAlchemy de BacLipidDB (modèle complet).

Contient les 8 tables de la base de données :
    - Organism   : organisme source (genre, espèce, souche)
    - Experiment : expérience associée à un organisme
    - Method     : méthode d'acquisition
    - File       : fichier de données associé à une expérience et une méthode
    - Adduct     : adduit ionique
    - Detection  : signal détecté par le spectromètre de masse
    - Fragment   : ions fragments associés à une détection (MS2 uniquement)
    - Lipid      : lipide identifié (nom, classe, catégorie, formule)
    - Annotation : lien entre une détection et un lipide, avec un niveau de confiance

Relations :
    - Organism   1→N  Experiment  (un organisme peut avoir plusieurs expériences)
    - Experiment 1→N  File        (une expérience peut avoir plusieurs fichiers)
    - Method     1→N  File        (une méthode peut être utilisée dans plusieurs fichiers)
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
from sqlalchemy import ForeignKey
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class Organism(Base):
    __tablename__ = 'Organism'
    Organism_ID : Mapped[int] = mapped_column(primary_key=True)

    Strain : Mapped[Optional[str]] = mapped_column()
    Genus : Mapped[Optional[str]] = mapped_column()
    Species : Mapped[Optional[str]] = mapped_column()
    Full_name : Mapped[Optional[str]] = mapped_column()

    # Relation 1→N : un organisme peut avoir plusieurs expériences
    experiments: Mapped[List["Experiment"]] = relationship(back_populates="organism")

    def __repr__(self):
        return f"Organism(Organism_ID={self.Organism_ID}, Strain='{self.Strain}', Genus='{self.Genus}', Species='{self.Species}', Full_name='{self.Full_name}')"

class Experiment(Base):
    __tablename__ = 'Experiment'
    Experiment_ID : Mapped[int] = mapped_column(primary_key=True)
    Organism_id : Mapped[int] = mapped_column(ForeignKey('Organism.Organism_ID'))

    Treatment : Mapped[Optional[str]] = mapped_column()
    Culture_mode : Mapped[Optional[str]] = mapped_column()
    DOI : Mapped[Optional[str]] = mapped_column()

    # Relation N→1 : une expérience est rattachée à un seul organisme
    organism: Mapped["Organism"] = relationship(back_populates="experiments")

    # Relation 1→N : une expérience peut avoir plusieurs fichiers
    files: Mapped[List["File"]] = relationship(back_populates="experiment")

    def __repr__(self):
        return f"Experiment(Experiment_ID={self.Experiment_ID}, Organism_id={self.Organism_id}, Treatment='{self.Treatment}', Culture_mode='{self.Culture_mode}', DOI='{self.DOI}')"

class Method(Base):
    __tablename__ = 'Method'
    Method_ID : Mapped[int] = mapped_column(primary_key=True)

    Instrument : Mapped[str] = mapped_column()
    Instrument_type : Mapped[str] = mapped_column()
    Source : Mapped[str] = mapped_column()
    Polarity : Mapped[str] = mapped_column()
    Fragmentation_mode : Mapped[str] = mapped_column()

    # Relation 1→N : une méthode peut être utilisée dans plusieurs fichiers
    files: Mapped[List["File"]] = relationship(back_populates="method")

    def __repr__(self):
        return f"Method(Method_ID={self.Method_ID}, Instrument='{self.Instrument}', Instrument_type='{self.Instrument_type}', Source='{self.Source}', Polarity='{self.Polarity}', Fragmentation_mode='{self.Fragmentation_mode}')"

class File(Base):
    __tablename__ = 'File'
    File_ID : Mapped[int] = mapped_column(primary_key=True)
    Experiment_id : Mapped[int] = mapped_column(ForeignKey('Experiment.Experiment_ID'))
    Method_id : Mapped[int] = mapped_column(ForeignKey('Method.Method_ID'))

    Name_file : Mapped[Optional[str]] = mapped_column()

    # Relation N→1 : un fichier est rattaché à une seule expérience
    experiment: Mapped["Experiment"] = relationship(back_populates="files")

    # Relation N→1 : un fichier est rattaché à une seule méthode
    method: Mapped["Method"] = relationship(back_populates="files")

    def __repr__(self):
        return f"File(File_ID={self.File_ID}, Experiment_id={self.Experiment_id}, Method_id={self.Method_id}, Name_file='{self.Name_file}')"

class Adduct(Base):
    __tablename__ = 'Adduct'
    Adduct_ID : Mapped[int] = mapped_column(primary_key=True)

    Adduct_name : Mapped[str] = mapped_column()
    Charge : Mapped[int] = mapped_column()

    def __repr__(self):
        return f"Adduct(Adduct_ID={self.Adduct_ID}, Adduct_name='{self.Adduct_name}', Charge={self.Charge})"

class Detection(Base):
    __tablename__ = 'Detection'
    Detection_ID : Mapped[int] = mapped_column(primary_key=True)

    Precursor_MZ : Mapped[float] = mapped_column()
    Scan : Mapped[Optional[int]] = mapped_column()
    MS_level : Mapped[Optional[str]] = mapped_column()
    Num_Peaks : Mapped[Optional[int]] = mapped_column()
    Energie_collision : Mapped[Optional[float]] = mapped_column()
    Exact_mass : Mapped[Optional[float]] = mapped_column()
    Molecular_weight : Mapped[Optional[float]] = mapped_column()
    RT : Mapped[Optional[float]] = mapped_column()
    CCS : Mapped[Optional[float]] = mapped_column()

    # Relation 1→N : une détection peut être associée à plusieurs fragments (MS2 uniquement)
    fragments: Mapped[List["Fragment"]] = relationship(back_populates="detection")

    # Relation 1→N : une détection peut être associée à plusieurs annotations
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="detection")

    def __repr__(self):
        return f"Detection(Detection_ID={self.Detection_ID}, Precursor_MZ={self.Precursor_MZ}, Scan={self.Scan}, MS_level={self.MS_level}, Num_Peaks={self.Num_Peaks}, Energie_collision={self.Energie_collision}, Exact_mass={self.Exact_mass}, Molecular_weight={self.Molecular_weight}, RT={self.RT}, CCS={self.CCS})"

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
    Lipids_ID : Mapped[int] = mapped_column(primary_key=True)

    Lipid_name : Mapped[str] = mapped_column()
    Lipid_class : Mapped[Optional[str]] = mapped_column()
    Lipid_category : Mapped[Optional[str]] = mapped_column()
    Formula : Mapped[str] = mapped_column()

    # Relation 1→N : un lipide peut être associé à plusieurs annotations
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="lipid")

    def __repr__(self):
        return f"Lipid(Lipids_ID={self.Lipids_ID}, Lipid_name='{self.Lipid_name}', Lipid_class='{self.Lipid_class}', Lipid_category='{self.Lipid_category}', Formula='{self.Formula}')"

class Annotation(Base):
    __tablename__ = 'Annotation'
    Annotation_ID : Mapped[int] = mapped_column(primary_key=True)
    Lipid_id : Mapped[int] = mapped_column(ForeignKey('Lipid.Lipids_ID'))
    Detection_id : Mapped[int] = mapped_column(ForeignKey('Detection.Detection_ID'))

    Confidence_level : Mapped[Optional[int]] = mapped_column()

    # Relation N→1 : une annotation est rattachée à un seul lipide
    lipid: Mapped["Lipid"] = relationship(back_populates="annotations")

    # Relation N→1 : une annotation est rattachée à une seule détection
    detection: Mapped["Detection"] = relationship(back_populates="annotations")

    def __repr__(self):
        return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id}, Confidence_level={self.Confidence_level})"