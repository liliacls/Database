"""
Data_Integration.py
-------------------
Module 1 : Intégration de données lipidiques dans BacLipidDB.

Workflow en 5 étapes :
    1. Settings      : sélection du niveau MS, mode d'ionisation et niveau de confiance.
    2. File upload   : chargement d'un fichier .xlsx / .csv / .tsv.
    3. Verification  : contrôle de la présence des colonnes obligatoires.
    4. Completion    : calcul automatique des colonnes dérivées, édition et validation.
    5. Integration   : insertion dans les tables Detection, Lipid et Annotation.

Colonnes obligatoires : Lipid_Name, Formula, Precursor_MZ.
Colonnes optionnelles : RT, CCS.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_loading.data_MS1_load import database_loading_MS1
from utils.lipid_class_calc import lipid_class_calculation, lipid_category_calculation
from utils.molecularw_calc import molecularw_calculation
from utils.exact_mass_calc import exact_mass_calculation

# Colonnes obligatoire pour l'annotation MS1
REQUIRED_COLUMNS = ['Lipid_Name', 'Formula', 'Precursor_MZ']


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _icon(done):
    """ Affichage de l'icône de progression selon l'état d'une étape du worflow """
    return "✅" if done else "⬜"

step1_done = all(st.session_state.get(k) is not None for k in ["ms_level", "ion_mode", "confidence_level"])

