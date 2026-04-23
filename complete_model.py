from sqlalchemy import Column, Integer, String, Float, ForeignKey
from typing import Optional, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase

# ============================================================
# Définition des tables de la base de données
# Les clés primaires sont nommées avec le suffixe "_ID"
# Les clés étrangères sont nommées avec le suffixe "_id"
# ============================================================

class Base (DeclarativeBase):
    pass

class Organism(Base):
    __tablename__ = 'Organism'
    Organism_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Strain : Mapped[String] = mapped_column()
    Genus : Mapped[String] = mapped_column()
    Species : Mapped[String] = mapped_column()
    Full_name : Mapped[String] = mapped_column()

    # Un organisme peut avoir PLUSIEURS expériences → list
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="organism")

    def __repr__(self):
        return f"Organism(Organism_ID={self.Organism_ID}, Strain='{self.Strain}', Genus='{self.Genus}', Species='{self.Species}', Full_name='{self.Full_name}')"
    
class Experiment(Base):
    __tablename__ = 'Experiment'
    Experiment_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Organism_id : Mapped[Integer] = mapped_column(ForeignKey('Organism.Organism_ID'))
    Treatment : Mapped[String] = mapped_column()
    Culture_mode : Mapped[String] = mapped_column()
    DOI : Mapped[String] = mapped_column()

    # Une expérience appartient à UN SEUL organisme → pas de list
    organism: Mapped["Organism"] = relationship(back_populates="experiments")

def __repr__(self):
    return f"Experiment(Experiment_ID={self.Experiment_ID}, Organism_id={self.Organism_id}, Treatment='{self.Treatment}', Culture_mode='{self.Culture_mode}', DOI='{self.DOI}')"

class Method(Base):
    __tablename__ = 'Method'
    Method_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Instrument : Mapped[String] = mapped_column()
    Instrument_type : Mapped[String] = mapped_column()
    Source : Mapped[String] = mapped_column()
    Polarity : Mapped[String] = mapped_column()
    Fragmentation_mode : Mapped[String] = mapped_column()

def __repr__(self):
    return f"Method(Method_ID={self.Method_ID}, Instrument='{self.Instrument}', Instrument_type='{self.Instrument_type}', Source='{self.Source}', Polarity='{self.Polarity}', Fragmentation_mode='{self.Fragmentation_mode}')"

class File(Base):
    __tablename__ = 'File'
    File_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Experiment_id : Mapped[Integer] = mapped_column(ForeignKey('Experiment.Experiment_ID'))
    Method_id : Mapped[Integer] = mapped_column(ForeignKey('Method.Method_ID'))
    Name_file : Mapped[String] = mapped_column()

def __repr__(self):
    return f"File(File_ID={self.File_ID}, Experiment_id={self.Experiment_id}, Method_id={self.Method_id}, Name_file='{self.Name_file}')"

class Adduct(Base):
    __tablename__ = 'Adduct'
    Adduct_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Adduct_name : Mapped[String] = mapped_column()
    Charge : Mapped[Integer] = mapped_column()

def __repr__(self):
    return f"Adduct(Adduct_ID={self.Adduct_ID}, Adduct_name='{self.Adduct_name}', Charge={self.Charge})"


class Detection(Base):
    __tablename__ = 'Detection'
    Detection_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Adduct_id : Mapped[Integer] = mapped_column(ForeignKey('Adduct.Adduct_ID'))
    File_id : Mapped[Integer] = mapped_column(ForeignKey('File.File_ID'))
    Precursor_MZ : Mapped[Float] = mapped_column()
    Scan : Mapped[Integer] = mapped_column()
    MS_level : Mapped[Integer] = mapped_column()
    Num_Peaks : Mapped[Integer] = mapped_column()
    Energie_collision : Mapped[Float] = mapped_column()
    Exact_mass : Mapped[Float] = mapped_column()
    Molecular_weight : Mapped[Float] = mapped_column()
    RT : Mapped[Float] = mapped_column()
    CCS : Mapped[Float] = mapped_column()

def __repr__(self):
    return f"Detection(Detection_ID={self.Detection_ID}, Adduct_id={self.Adduct_id}, File_id={self.File_id}, Precursor_MZ={self.Precursor_MZ}, Scan={self.Scan}, MS_level={self.MS_level}, Num_Peaks={self.Num_Peaks}, Energie_collision={self.Energie_collision}, Exact_mass={self.Exact_mass}, Molecular_weight={self.Molecular_weight}, RT={self.RT}, CCS={self.CCS})"

class Fragment(Base):
    __tablename__ = 'Fragment'
    Fragment_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Detection_id : Mapped[Integer] = mapped_column(ForeignKey('Detection.Detection_ID'))
    MZ : Mapped[Float] = mapped_column()
    Intensity : Mapped[Float] = mapped_column()

def __repr__(self):
    return f"Fragment(Fragment_ID={self.Fragment_ID}, Detection_id={self.Detection_id}, MZ={self.MZ}, Intensity={self.Intensity})"  

class Lipid(Base):
    __tablename__ = 'Lipid'
    Lipids_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Lipid_name : Mapped[String] = mapped_column()
    Lipid_class : Mapped[String] = mapped_column()
    Lipid_category : Mapped[String] = mapped_column()
    Formula : Mapped[String] = mapped_column()

def __repr__(self):
    return f"Lipid(Lipids_ID={self.Lipids_ID}, Lipid_name='{self.Lipid_name}', Lipid_class='{self.Lipid_class}', Lipid_category='{self.Lipid_category}', Formula='{self.Formula}')"

class Annotation(Base):
    __tablename__ = 'Annotation'
    Annotation_ID : Mapped[Integer] = mapped_column(primary_key=True)
    Lipid_id : Mapped[Integer] = mapped_column(ForeignKey('Lipid.Lipids_ID'))
    Detection_id : Mapped[Integer] = mapped_column(ForeignKey('Detection.Detection_ID'))
    Confidence_level : Mapped[Integer] = mapped_column()

def __repr__(self):
    return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id}, Confidence_level={self.Confidence_level})"