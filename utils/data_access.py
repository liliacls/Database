import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, joinedload
from models.model import Annotation

@st.cache_data(ttl=60)
def load_database(_engine: Engine) -> pd.DataFrame:
    """
    Load and cache the full joined view (Annotation + Lipid + Detection).

    :param _engine: SQLAlchemy engine connected to the database
    :type _engine: sqlalchemy.engine.Engine
    :return: DataFrame with one row per Annotation, joined with its Lipid and Detection.
    :rtype: pandas.DataFrame
    """
    with Session(_engine) as session:
        results = (
            session.query(Annotation)
            .options(
                joinedload(Annotation.lipid),
                joinedload(Annotation.detection),
            )
            .order_by(Annotation.Annotation_ID)
            .all()
        )
        return pd.DataFrame([
            {
                "Annotation_ID":     a.Annotation_ID,
                "Detection_ID":      a.detection.Detection_ID,
                "Lipid_ID":          a.lipid.Lipid_ID,
                "Lipid_name":        a.lipid.Lipid_name,
                "Formula":           a.lipid.Formula,
                "FA_composition":    a.lipid.FA_composition,
                "Lipid_category":    a.lipid.Lipid_category,
                "Lipid_class":       a.lipid.Lipid_class,
                "Lipid_subclass":    a.lipid.Lipid_subclass,
                "Precursor_MZ":      a.detection.Precursor_MZ,
                "Adduct":            a.detection.Adduct,
                "Neutral_mass":      a.detection.Neutral_mass,
                "Molecular_weight":  a.lipid.Molecular_weight,
                "Monoisotopic_mass": a.lipid.Monoisotopic_mass,
                "MS_level":          a.detection.MS_level,
                "Ionisation_mode":   a.detection.Ionisation_mode,
                "Num_Peaks":         a.detection.Num_Peaks,
                "RT":                a.detection.RT,
                "CCS":               a.detection.CCS,
            }
            for a in results
        ])