"""
Database.py
-----------
Module 2 : Consultation des tables de BacLipidDB.

Permet d'afficher le contenu des tables Detection, Fragment, Lipid et Annotation,
ainsi qu'une vue complète par jointure des tables Detection, Lipid et Annotation.
"""

import logging
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session, joinedload

from models.model import Annotation
from config import get_engine

logger = logging.getLogger(__name__)

st.markdown("""
    <style>
    .module {
        border: 2px solid #1F77B4;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    <div class="module">
        <h1><span style="color:#1F77B4">MODULE 2</span> : Database page</h1>
    </div>
""", unsafe_allow_html=True)
st.write("")

engine = get_engine()

table = st.radio(
    "Select a table",
    options=["Annotation", "Detection", "Fragment", "Lipid", "Full view"],
    horizontal=True,
    key="table_select"
)

st.divider()

try:
    if table == "Full view":
        with Session(engine) as session:
            results = (
                session.query(Annotation)
                .options(
                    joinedload(Annotation.lipid),
                    joinedload(Annotation.detection),
                )
                .all()
            )
            df = pd.DataFrame([
                {
                    "Lipid_name":       a.lipid.Lipid_name,
                    "Formula":          a.lipid.Formula,
                    "Lipid_class":      a.lipid.Lipid_class,
                    "Lipid_subclass":   a.lipid.Lipid_subclass,
                    "Lipid_category":   a.lipid.Lipid_category,
                    "Precursor_MZ":     a.detection.Precursor_MZ,
                    "Neutral_mass":     a.detection.Neutral_mass,
                    "Molecular_weight": a.lipid.Molecular_weight,
                    "MS_level":         a.detection.MS_level,
                    "Num_Peaks":        a.detection.Num_Peaks,
                    "RT":               a.detection.RT,
                    "CCS":              a.detection.CCS,
                    "Confidence_level": a.Confidence_level,
                }
                for a in results
            ])
                
    else:
        df = pd.read_sql_table(table, engine)

    st.subheader(f"Table : {table} - {len(df)} rows")
    if df.empty:
        st.info("This table contains no data yet.")
    else:
        st.dataframe(df, use_container_width=True)

except Exception as e:
    logger.exception("Error loading table '%s'", table)
    st.error(f"Error loading table : {e}")