with st.sidebar:
    st.markdown("### Workflow")
    st.markdown(f"{_icon(step1_done)} Step 1 - Settings")
    st.markdown(f"{_icon('df' in st.session_state)} Step 2 - File upload")
    st.markdown(f"{_icon(st.session_state.get('columns_valid', False))} Step 3 - Verification")
    st.markdown(f"{_icon('df_valide' in st.session_state)} Step 4 - Completion")
    st.markdown(f"{_icon(st.session_state.get('integration_done', False))} Step 5 - Integration")
    st.divider()
    if st.button("Reset 🔄", type="secondary", use_container_width=True):
        for key in ["df", "df_file_name", "df_complete", "df_valide", "integration_done", "columns_valid"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

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
        <h1><span style="color:#1F77B4">MODULE 1</span> : Data integration page</h1>
    </div>
""", unsafe_allow_html=True)

# ── STEP 1 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 1] - Settings", text_alignment="left")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    ms_level = st.selectbox(
        "Annotation level",
        options=["MS1", "MS2", "MS3"],
        index=None,
        placeholder="Annotation level",
        key="ms_level",
    )

with col2:
    ion_mode = st.selectbox(
        "Ionization mode",
        options=["Positive", "Negative"],
        index=None,
        placeholder="Ionization mode",
        key="ion_mode",
    )

with col3:
    confidence_level = st.selectbox(
        "Confidence level",
        options=[1, 2, 3, 4],
        index=None,
        placeholder="Confidence level",
        key="confidence_level",
    )

if None in [ms_level, ion_mode, confidence_level]:
    st.warning("Please fill in all parameters before continuing.", icon="⚠️")
    st.stop()
else:
    st.success(f"Selected : {ms_level} | {ion_mode} | Confidence {confidence_level}", icon="✅")

# ── STEP 2 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 2] - File upload", text_alignment="left")
st.divider()

uploaded_file = st.file_uploader(
    "Choose an annotation file",
    type=["csv", "xlsx", "tsv"],
    accept_multiple_files=False,
    key="file_uploader",
)

if uploaded_file is None:
    st.stop()

try:
    if st.session_state.get("df_file_name") != uploaded_file.name:
        if uploaded_file.name.endswith(".csv"):
            df_new = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".tsv"):
            df_new = pd.read_csv(uploaded_file, sep='\t')
        else:
            df_new = pd.read_excel(uploaded_file)
        for key in ["df_complete", "df_valide", "integration_done", "columns_valid"]:
            st.session_state.pop(key, None)
        st.session_state["df"] = df_new
        st.session_state["df_file_name"] = uploaded_file.name
        st.rerun()

    st.success(f"File loaded : {uploaded_file.name} - {len(st.session_state['df'])} rows detected.", icon="✅")

except Exception as e:
    st.error(f"Error loading file : {e}")
    st.stop()

df = st.session_state["df"]

# ── STEP 3 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 3] - Required columns verification", text_alignment="left")
st.divider()

missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
    st.session_state["columns_valid"] = False
    st.error(
        f"The file is missing the following required columns : "
        f"**{', '.join(missing_columns)}**\n\n"
        f"Please correct your file and reload it."
    )
    st.stop()
else:
    if not st.session_state.get("columns_valid", False):
        st.session_state["columns_valid"] = True
        st.rerun()
    st.success("All required columns found", icon="✅")
    with st.expander("Preview raw data", expanded=True):
        st.dataframe(df, use_container_width=True)

# ── STEP 4 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 4] - Preview and automatic completion", text_alignment="left")
st.divider()

if "df_complete" not in st.session_state:
    if st.button("Run automatic completion", type="primary", use_container_width=True):
        with st.spinner("Computing derived columns..."):
            try:
                df["Exact_mass"] = df["Precursor_MZ"].apply(
                    lambda mz: exact_mass_calculation(mz, ion_mode)
                )
            except Exception as e:
                st.error(f"Error calculating exact mass : {e}")
                st.stop()

            try:
                df["Molecular_weight"] = df["Formula"].apply(
                    lambda f: molecularw_calculation(f)
                )
            except Exception as e:
                st.error(f"Error calculating molecular weight : {e}")
                st.stop()

            try:
                df["Lipid_class"] = df["Lipid_Name"].apply(
                    lambda n: lipid_class_calculation(n)
                )
            except Exception as e:
                st.error(f"Error inferring lipid class : {e}")
                st.stop()

            try:
                df["Lipid_category"] = df["Lipid_class"].apply(
                    lambda c: lipid_category_calculation(c)
                )
            except Exception as e:
                st.error(f"Error inferring lipid category : {e}")
                st.stop()

            df["MS_level"] = ms_level
            df["Num_Peaks"] = 0 if ms_level == "MS1" else None

        st.session_state["df_complete"] = df
        st.rerun()

if "df_complete" not in st.session_state:
    st.stop()

st.caption(f"Settings : {ms_level} | {ion_mode} | Confidence {confidence_level}")
df_edite = st.data_editor(
    st.session_state["df_complete"],
    use_container_width=True,
    num_rows="dynamic",
    key="editor_integration"
)

if st.button("Validate data", type="primary", use_container_width=True):
    if df_edite.isnull().any().any():
        colonnes_vides = df_edite.columns[df_edite.isnull().any()].tolist()
        st.warning(
            f"The table contains empty cells in : **{', '.join(colonnes_vides)}**",
            icon="⚠️",
        )
    else:
        st.session_state["df_valide"] = df_edite
        st.rerun()

if "df_valide" in st.session_state:
    st.subheader("Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**By lipid class :**")
        st.dataframe(
            st.session_state["df_valide"]["Lipid_class"]
            .value_counts()
            .rename_axis("Class")
            .reset_index(name="Count"),
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.markdown("**By lipid category :**")
        st.dataframe(
            st.session_state["df_valide"]["Lipid_category"]
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Count"),
            use_container_width=True,
            hide_index=True,
        )

    st.info(f"Total : **{len(st.session_state['df_valide'])}** lipids to integrate.")

# ── STEP 5 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 5] - Database integration", text_alignment="left")
st.divider()

if "df_valide" not in st.session_state:
    st.warning("Please validate the data in step 4 before continuing.", icon="⚠️")
    st.stop()

if st.session_state.get("integration_done", False):
    st.success(
        "Integration already completed. Use the **Reset** button in the sidebar to start a new integration.",
        icon="✅",
    )
else:
    st.info(f"Ready to integrate **{len(st.session_state['df_valide'])}** lipids into the database.")
    if st.button("Integrate data", type="primary", use_container_width=True):
        with st.spinner("Integrating data into the database..."):
            try:
                database_loading_MS1(st.session_state["df_valide"], confidence_level)
                st.session_state["integration_done"] = True
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error during database integration : {e}")