"""
Data_Integration.py
-------------------
Module 1 : Intégration de données lipidiques dans BacLipidDB.

Colonnes obligatoires : Lipid_Name, Formula, Precursor_MZ, Lipid_category , Lipid_class, Lipid_subclass.
Colonnes optionnelles : RT, CCS.

Workflow en 5 étapes :
    1. Settings      : sélection du niveau MS, mode d'ionisation et niveau de confiance.
    2. File upload   : chargement d'un fichier .xlsx, .csv, .tsv
    3. Verification  : contrôle de la présence des colonnes obligatoires.
    4. Completion    : calcul automatique des colonnes dérivées, édition et validation.
    5. Integration   : insertion dans les tables Detection, Lipid et Annotation.
"""

import streamlit as st
import pandas as pd

from utils.loading_MS1 import database_loading_MS1
from utils.molecular_weight import molecularw_calculation
from utils.neutral_mass import neutral_mass_cal

# Colonnes obligatoires pour l'annotation MS1
REQUIRED_COLUMNS = ["Lipid_Name", "Formula", "Precursor_MZ", "Lipid_category", "Lipid_class", "Lipid_subclass"]


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _icon(done):
    return "✅" if done else "⬜"

step1_done = all(st.session_state.get(k) is not None for k in ["ms_level", "ion_mode", "confidence_level"])

with st.sidebar:
    st.markdown("### Workflow")
    st.markdown(f"{_icon(step1_done)} Step 1 - Settings")
    st.markdown(f"{_icon('df' in st.session_state)} Step 2 - File upload")
    st.markdown(f"{_icon(st.session_state.get('columns_valid', False))} Step 3 - Verification")
    st.markdown(f"{_icon('df_valide' in st.session_state)} Step 4 - Completion & Validation")
    st.markdown(f"{_icon(st.session_state.get('integration_done', False))} Step 5 - Integration")
    st.divider()
    if st.button("Reset 🔄", type="secondary", use_container_width=True):
        for key in ["df", "df_file_id", "df_complete", "df_valide", "integration_done", "columns_valid", "editor_integration"]:
            st.session_state.pop(key, None)
        st.session_state["ms_level"] = None
        st.session_state["ion_mode"] = None
        st.session_state["confidence_level"] = None
        st.session_state["file_uploader"] = None
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

_locked = "df_complete" in st.session_state

with col1:
    ms_level = st.selectbox(
        "Annotation level",
        options=["MS1", "MS2"],
        index=None,
        placeholder="Annotation level",
        key="ms_level",
        disabled=_locked,
    )

with col2:
    ion_mode = st.selectbox(
        "Ionization mode",
        options=["Positive", "Negative"],
        index=None,
        placeholder="Ionization mode",
        key="ion_mode",
        disabled=_locked,
    )

with col3:
    confidence_level = st.selectbox(
        "Confidence level",
        options=[1, 2, 3, 4],
        index=None,
        placeholder="Confidence level",
        key="confidence_level",
        disabled=_locked,
    )

if None in [ms_level, ion_mode, confidence_level]:
    st.warning("Please fill in all parameters before continuing.", icon="⚠️")
    st.stop()

st.success(f"Selected : {ms_level} | {ion_mode} | Confidence {confidence_level}", icon="✅")

# ── STEP 2 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 2] - File upload", text_alignment="left")
st.divider()

uploaded_file = st.file_uploader(
    "Choose an annotation file",
    type=["csv", "xlsx", "tsv"],
    key="file_uploader",
)

if uploaded_file is None:
    st.stop()

try:
    if st.session_state.get("df_file_id") != uploaded_file.file_id:
        if uploaded_file.name.endswith(".csv"):
            df_new = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".tsv"):
            df_new = pd.read_csv(uploaded_file, sep="\t")
        else:
            df_new = pd.read_excel(uploaded_file)
        for key in ["df_complete", "df_valide", "integration_done", "columns_valid", "editor_integration"]:
            st.session_state.pop(key, None)
        st.session_state["df"] = df_new
        st.session_state["df_file_id"] = uploaded_file.file_id
        st.rerun()

    st.success(f"File loaded : {uploaded_file.name} - {len(st.session_state['df'])} rows detected.", icon="✅")

