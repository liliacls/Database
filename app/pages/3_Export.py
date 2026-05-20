"""
Export.py
-----------
Module 3 : Export des données depuis BacLipidDB.

Permet de filtrer les données par catégorie, classe lipidique, niveau MS,
niveau de confiance et plage de m/z, puis de les télécharger en CSV compatible MZmine.
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.model import Annotation
from config import DB_PATH


@st.cache_resource
def get_engine():
    """Crée et met en cache la connexion à la base de données."""
    return create_engine(DB_PATH, echo=False)


@st.cache_data
def load_data(_engine):
    """Charge et met en cache toutes les annotations avec leurs données Lipid et Detection associées.

    :param _engine: moteur SQLAlchemy connecté à la base de données.
    :type _engine: sqlalchemy.engine.Engine
    :return: DataFrame avec les colonnes name, formula, Lipid_class, Lipid_category, mz, MS_level,
             Confidence_level, et optionnellement RT et CCS (None si non renseignés).
    :rtype: pandas.DataFrame
    """
    with Session(_engine) as session:
        results = (
            session.query(Annotation)
            .join(Annotation.lipid)
            .join(Annotation.detection)
            .all()
        )
        return pd.DataFrame([
            {
                "name":             a.lipid.Lipid_name,
                "formula":          a.lipid.Formula,
                "Lipid_class":      a.lipid.Lipid_class,
                "Lipid_category":   a.lipid.Lipid_category,
                "mz":               a.detection.Precursor_MZ,
                "MS_level":         a.detection.MS_level,
                "Confidence_level": a.Confidence_level,
                "RT":               a.detection.RT,
                "CCS":              a.detection.CCS,
            }
            for a in results
        ])


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
    <style>
    .module {
        border: 2px solid #1F77B4;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    <div class="module">
        <h1><span style="color:#1F77B4">MODULE 3</span> : Export page</h1>
    </div>
""", unsafe_allow_html=True)
st.write("")

engine = get_engine()
df_all = load_data(engine)

if df_all.empty:
    st.info("The database contains no data yet.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────

st.subheader("Filters")
st.write("")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    categories = sorted(df_all["Lipid_category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Lipid category", options=categories)

with col2:
    classes = sorted(df_all["Lipid_class"].dropna().unique().tolist())
    selected_classes = st.multiselect("Lipid class", options=classes)

with col3:
    ms_levels = sorted(df_all["MS_level"].dropna().unique().tolist())
    selected_ms = st.multiselect("MS level", options=ms_levels)

with col4:
    confidence_levels = sorted(df_all["Confidence_level"].dropna().unique().tolist())
    selected_confidence = st.multiselect("Confidence level", options=confidence_levels)

mz_min = float(df_all["mz"].min())
mz_max = float(df_all["mz"].max())

if mz_min == mz_max:
    st.caption(f"Single m/z value : {mz_min}")
    mz_range = (mz_min, mz_max)
else:
    mz_range = st.slider(
        "Precursor m/z range",
        min_value=mz_min,
        max_value=mz_max,
        value=(mz_min, mz_max),
        step=0.01,
    )

st.divider()

# ── Apply filters ─────────────────────────────────────────────────────────────

df_filtered = df_all.copy()

if selected_categories:
    df_filtered = df_filtered[df_filtered["Lipid_category"].isin(selected_categories)]
if selected_classes:
    df_filtered = df_filtered[df_filtered["Lipid_class"].isin(selected_classes)]
if selected_ms:
    df_filtered = df_filtered[df_filtered["MS_level"].isin(selected_ms)]
if selected_confidence:
    df_filtered = df_filtered[df_filtered["Confidence_level"].isin(selected_confidence)]

df_filtered = df_filtered[
    (df_filtered["mz"] >= mz_range[0]) & (df_filtered["mz"] <= mz_range[1])
]

# ── Preview ───────────────────────────────────────────────────────────────────

st.subheader(f"Preview — {len(df_filtered)} rows")

if df_filtered.empty:
    st.warning("No data matches the selected filters.", icon="⚠️")
    st.stop()

df_preview = df_filtered[["formula", "mz", "name", "RT", "CCS"]].reset_index(drop=True)
st.dataframe(df_preview, use_container_width=True, height=400)

# ── Download ──────────────────────────────────────────────────────────────────

st.divider()

df_export = df_filtered[["formula", "mz", "name"]].reset_index(drop=True)
csv = df_export.to_csv(index=False, encoding="utf-8", lineterminator="\r\n")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="annotation_export.csv",
    mime="text/csv",
    type="primary",
    use_container_width=True,
)