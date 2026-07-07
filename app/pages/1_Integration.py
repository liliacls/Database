import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loading_MS1 import database_loading_MS1
from utils.molecular_weight import molecular_weight
from utils.monoisotopic import monoisotopic_mass
from utils.neutral_mass import neutral_mass

# ── Constants ────────────────────────────────────────────────────────────────────

# Required columns in MS1 file
REQUIRED_COLUMNS = ["Lipid_Name", "Formula", "Precursor_MZ", "Lipid_category", "Lipid_class", "Lipid_subclass"]

# Columns that must not contain empty values
NON_EMPTY_COLUMNS = ["Lipid_Name", "Formula", "Precursor_MZ"]

CHART_COLOR_SCALE = [[0, "#4292C6"], [1, "#08306B"]]
COLOR = "#1F77B4"

# session_state keys
DF = "df"
COLUMNS_VALID = "columns_valid"
DF_VALID = "df_validated"
INTEGRATION_DONE = "integration_done"
DF_COMPLETE = "df_complete"
DF_ID = "df_file_id"
EDITOR = "editor_integration"

# Full reset (sidebar button): clears everything
RESET_KEYS = [DF, DF_ID, DF_COMPLETE, DF_VALID, INTEGRATION_DONE, COLUMNS_VALID, EDITOR]

# Reset on new file upload only: keeps step 1 settings and the file itself, but clears everything computed downstream
RELOAD_RESET_KEYS = [DF_COMPLETE, DF_VALID, INTEGRATION_DONE, COLUMNS_VALID, EDITOR]

# ── Sidebar ────────────────────────────────────────────────────────────────────

def _icon(done):
    return "✅" if done else "⬜"

step1_done = all(st.session_state.get(k) not in (None, "") for k in ["ms_level", "ion_mode", "integrator_name"])

with st.sidebar:
    st.markdown("### Workflow")
    st.markdown(f"{_icon(step1_done)} Step 1 - Settings")
    st.markdown(f"{_icon(DF in st.session_state)} Step 2 - File upload")
    st.markdown(f"{_icon(st.session_state.get('columns_valid', False))} Step 3 - Verification")
    st.markdown(f"{_icon(DF_VALID in st.session_state)} Step 4 - Completion & Validation")
    st.markdown(f"{_icon(st.session_state.get('integration_done', False))} Step 5 - Integration")
    st.divider()
    if st.button("Reset 🔄", type="secondary", width="stretch"):
        for key in RESET_KEYS:
            st.session_state.pop(key, None)
        st.session_state["ms_level"] = None
        st.session_state["ion_mode"] = None
        st.session_state["confidence_level"] = None
        st.session_state["integrator_name"] = ""
        st.session_state["file_uploader"] = None
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────

st.html("""
    <style>
    .module {
        border: 2px solid {COLOR};
        border-radius: 10px;
        text-align: center;
    }
    </style>
    <div class="module">
        <h1><span style="color:{COLOR}">MODULE 1</span> : Data integration page</h1>
    </div>
""")

# ── Progress bar ────────────────────────────────────────────────────────────────────

steps_status = [
    step1_done,
    "df" in st.session_state,
    st.session_state.get("columns_valid", False),
    DF_VALID in st.session_state,
    st.session_state.get("integration_done", False),
]
completed_step = sum(steps_status)

st.progress(completed_step / len(steps_status), text=f"Step {completed_step} / {len(steps_status)} completed")

# ── Info ────────────────────────────────────────────────────────────────────

with st.expander("ℹ️ How to use this page"):
    st.markdown("""
    This page integrates a lipid annotation file into BacLipidDB in 5 steps :

    1. **Settings** - choose the MS level, ionization mode, confidence level and your name for this integration.
    2. **File upload** - upload a `.csv`, `.tsv` or `.xlsx` file.
    3. **Verification** - the app checks that all required columns are present (see **Resources** page for the expected format).
    4. **Completion** - derived columns are computed automatically, you can then edit and validate the table.
    5. **Integration** - the validated data is inserted into the BacLipidDB.

    """)

# ── STEP 1 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 1] - Settings", divider="blue", text_alignment="left")