except Exception as e:
    st.error(f"Error loading file : {e}")
    st.stop()

df = st.session_state["df"].copy()

# ── STEP 3 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 3] - Required columns verification", text_alignment="left")
st.divider()

missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
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
                df["Neutral_mass"] = df["Precursor_MZ"].apply(
                    lambda mz: neutral_mass_cal(mz, ion_mode)
                )
            except Exception as e:
                st.error(f"Error calculating neutral mass : {e}")
                st.stop()

            df["Molecular_weight"] = df["Formula"].apply(molecularw_calculation)
            invalid_formulas = df.loc[df["Molecular_weight"].isna(), "Formula"].tolist()
            if invalid_formulas:
                st.error(
                    f"Cannot compute molecular weight for the following formula(s) : "
                    f"**{', '.join(str(f) for f in invalid_formulas)}**\n\n"
                    f"Please correct these formulas in your file and reload it."
                )
                st.stop()

            df["MS_level"] = ms_level
            df["Num_Peaks"] = 0

        st.session_state["df_complete"] = df
        st.rerun()

if "df_complete" not in st.session_state:
    st.stop()

st.caption(f"Settings : {ms_level} | {ion_mode} | Confidence {confidence_level}")
df_edite = st.data_editor(
    st.session_state["df_complete"],
    use_container_width=True,
    num_rows="dynamic",
    key="editor_integration",
    column_config={
        "Neutral_mass":     st.column_config.NumberColumn(disabled=True),
        "Molecular_weight": st.column_config.NumberColumn(disabled=True),
        "MS_level":         st.column_config.TextColumn(disabled=True),
        "Num_Peaks":        st.column_config.NumberColumn(disabled=True),
    },
)

if st.button("Validate data", type="primary", use_container_width=True):
    strictly_required = ["Lipid_Name", "Formula", "Precursor_MZ"]
    colonnes_vides = [c for c in strictly_required if df_edite[c].isnull().any()]
    if colonnes_vides:
        st.warning(
            f"The table contains empty cells in required columns : **{', '.join(colonnes_vides)}**",
            icon="⚠️",
        )
    else:
        st.session_state["df_valide"] = df_edite
        st.rerun()

if "df_valide" in st.session_state:
    st.subheader("Summary")

    df_valide = st.session_state["df_valide"]
    total = len(df_valide)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total lipids", total)
    m2.metric("Categories", df_valide["Lipid_category"].nunique())
    m3.metric("Classes", df_valide["Lipid_class"].nunique())
    m4.metric("Subclasses", df_valide["Lipid_subclass"].nunique())

    st.markdown("")
    col_cat, col_class, col_subclass = st.columns(3)

    for col, field, label in [
        (col_cat, "Lipid_category", "By category"),
        (col_class, "Lipid_class", "By class"),
        (col_subclass, "Lipid_subclass", "By subclass"),
    ]:
        with col:
            st.markdown(f"**{label}**")
            counts = df_valide[field].value_counts(dropna=False)
            for name, count in counts.items():
                display = str(name) if pd.notna(name) else "Unknown"
                st.caption(f"{display} - {count}")

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
    if st.session_state.pop("show_balloons", False):
        st.balloons()
else:
    st.info(f"Ready to integrate **{len(st.session_state['df_valide'])}** lipids into the database.")
    if st.button("Integrate data", type="primary", use_container_width=True):
        with st.spinner("Integrating data into the database..."):
            try:
                database_loading_MS1(st.session_state["df_valide"], confidence_level)
                st.session_state["integration_done"] = True
                st.session_state["show_balloons"] = True
                st.rerun()
            except Exception as e:
                st.error(f"Error during database integration : {e}")
                st.stop()
