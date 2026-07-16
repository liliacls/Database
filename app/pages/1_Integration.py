import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loading_MS1 import DB_MS1
from utils.loading_MS2 import ms2_parsing, DB_MS2
from utils.molecular_weight import molecular_weight
from utils.monoisotopic import monoisotopic_mass
from utils.neutral_mass import neutral_mass, adduct

# ── Constants ────────────────────────────────────────────────────────────────────

# Required columns in MS1 file
REQUIRED_COLUMNS = ["Lipid_Name", "Formula", "Precursor_MZ", "Lipid_category", "Lipid_class", "Lipid_subclass", "Adduct"]

# Columns that must not contain empty values
NON_EMPTY_COLUMNS = ["Lipid_Name", "Formula", "Precursor_MZ", "Adduct"]

CHART_COLOR_SCALE = [[0, "#4292C6"], [1, "#08306B"]]
COLOR = "#1F77B4"

# session_state keys
MS1 = "ms1"
MS2 = "ms2"
COLUMNS_VALID = "columns_valid"
DF_VALID = "df_validated"
INTEGRATION_DONE = "integration_done"
DF_COMPLETE = "df_complete"
DF_ID = "df_file_id"
DF_MS_LEVEL = "df_ms_level"
EDITOR = "editor_integration"
UPLOADER_VERSION = "uploader_version"

# Full reset (sidebar button): clears everything
RESET_KEYS = [MS1, MS2, DF_ID, DF_MS_LEVEL, DF_COMPLETE, DF_VALID, INTEGRATION_DONE, COLUMNS_VALID, EDITOR]

# Reset on new file upload only: keeps step 1 settings and the file itself, but clears everything computed downstream
RELOAD_RESET_KEYS = [DF_COMPLETE, DF_VALID, INTEGRATION_DONE, COLUMNS_VALID, EDITOR]


def _adducts(records):
    """Resolve the adduct and neutral mass for a batch of (label, lipid_name, precursor_mz, raw_adduct) records.

    :param records: iterable of (label, lipid_name, precursor_mz, raw_adduct) tuples
    :return: (adducts, masses, error_messages) lists, aligned with records ; failed entries resolve to None
    :rtype: tuple[list, list, list[str]]
    """
    adducts, masses, errors = [], [], []
    for label, lipid_name, precursor_mz, raw_adduct in records:
        try:
            resolved_adduct = adduct(raw_adduct)
            mass = neutral_mass(precursor_mz, resolved_adduct)
        except ValueError as e:
            errors.append(f"{label} ({lipid_name}) : {e}")
            resolved_adduct, mass = None, None
        adducts.append(resolved_adduct)
        masses.append(mass)
    return adducts, masses, errors


# ── Sidebar ────────────────────────────────────────────────────────────────────

def _workflow(done):
    return "✅" if done else "⬜"

step1_done = all(st.session_state.get(k) not in (None, "") for k in ["ms_level", "ion_mode", "integrator_name", "file_row_name"])

with st.sidebar:
    st.markdown("### Workflow")
    st.markdown(f"{_workflow(step1_done)} Step 1 - Settings")
    st.markdown(f"{_workflow(MS1 in st.session_state or MS2 in st.session_state)} Step 2 - File upload")
    st.markdown(f"{_workflow(st.session_state.get('columns_valid', False))} Step 3 - Verification")
    st.markdown(f"{_workflow(DF_VALID in st.session_state)} Step 4 - Completion & Validation")
    st.markdown(f"{_workflow(st.session_state.get('integration_done', False))} Step 5 - Integration")
    st.divider()
    if st.button("Reset 🔄", type="secondary", width="stretch"):
        for key in RESET_KEYS:
            st.session_state.pop(key, None)
        st.session_state["ms_level"] = None
        st.session_state["ion_mode"] = None
        st.session_state["integrator_name"] = ""
        st.session_state["file_row_name"] = ""
        st.session_state[UPLOADER_VERSION] = st.session_state.get(UPLOADER_VERSION, 0) + 1
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────

st.html(f"""
    <style>
    .module {{
        border: 2px solid {COLOR};
        border-radius: 10px;
        text-align: center;
    }}
    </style>
    <div class="module">
        <h1><span style="color:{COLOR}">MODULE 1</span> : Data integration page</h1>
    </div>
""")

# ── Progress bar ────────────────────────────────────────────────────────────────────

steps_status = [
    step1_done,
    MS1 in st.session_state or MS2 in st.session_state,
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

    1. **Settings** - choose the MS level, ionization mode, your name and the file row name for this integration.
    2. **File upload** - upload a `.csv`, `.tsv` or `.xlsx` file for MS1 or MS2 annotations.
    3. **Verification** - the app checks that the file matches the expected format (see **Resources** page).
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
        options=["MS1", "MS2"],
        index=None,
        key="ms_level",
        disabled=settings_locked,
        help="MS1 for precursor-only annotations, MS2 for annotations with fragment spectra.",
    )