col1, col2, col3, col4 = st.columns(4)

# Once automatic completion (step 4) has run, step 1's parameters are locked to ensure consistency between the derived columns and the settings they were computed from.
settings_locked = DF_COMPLETE in st.session_state

with col1:
    ms_level = st.selectbox(
        "Annotation level",
        options=["MS1"],
        index=None,
        key="ms_level",
        disabled=settings_locked,
        help="MS1 for precursor-only annotations",
    )

with col2:
    ion_mode = st.selectbox(
        "Ionization mode",
        options=["Positive", "Negative"],
        index=None,
        key="ion_mode",
        disabled=settings_locked,
        help="Ionization mode used during acquisition : determines how the neutral mass is calculated from Precursor_MZ.",
    )

with col3:
    integrator_name = st.text_input(
        "Your name",
        key="integrator_name",
        disabled=settings_locked,
        help="Name of the person integrating this batch, recorded in the import history.",
    )

with col4:
    file_row_name = st.text_input(
        "File row name",
        key="file_row_name",
        disabled=settings_locked,
        help="Name of the file who provided annotations",
    )


if None in [ms_level, ion_mode] or not integrator_name:
    st.warning("Please fill in all parameters before continuing.", icon="⚠️")
    st.stop()

st.success(f"Selected : {ms_level} | {ion_mode} | Integrator : {integrator_name}", icon="✅")

# ── STEP 2 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 2] - File upload", divider="blue", text_alignment="left")

uploaded_file = st.file_uploader(
    "Choose an annotation file",
    type=["csv", "xlsx", "tsv"],
    key="file_uploader",
)

if uploaded_file is None:
    st.stop()

try:
    if st.session_state.get(DF_ID) != uploaded_file.file_id:

        if uploaded_file.name.endswith(".csv"):
            df_new = pd.read_csv(uploaded_file)

        elif uploaded_file.name.endswith(".tsv"):
            df_new = pd.read_csv(uploaded_file, sep="\t")

        else:
            df_new = pd.read_excel(uploaded_file)

        for key in RELOAD_RESET_KEYS:
            st.session_state.pop(key, None)

        st.session_state[DF] = df_new
        st.session_state[DF_ID] = uploaded_file.file_id
        st.rerun()

    st.success(f"File loaded : {uploaded_file.name} - {len(st.session_state[DF])} rows detected.", icon="✅")

except Exception as e:
    st.error(f"Error loading file : {e}")
    st.stop()

df = st.session_state[DF].copy()

# ── STEP 3 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 3] - Required columns verification", divider="blue", text_alignment="left")

missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
    st.error(
        f"The file is missing the following required columns : "
        f"**{', '.join(missing_columns)}**\n\n"
        f"Please correct your file and reload it."
    )
    st.stop()
else:
    if not st.session_state.get(COLUMNS_VALID, False):
        st.session_state[COLUMNS_VALID] = True
        st.rerun()
    st.success("All required columns found", icon="✅")

    required = NON_EMPTY_COLUMNS
    empty_columns = [c for c in required if df[c].isnull().any()]
    if empty_columns:
        st.error(
            f"The file contains empty cells in required columns : "
            f"**{', '.join(empty_columns)}**\n\n"
            f"Please correct your file and reload it."
        )
        st.stop()

    numeric_precursor = pd.to_numeric(df["Precursor_MZ"], errors="coerce")
    invalid_precursor_rows = df.index[numeric_precursor.isnull()].tolist()
    if invalid_precursor_rows:
        st.error(
            f"The column **Precursor_MZ** must contain only numeric values. "
            f"Non-numeric value(s) found at row(s) : "
            f"{', '.join(str(i) for i in invalid_precursor_rows)}\n\n"
            f"Please correct your file and reload it."
        )
        st.stop()
    df["Precursor_MZ"] = numeric_precursor.astype(float)

    with st.expander("Preview raw data", expanded=True):
        st.dataframe(df, width="stretch", column_config={
            "Precursor_MZ": st.column_config.NumberColumn(format="%.6f"),
        })

# ── STEP 4 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 4] - Preview and automatic completion", divider="blue", text_alignment="left")

