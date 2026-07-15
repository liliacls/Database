import streamlit as st
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from datetime import datetime

from models.model import Annotation
from config import get_engine
from utils.msp_export import generate_msp as _generate_msp


@st.cache_data(ttl=60)
def generate_msp(
    _engine: Engine,
    categories: list[str | None],
    classes: list[str | None],
    sub_classes: list[str | None],
    mz_range: tuple[float, float],
) -> str:
    """Cached wrapper around utils.msp_export.generate_msp (see there for parameter details).

    Leading underscore on _engine so Streamlit does not attempt to hash it as a cache key.
    """
    return _generate_msp(_engine, categories, classes, sub_classes, mz_range)


@st.cache_data(ttl=60)
def load_data(_engine: Engine) -> pd.DataFrame:
    """Load and cache all annotations along with their associated Lipid and Detection data.

    :param _engine: SQLAlchemy engine connected to the database
    :type _engine: sqlalchemy.engine.Engine
    :return: DataFrame with columns name, formula, Lipid_category, Lipid_class, Lipid_subclass, mz, neutral_mass, MS_level, Ionisation_mode, Adduct, 
    RT, CCS and Num_Peaks (RT/CCS are None if not provided).
    :rtype: pandas.DataFrame
    """
    with Session(_engine) as session:
        results = (
            session.query(Annotation)
            .join(Annotation.lipid)
            .join(Annotation.detection)
            .all()
        )
        return pd.DataFrame(
            [
                {
                    "name": a.lipid.Lipid_name,
                    "formula": a.lipid.Formula,
                    "Lipid_category": a.lipid.Lipid_category,
                    "Lipid_class": a.lipid.Lipid_class,
                    "Lipid_subclass": a.lipid.Lipid_subclass,
                    "mz": a.detection.Precursor_MZ,
                    "neutral_mass": a.detection.Neutral_mass,
                    "MS_level": a.detection.MS_level,
                    "Ionisation_mode": a.detection.Ionisation_mode,
                    "Adduct": a.detection.Adduct,
                    "RT": a.detection.RT,
                    "CCS": a.detection.CCS,
                    "Num_Peaks": a.detection.Num_Peaks,
                }
                for a in results
            ]
        )


# ── Header ────────────────────────────────────────────────────────────────────

st.html("""
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
""")
st.write("")

with st.expander("ℹ️ How to use this page"):
    st.markdown("""
    This page lets you filter and export annotations from BacLipidDB.

    1. **Filters** - narrow down the data by lipid category/class/subclass, MS level,
       ionization mode and Precursor m/z. Leave a filter empty to include all values.
    2. **Preview** - check the filtered rows before exporting.
    3. **Download** - export the filtered data :
       - **CSV (MS1 + MS2)** - all filtered annotations, in the MS1 CSV format compatible
         with MZmine.
       - **MSP (MS2)** - annotations with fragment spectra, in `.msp` format. RT and CCS
         are included in the header of each entry when available.
       - **CSV (CCS + RT)** - annotations that have both an RT and a CCS value, with
         those columns included (only available when such rows exist). MZmine does not
         accept a CSV for MS1 annotation where some rows have CCS/RT values and others don't, so this
         export is kept separate from the plain CSV export above.
    """)

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
    selected_categories = st.multiselect(
        "Lipid category",
        options=categories,
        help="Leave empty to include all categories.",
    )

with col2:
    classes = sorted(df_all["Lipid_class"].dropna().unique().tolist())
    if df_all["Lipid_class"].isna().any():
        classes = ["(None)"] + classes
    selected_classes = st.multiselect(
        "Lipid class", options=classes, help="Leave empty to include all classes."
    )

with col3:
    sub_classes = sorted(df_all["Lipid_subclass"].dropna().unique().tolist())
    if df_all["Lipid_subclass"].isna().any():
        sub_classes = ["(None)"] + sub_classes
    selected_sub_classes = st.multiselect(
        "Lipid subclass",
        options=sub_classes,
        help="Leave empty to include all subclasses.",
    )

col4, col5, col6 = st.columns(3)

with col4:
    ms_levels = sorted(df_all["MS_level"].dropna().unique().tolist())
    selected_ms = st.multiselect("MS level", options=ms_levels)

with col5:
    ionisation_modes = sorted(df_all["Ionisation_mode"].dropna().unique().tolist())
    selected_ionisation_modes = st.multiselect(
        "Ionisation mode", options=ionisation_modes
    )