with col2:
    ion_mode = st.selectbox(
        "Ionization mode",
        options=["Positive", "Negative"],
        index=None,
        key="ion_mode",
        disabled=settings_locked,
        help="Ionization mode used during acquisition. Only used to fill the Ionisation_mode column in the database, it does not affect which adduct is used or how the neutral mass is computed."
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
        help="Name of the row file experiment who provided annotations",
    )

if None in [ms_level, ion_mode] or not integrator_name or not file_row_name:
    st.warning("Please fill in all parameters before continuing.", icon="⚠️")
    st.stop()

st.success(f"Selected : {ms_level} | {ion_mode} | Integrator : {integrator_name}", icon="✅")

# ── STEP 2 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 2] - File upload", divider="blue", text_alignment="left")

uploaded_file = st.file_uploader(
    "Choose an annotation file",
    type=["csv", "tsv", "xlsx"],
    key=f"file_uploader_{st.session_state.get(UPLOADER_VERSION, 0)}",
)

if uploaded_file is None:
    st.stop()

try:
    if (
        st.session_state.get(DF_ID) != uploaded_file.file_id
        or st.session_state.get(DF_MS_LEVEL) != ms_level
    ):

        if ms_level == "MS2":
            new_value = ms2_parsing(uploaded_file)

        elif uploaded_file.name.endswith(".csv"):
            new_value = pd.read_csv(uploaded_file)

        elif uploaded_file.name.endswith(".tsv"):
            new_value = pd.read_csv(uploaded_file, sep="\t")
        else:
            new_value = pd.read_excel(uploaded_file)

        for key in RELOAD_RESET_KEYS:
            st.session_state.pop(key, None)
        st.session_state.pop(MS1 if ms_level == "MS2" else MS2, None)

        st.session_state[MS2 if ms_level == "MS2" else MS1] = new_value
        st.session_state[DF_ID] = uploaded_file.file_id
        st.session_state[DF_MS_LEVEL] = ms_level
        st.rerun()

    if ms_level == "MS2":
        st.success(f"File loaded : {uploaded_file.name} - {len(st.session_state[MS2])} scans detected.", icon="✅")
    else:
        st.success(f"File loaded : {uploaded_file.name} - {len(st.session_state[MS1])} rows detected.", icon="✅")

except Exception as e:
    st.error(f"Error loading file : {e}")
    st.stop()

if ms_level != "MS2":
    df = st.session_state[MS1].copy()

# ── STEP 3 ────────────────────────────────────────────────────────────────────

st.header(":blue[STEP 3] - Required columns verification", divider="blue", text_alignment="left")

if ms_level == "MS2":
    ms2 = st.session_state[MS2]

    if not st.session_state.get(COLUMNS_VALID, False):
        st.session_state[COLUMNS_VALID] = True
        st.rerun()
    st.success(f"{len(ms2)} scan(s) parsed successfully", icon="✅")

    preview = pd.DataFrame(
        [
            {
                "Precursor_MZ": m["precursor_mz"],
                "Formula": m["formula"],
                "Lipid_Name": m["lipid_name"],
                "FA_composition": m["fa_composition"],
                "Adduct": m["adduct"],
                "Lipid_category": m["lipid_category"],
                "Lipid_class": m["lipid_class"],
                "Lipid_subclass": m["lipid_subclass"],
                "RT": m["rt"],
                "CCS": m["ccs"],
                "Num_Peaks": m["num_peaks"],
            }
            for m in ms2
        ]
    )

    with st.expander("Preview scan data", expanded=True):
        st.dataframe(preview, width="stretch", column_config={
            "Precursor_MZ": st.column_config.NumberColumn(format="%.6f"),
        })