if DF_COMPLETE not in st.session_state:
    if st.button("Run automatic completion", type="primary", width="stretch"):
        with st.spinner("Computing derived columns..."):
            try:
                df["Neutral_mass"] = df["Precursor_MZ"].apply(
                    lambda mz: neutral_mass(mz, ion_mode)
                )
            except Exception as e:
                st.error(f"Error calculating neutral mass : {e}")
                st.stop()

            df["Molecular_weight"] = df["Formula"].apply(molecular_weight)
            df["Monoisotopic_mass"] = df["Formula"].apply(monoisotopic_mass)
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
            df["Ionisation_mode"] = ion_mode

        st.session_state[DF_COMPLETE] = df
        st.rerun()

if DF_COMPLETE not in st.session_state:
    st.stop()

st.caption(f"Settings : {ms_level} | {ion_mode}")
df_edited = st.data_editor(
    st.session_state[DF_COMPLETE],
    width="stretch",
    num_rows="dynamic",
    key="editor_integration",

    # These columns are computed automatically from Formula/Precursor_MZ and settings, disabling edition keeps them consistent with the values they were derived from.
    column_config={
        "Precursor_MZ":     st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Neutral_mass":     st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Molecular_weight": st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Formula":          st.column_config.TextColumn(disabled=True),
        "MS_level":         st.column_config.TextColumn(disabled=True),
        "Num_Peaks":        st.column_config.NumberColumn(disabled=True),
        "Ionisation_mode":  st.column_config.TextColumn(disabled=True),
    },
)

if st.button("Validate data", type="primary", width="stretch"):
    empty_columns = [c for c in NON_EMPTY_COLUMNS if df_edited[c].isnull().any()]
    if empty_columns:
        st.warning(
            f"The table contains empty cells in required columns : **{', '.join(empty_columns)}**",
            icon="⚠️",
        )
    else:
        st.session_state[DF_VALID] = df_edited
        st.rerun()

if DF_VALID in st.session_state:
    st.subheader("Summary")

    df_validated = st.session_state[DF_VALID]
    total = len(df_validated)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total lipids", total)
    m2.metric("Categories", df_validated["Lipid_category"].nunique())
    m3.metric("Classes", df_validated["Lipid_class"].nunique())
    m4.metric("Subclasses", df_validated["Lipid_subclass"].nunique())

    st.markdown("")
    col_cat, col_class, col_subclass = st.columns(3)

    for col, field, label in [
        (col_cat, "Lipid_category", "By category"),
        (col_class, "Lipid_class", "By class"),
        (col_subclass, "Lipid_subclass", "By subclass"),
    ]:
        counts = df_validated[field].value_counts(dropna=False).reset_index()
        counts.columns = [field, "Count"]
        counts[field] = counts[field].fillna("Unknown").astype(str)
        fig = px.bar(
            counts,
            x="Count",
            y=field,
            orientation="h",
            title=label,
            color="Count",
            color_continuous_scale=CHART_COLOR_SCALE,
            text="Count",
        )
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=10, t=40, b=0),
            yaxis_title=None,
            xaxis_title=None,
            height=max(180, len(counts) * 36 + 60),
            title_font_size=14,
        )
        fig.update_traces(textposition="outside")
        fig.update_yaxes(tickfont=dict(color="black"))
        fig.update_xaxes(tickfont=dict(color="black"))
        with col:
            st.plotly_chart(fig, width='stretch')

# ── STEP 5 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 5] - Database integration", divider="blue", text_alignment="left")

if DF_VALID not in st.session_state:
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
    st.info(f"Ready to integrate **{len(st.session_state[DF_VALID])}** lipids into the database.")
    if st.button("Integrate data", type="primary", width="stretch"):
        with st.spinner("Integrating data into the database..."):
            try:
                # Use the function in loading_MS1.py to insert the data into the database
                database_loading_MS1(
                    st.session_state[DF_VALID],
                    uploaded_file.name,
                    integrator_name,
                    file_row_name,
                )
                st.session_state["integration_done"] = True
                st.session_state["show_balloons"] = True
                st.rerun()
            except Exception as e:
                st.error(f"Error during database integration : {e}")
                st.stop()