mz_min = float(df_all["mz"].min())
mz_max = float(df_all["mz"].max())

with col6:
    st.caption(
        "Precursor m/z range",
        help="Only annotations with Precursor_MZ within this range will be included in the export.",
    )
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        mz_min_input = st.number_input(
            "Min m/z",
            min_value=0.0,
            value=mz_min,
            step=0.01,
            format="%.6f",
        )
    with sub_col2:
        mz_max_input = st.number_input(
            "Max m/z",
            min_value=0.0,
            value=mz_max,
            step=0.01,
            format="%.6f",
        )

mz_range = (min(mz_min_input, mz_max_input), max(mz_min_input, mz_max_input))

st.divider()

# ── Apply filters ─────────────────────────────────────────────────────────────

df_filtered = df_all.copy()

if selected_categories:
    mask = df_filtered["Lipid_category"].isin(
        [c for c in selected_categories if c != "(None)"]
    )
    if "(None)" in selected_categories:
        mask |= df_filtered["Lipid_category"].isna()
    df_filtered = df_filtered[mask]

if selected_classes:
    mask = df_filtered["Lipid_class"].isin(
        [c for c in selected_classes if c != "(None)"]
    )
    if "(None)" in selected_classes:
        mask |= df_filtered["Lipid_class"].isna()
    df_filtered = df_filtered[mask]

if selected_sub_classes:
    mask = df_filtered["Lipid_subclass"].isin(
        [c for c in selected_sub_classes if c != "(None)"]
    )
    if "(None)" in selected_sub_classes:
        mask |= df_filtered["Lipid_subclass"].isna()
    df_filtered = df_filtered[mask]

if selected_ms:
    df_filtered = df_filtered[df_filtered["MS_level"].isin(selected_ms)]

if selected_ionisation_modes:
    df_filtered = df_filtered[
        df_filtered["Ionisation_mode"].isin(selected_ionisation_modes)
    ]

df_filtered = df_filtered[
    (df_filtered["mz"] >= mz_range[0]) & (df_filtered["mz"] <= mz_range[1])
]

# ── Preview ───────────────────────────────────────────────────────────────────

st.subheader(f"Preview - {len(df_filtered)} rows")

if df_filtered.empty:
    st.warning("No data matches the selected filters.", icon="⚠️")
    st.stop()

preview_columns = ["name", "formula", "mz", "MS_level", "RT", "CCS", "Num_Peaks"]
df_preview = df_filtered[preview_columns].copy().reset_index(drop=True)
st.dataframe(
    df_preview,
    height=400,
    column_config={
        "mz": st.column_config.NumberColumn(format="%.6f"),
    },
)

# ── Download ──────────────────────────────────────────────────────────────────

st.divider()

ms2 = (df_filtered["MS_level"] == "MS2").any()
rt_ccs = (df_filtered["RT"].notna() & df_filtered["CCS"].notna()).any()

col_1, col_2, col_3 = st.columns(3)

with col_1:
    df_export_all = df_filtered[
        ["neutral_mass", "mz", "formula", "name"]
    ].reset_index(drop=True)
    csv_all = df_export_all.to_csv(index=False, lineterminator="\r\n")
    st.download_button(
        label="Download CSV (MS1 + MS2)",
        data=csv_all,
        file_name=f"annotation_export_MS1+MS2_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        type="primary",
        width="stretch",
    )

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
            file_name=f"annotation_export_MS2_{datetime.now().strftime('%Y%m%d')}.msp",
            mime="text/plain",
            type="primary",
            width="stretch",
        )
    else:
        st.button("Download MSP (MS2)", disabled=True, width="stretch")

with col_3:
    if rt_ccs:
        df_export_rt_ccs = df_filtered[
            df_filtered["RT"].notna() & df_filtered["CCS"].notna()
        ][["neutral_mass", "mz", "formula", "name", "RT", "CCS"]].reset_index(
            drop=True
        )
        csv_rt_ccs = df_export_rt_ccs.to_csv(index=False, lineterminator="\r\n")
        st.download_button(
            label="Download CSV (CCS + RT)",
            data=csv_rt_ccs,
            file_name=f"annotation_export_CCS_RT_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="primary",
            width="stretch",
        )
    else:
        st.button("Download CSV (CCS + RT)", disabled=True, width="stretch")