else:
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
        invalid_precursor = df.index[numeric_precursor.isnull()].tolist()
        if invalid_precursor:
            st.error(
                f"The column **Precursor_MZ** must contain only numeric values. "
                f"Non-numeric value(s) found at row(s) : "
                f"{', '.join(str(i) for i in invalid_precursor)}\n\n"
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

            if ms_level == "MS2":
                rows = []
                for data in ms2:
                    rows.append(
                        {
                            "Lipid_Name": data["lipid_name"],
                            "Formula": data["formula"],
                            "Precursor_MZ": data["precursor_mz"],
                            "FA_composition": data["fa_composition"],
                            "Num_Peaks": data["num_peaks"],
                            "Molecular_weight": molecular_weight(data["formula"]),
                            "Monoisotopic_mass": monoisotopic_mass(data["formula"]),
                            "MS_level": ms_level,
                            "Ionisation_mode": ion_mode,
                            "Lipid_category": data["lipid_category"],
                            "Lipid_class": data["lipid_class"],
                            "Lipid_subclass": data["lipid_subclass"],
                            "RT": data["rt"],
                            "CCS": data["ccs"],
                        }
                    )
                df = pd.DataFrame(rows)

                invalid_formulas = df.loc[df["Molecular_weight"].isna(), "Formula"].tolist()
                if invalid_formulas:
                    st.error(
                        f"Cannot compute molecular weight for the following formula(s) : "
                        f"**{', '.join(str(f) for f in invalid_formulas)}**\n\n"
                        f"Please correct these formulas in your file and reload it."
                    )
                    st.stop()

                adducts, n_mass, e_adduct = _adducts(
                    (f"Scan {data['scan_id']}", data["lipid_name"], data["precursor_mz"], data.get("adduct"))
                    for data in ms2
                )

                if e_adduct:
                    st.error(
                        "Could not resolve the precursor adduct for the following scan(s) :\n\n"
                        + "\n".join(f"- {msg}" for msg in e_adduct)
                        + "\n\nPlease correct the Adduct field for these scans and reload the file."
                    )
                    st.stop()

                df["Adduct"] = adducts
                df["Neutral_mass"] = n_mass

            else:
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

                adducts, neutral_masses, e_adduct = _adducts(
                    (f"Row {idx}", row["Lipid_Name"], row["Precursor_MZ"], row.get("Adduct"))
                    for idx, row in df.iterrows()
                )

                if e_adduct:
                    st.error(
                        "Could not resolve the precursor adduct for the following row(s) :\n\n"
                        + "\n".join(f"- {msg}" for msg in e_adduct)
                        + "\n\nPlease correct the Adduct column for these rows and reload the file."
                    )
                    st.stop()

                df["Adduct"] = adducts
                df["Neutral_mass"] = neutral_masses

                df["MS_level"] = ms_level
                df["Num_Peaks"] = 0
                df["Ionisation_mode"] = ion_mode

        st.session_state[DF_COMPLETE] = df
        st.rerun()

if DF_COMPLETE not in st.session_state:
    st.stop()

st.caption(f"Settings : {ms_level} | {ion_mode}")

if ms_level == "MS2":
    editor_num_rows = "fixed"
    # These columns are computed automatically from Formula/Precursor_MZ and settings, disabling edition keeps them consistent with the values they were derived from.
    column_config = {
        "Precursor_MZ":      st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Neutral_mass":      st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Molecular_weight":  st.column_config.NumberColumn(format="%.0f", disabled=True),
        "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Formula":           st.column_config.TextColumn(disabled=True),
        "MS_level":          st.column_config.TextColumn(disabled=True),
        "Num_Peaks":         st.column_config.NumberColumn(disabled=True),
        "Ionisation_mode":   st.column_config.TextColumn(disabled=True),
        "Adduct":            st.column_config.TextColumn(disabled=True),
        "Scan_id":           st.column_config.TextColumn(disabled=True),
    }
else:
    editor_num_rows = "dynamic"
    # These columns are computed automatically from Formula/Precursor_MZ and settings, disabling edition keeps them consistent with the values they were derived from.
    column_config = {
        "Precursor_MZ":     st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Neutral_mass":     st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Molecular_weight": st.column_config.NumberColumn(format="%.0f", disabled=True),
        "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f", disabled=True),
        "Formula":          st.column_config.TextColumn(disabled=True),
        "MS_level":         st.column_config.TextColumn(disabled=True),
        "Num_Peaks":        st.column_config.NumberColumn(disabled=True),
        "Ionisation_mode":  st.column_config.TextColumn(disabled=True),
        "Adduct":           st.column_config.TextColumn(disabled=True),
    }

df_edited = st.data_editor(
    st.session_state[DF_COMPLETE],
    width="stretch",
    num_rows=editor_num_rows,
    key="editor_integration",
    column_config=column_config,
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
                if ms_level == "MS2":

                    validated_df = st.session_state[DF_VALID]
                    scans = st.session_state[MS2]
                    for pos, row in enumerate(validated_df.to_dict("records")):
                        scan = scans[pos]
                        scan["lipid_name"] = row["Lipid_Name"]
                        scan["fa_composition"] = row["FA_composition"] if pd.notna(row["FA_composition"]) else None
                        scan["lipid_category"] = row["Lipid_category"] if pd.notna(row["Lipid_category"]) else None
                        scan["lipid_class"] = row["Lipid_class"] if pd.notna(row["Lipid_class"]) else None
                        scan["lipid_subclass"] = row["Lipid_subclass"] if pd.notna(row["Lipid_subclass"]) else None
                        scan["rt"] = row["RT"] if pd.notna(row["RT"]) else None
                        scan["ccs"] = row["CCS"] if pd.notna(row["CCS"]) else None
                        scan["molecular_weight"] = row["Molecular_weight"]
                        scan["monoisotopic_mass"] = row["Monoisotopic_mass"]
                        scan["neutral_mass"] = row["Neutral_mass"]
                        scan["adduct"] = row["Adduct"]
                        scan["ion_mode"] = row["Ionisation_mode"]

                    DB_MS2(
                        scans,
                        uploaded_file.name,
                        integrator_name,
                        file_row_name,
                    )
                else:
                    DB_MS1(
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
