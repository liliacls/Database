# ============================================================
# Dépendances
# ============================================================

from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import pandas as pd

# ============================================================
# Connexion à la base de données
# ============================================================

# Créer une connexion à la base de données SQLite
engine = create_engine("sqlite:///lipids.db", echo=False)
conn = engine.connect()

# ============================================================
# Définition des tables
# ============================================================

Base = declarative_base()

class Organism(Base):
    __tablename__ = 'Organism'
    Organism_ID = Column(Integer, primary_key=True)
    Strain = Column(Text)
    Genus = Column(Text)
    Species = Column(Text)
    Full_name = Column(Text)

class Experiment(Base):
    __tablename__ = 'Experiment'
    Experiment_ID = Column(Integer, primary_key=True)
    Organism_id = Column(Integer, ForeignKey('Organism.Organism_ID'))
    Treatment = Column(Text)
    Culture_mode = Column(Text)
    DOI = Column(Text)

class Method(Base):
    __tablename__ = 'Method'
    Method_ID = Column(Integer, primary_key=True)
    Instrument = Column(Text)
    Instrument_type = Column(Text)
    Source = Column(Text)
    Polarity = Column(Text)
    Fragmentation_mode = Column(Text)

class File(Base):
    __tablename__ = 'File'
    File_ID = Column(Integer, primary_key=True)
    Experiment_id = Column(Integer, ForeignKey('Experiment.Experiment_ID'))
    Method_id = Column(Integer, ForeignKey('Method.Method_ID'))
    Name_file = Column(Text)

class Adduct(Base):
    __tablename__ = 'Adduct'
    Adduct_ID = Column(Integer, primary_key=True)
    Adduct_name = Column(Text)
    Charge = Column(Integer)


class Detection(Base):
    __tablename__ = 'Detection'
    Detection_ID = Column(Integer, primary_key=True)
    Adduct_id = Column(Integer, ForeignKey('Adduct.Adduct_ID'))
    File_id = Column(Integer, ForeignKey('File.File_ID'))
    Precursor_MZ = Column(Float)
    Scan = Column(Integer)
    MS_level = Column(Integer)
    Num_Peaks = Column(Integer)
    Energie_collision = Column(Float)
    Exact_mass = Column(Float)
    Molecular_weight = Column(Float)
    RT = Column(Float)
    CCS = Column(Float)

class Fragment(Base):
    __tablename__ = 'Fragment'
    Fragment_ID = Column(Integer, primary_key=True)
    Detection_id = Column(Integer, ForeignKey('Detection.Detection_ID'))
    MZ = Column(Float)
    Intensity = Column(Float)

class Lipid(Base):
    __tablename__ = 'Lipid'
    Lipids_ID = Column(Integer, primary_key=True)
    Lipid_name = Column(Text)
    Lipid_class = Column(Text)
    Lipid_category = Column(Text)
    Formula = Column(Text)

class Annotation(Base):
    __tablename__ = 'Annotation'
    Annotation_ID = Column(Integer, primary_key=True)
    Lipid_id = Column(Integer, ForeignKey('Lipid.Lipids_ID'))
    Detection_id = Column(Integer, ForeignKey('Detection.Detection_ID'))
    Confidence_level = Column(Integer)

# ============================================================
# Création des tables
# ============================================================
Base.metadata.create_all(engine)
print("Tables créées avec succès !")