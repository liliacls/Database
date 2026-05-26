"""
Export.py
-----------
Module 3 : Export des données depuis BacLipidDB.

Permet de filtrer les données par catégorie, classe lipidique, niveau MS,
niveau de confiance et plage de m/z, puis de les télécharger en CSV compatible MZmine.
"""

import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

from models.model import Annotation
from config import get_engine
from utils.msp_export import generate_msp as _generate_msp


@st.cache_data
def generate_msp(_engine, categories, classes, sub_classes, mz_range):
    return _generate_msp(_engine, categories, classes, sub_classes, mz_range)


@st.cache_data(ttl=60)
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
                "Lipid_category":   a.lipid.Lipid_category,
                "Lipid_class":      a.lipid.Lipid_class,
                "Lipid_subclass":   a.lipid.Lipid_subclass,
                "mz":               a.detection.Precursor_MZ,
                "neutral_mass":     a.detection.Neutral_mass,
                "MS_level":         a.detection.MS_level,
                "Confidence_level": a.Confidence_level,
                "RT":               a.detection.RT,
                "CCS":              a.detection.CCS,
                "Num_Peaks":        a.detection.Num_Peaks,
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
try:
    df_all = load_data(engine)
except Exception as e:
    st.error(f"Unable to load data from the database: {e}")
    st.stop()

if df_all.empty:
    st.info("The database contains no data yet.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────

st.subheader("Filters")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    categories = sorted(df_all["Lipid_category"].dropna().unique().tolist())
    if df_all["Lipid_category"].isna().any():
        categories = ["(None)"] + categories
    selected_categories = st.multiselect("Lipid category", options=categories)

with col2:
    classes = sorted(df_all["Lipid_class"].dropna().unique().tolist())
    if df_all["Lipid_class"].isna().any():
        classes = ["(None)"] + classes
    selected_classes = st.multiselect("Lipid class", options=classes)

with col3:
    sub_classes = sorted(df_all["Lipid_subclass"].dropna().unique().tolist())
    if df_all["Lipid_subclass"].isna().any():
        sub_classes = ["(None)"] + sub_classes
    selected_sub_classes = st.multiselect("Lipid subclass", options=sub_classes)

col4, _, _ = st.columns(3)

with col4:
    ms_levels = sorted(df_all["MS_level"].dropna().unique().tolist())
    selected_ms = st.multiselect("MS level", options=ms_levels)

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
    mask = df_filtered["Lipid_category"].isin([c for c in selected_categories if c != "(None)"])
    if "(None)" in selected_categories:
        mask |= df_filtered["Lipid_category"].isna()
    df_filtered = df_filtered[mask]

if selected_classes:
    mask = df_filtered["Lipid_class"].isin([c for c in selected_classes if c != "(None)"])
    if "(None)" in selected_classes:
        mask |= df_filtered["Lipid_class"].isna()
    df_filtered = df_filtered[mask]

if selected_sub_classes:
    mask = df_filtered["Lipid_subclass"].isin([c for c in selected_sub_classes if c != "(None)"])
    if "(None)" in selected_sub_classes:
        mask |= df_filtered["Lipid_subclass"].isna()
    df_filtered = df_filtered[mask]

if selected_ms:
    df_filtered = df_filtered[df_filtered["MS_level"].isin(selected_ms)]

df_filtered = df_filtered[
    (df_filtered["mz"] >= mz_range[0]) & (df_filtered["mz"] <= mz_range[1])
]

# ── Preview ───────────────────────────────────────────────────────────────────

st.subheader(f"Preview — {len(df_filtered)} rows")

if df_filtered.empty:
    st.warning("No data matches the selected filters.", icon="⚠️")
    st.stop()

preview_cols = ["name", "formula", "mz", "MS_level", "RT", "CCS", "Num_Peaks"]
df_preview = df_filtered[preview_cols].copy().reset_index(drop=True)
df_preview["Num_Peaks"] = df_preview.apply(
    lambda r: r["Num_Peaks"] if r["MS_level"] == "MS2" else None, axis=1
)
st.dataframe(df_preview, use_container_width=True, height=400)

# ── Download ──────────────────────────────────────────────────────────────────

st.divider()

ms1 = (df_filtered["MS_level"] == "MS1").any()
ms2 = (df_filtered["MS_level"] == "MS2").any()

col_1, col_2 = st.columns(2)

with col_1:
    if ms1:
        df_export = df_filtered[df_filtered["MS_level"] == "MS1"][["neutral_mass", "mz", "formula", "name"]].reset_index(drop=True)
        csv = df_export.to_csv(index=False, lineterminator="\r\n")
        st.download_button(
            label="Download CSV (MS1)",
            data=csv,
            file_name=f"annotation_export_{datetime.now()}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )
    else:
        st.button("Download CSV (MS1)", disabled=True, use_container_width=True)

with col_2:
    if ms2:
        msp = generate_msp(
            engine,
            categories=[None if c == "(None)" else c for c in selected_categories],
            classes=[None if c == "(None)" else c for c in selected_classes],
            sub_classes=[None if c == "(None)" else c for c in selected_sub_classes],
            mz_range=mz_range,
        )
        st.download_button(
            label="Download MSP (MS2)",
            data=msp,
            file_name=f"annotation_export_{datetime.now()}.msp",
            mime="text/plain",
            type="primary",
            use_container_width=True,
        )
    else:
        st.button("Download MSP (MS2)", disabled=True, use_container_width=True)