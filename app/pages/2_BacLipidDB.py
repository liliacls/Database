import json
import logging
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session, joinedload

from models.model import Annotation
from config import get_engine, HISTORY_PATH, PROJECT_ROOT

logger = logging.getLogger(__name__)

# Distinct pastel colors used to tag "Full view" rows by import batch
PALETTE = [
    "#FFB3B3", "#FFD9B3", "#FFFCB3", "#D4FFB3", "#B3FFD1",
    "#B3FFF6", "#B3E0FF", "#B3C2FF", "#D4B3FF", "#FFB3F0",
    "#FF8080", "#FFBE80", "#FFF980", "#AAFF80", "#80FFC0",
    "#80FFF2", "#80CCFF", "#809FFF", "#BE80FF", "#FF80E8",
    "#FFCCD5", "#FFE8CC", "#FFFBCC", "#DFFFCC", "#CCFFE8",
    "#CCFFFB", "#CCE8FF", "#CCD5FF", "#DFCCFF", "#FFCCF9",
    "#E8A0A0", "#E8C4A0", "#E8E7A0", "#C5E8A0", "#A0E8BE",
    "#A0E8E3", "#A0CBE8", "#A0AEE8", "#C5A0E8", "#E8A0DC",
    "#FFC4A0", "#E8D5A0", "#D5E8A0", "#A0D5E8", "#A0B8E8",
    "#D5A0E8", "#E8A0C4", "#C4E8A0", "#A0E8C4", "#E8C4D5",
]

logo_path = PROJECT_ROOT / "assets" / "DB.svg"

_, col_center, _ = st.columns([1, 1, 1])
with col_center:
    if logo_path.exists():
        st.image(str(logo_path), width="stretch")

st.html("""
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
""")
st.write("")

with st.expander("ℹ️ How to use this page"):
    st.markdown("""
    This page lets you explore the content of BacLipidDB.

    - **Annotation / Detection / Fragment / Lipid** - view the raw content of each individual table.
    - **Full view** - a joined view combining Detection, Lipid and Annotation. Rows are colored by import batch.
    - **History** - the list of past imports (filename, date, MS level, ionization mode, number of rows, submitted by).""")

engine = get_engine()

table = st.radio(
    "Select a table",
    options=["Annotation", "Detection", "Fragment", "Lipid", "Full view", "History"],
    horizontal=True,
    key="table_select",
)

st.divider()


def _load_history() -> list[dict]:
    """Load the import history from history.json.

    :return: list of import records, or an empty list if the file does not exist or is empty.
    :rtype: list[dict]
    """
    if not HISTORY_PATH.exists():
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []


def _formula(formula: str) -> dict:
    """Parse a chemical formula into a dict of element symbol -> atom count.

    :param formula: chemical formula, e.g. "C40H80NO8P".
    :type formula: str
    :return: mapping of element symbol to atom count.
    :rtype: dict
    """
    counts = {}
    for element, num in re.findall(r'([A-Z][a-z]?)(\d*)', str(formula)):
        if element:
            counts[element] = counts.get(element, 0) + (int(num) if num else 1)
    return counts


def _detection_batch_map(history: list[dict]) -> dict[int, int]:
    """Map each Detection_ID to the index of the import batch it belongs to.

    Used to color-code "Full view" rows by import batch (see PALETTE).

    :param history: import history, as returned by _load_history().
    :type history: list[dict]
    :return: mapping of Detection_ID to batch index.
    :rtype: dict[int, int]
    """
    mapping = {}
    for batch_id, entry in enumerate(history):
        for detection_id in entry.get("detection_ids", []):
            mapping[detection_id] = batch_id
    return mapping


try:
    if table == "History":

        # Function to load the import history from history.json and display it in a table
        history = _load_history()
        if not history:
            st.info("No imports recorded yet.")
        else:
            df_hist = pd.DataFrame([
                {
                    "Filename":         e.get("filename", "-"),
                    "Date":             pd.to_datetime(e.get("inserted")),
                    "MS level":         e.get("ms_level"),
                    "Ionisation mode":  e.get("ionisation_mode"),
                    "Rows inserted":    str(e.get("num_rows", "-")),
                    "Submitted by":     e.get("integrator") or "-",
                }
                for e in history
            ])
            st.subheader("History")
            st.dataframe(df_hist, width='stretch')

    elif table == "Full view":
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
                    "Detection_ID":      a.detection.Detection_ID,
                    "Lipid_name":        a.lipid.Lipid_name,
                    "Formula":           a.lipid.Formula,
                    "Lipid_class":       a.lipid.Lipid_class,
                    "Lipid_subclass":    a.lipid.Lipid_subclass,
                    "Lipid_category":    a.lipid.Lipid_category,
                    "Precursor_MZ":      a.detection.Precursor_MZ,
                    "Neutral_mass":      a.detection.Neutral_mass,
                    "Molecular_weight":  a.lipid.Molecular_weight,
                    "Monoisotopic_mass": a.lipid.Monoisotopic_mass,
                    "MS_level":          a.detection.MS_level,
                    "Ionisation_mode":   a.detection.Ionisation_mode,
                    "Num_Peaks":         a.detection.Num_Peaks,
                    "RT":                a.detection.RT,
                    "CCS":               a.detection.CCS,
                    "Confidence_level":  a.Confidence_level,
                }
                for a in results
            ])

        st.subheader(f"Table : Full view - {len(df)} rows")
        if df.empty:
            st.info("This table contains no data yet.")
        else:
            history = _load_history()
            id_caption = _detection_batch_map(history)
            df = df.reset_index(drop=True)
            caption_values = df["Detection_ID"].map(id_caption).values

            columns = {
                "Precursor_MZ":      st.column_config.NumberColumn(format="%.6f"),
                "Neutral_mass":      st.column_config.NumberColumn(format="%.6f"),
                "Molecular_weight":  st.column_config.NumberColumn(format="%.6f"),
                "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f"),
                "RT":                st.column_config.NumberColumn(format="%.4f"),
                "CCS":               st.column_config.NumberColumn(format="%.4f"),
            }

            def color(row):
                caption = caption_values[row.name]
                if pd.isna(caption):
                    return [""] * len(row)
                batch_color = PALETTE[int(caption) % len(PALETTE)]
                return [f"background-color: {batch_color}"] * len(row)

            styled = df.style.apply(color, axis=1)
            st.dataframe(styled, column_config=columns, width='stretch')

            if history:
                with st.expander("color caption"):
                    for i, entry in enumerate(history):
                        batch_color = PALETTE[i % len(PALETTE)]
                        submitted_by = entry.get("integrator")
                        by_suffix = f", by {submitted_by}" if submitted_by else ""
                        st.markdown(
                            f'<span style="background-color:{batch_color};padding:2px 12px;border-radius:4px;">'
                            f'&nbsp;</span>&nbsp; **File {i + 1}** - {entry.get("filename", "-")} '
                            f'({entry.get("inserted", "")}, {entry.get("num_rows", "-")} rows{by_suffix})',
                            unsafe_allow_html=True,
                        )

            # ── Graphique 1 : Molecular weight vs Neutral mass ─────────────────
            df_plot = df.dropna(subset=["Neutral_mass", "Monoisotopic_mass"]).copy()

            st.subheader("Measured neutral mass vs. theoretical monoisotopic mass (Da)")
            if df_plot.empty:
                st.info("No rows with both Neutral_mass and Monoisotopic_mass to plot.")
            else:
                df_plot["Delta (Da)"] = df_plot["Neutral_mass"] - df_plot["Monoisotopic_mass"]
                df_plot["Error (ppm)"] = (df_plot["Delta (Da)"] / df_plot["Monoisotopic_mass"]) * 1e6

                fig_scatter = px.scatter(
                    df_plot,
                    x="Monoisotopic_mass",
                    y="Neutral_mass",
                    color="Lipid_class",
                    hover_data=["Lipid_name", "Delta (Da)", "Error (ppm)"],
                    labels={
                        "Monoisotopic_mass": "Monoisotopic mass (Da)",
                        "Neutral_mass": "Precursor neutral mass (Da)",
                    },
                )

                min_val = min(df_plot["Monoisotopic_mass"].min(), df_plot["Neutral_mass"].min())
                max_val = max(df_plot["Monoisotopic_mass"].max(), df_plot["Neutral_mass"].max())

                fig_scatter.add_trace(go.Scatter(
                    x=[min_val, max_val], y=[min_val, max_val],
                    mode="lines", name="y = x",
                    line=dict(dash="dash", color="gray"),
                ))
                fig_scatter.update_xaxes(showline=True, linecolor="black", tickcolor="black", tickfont_color="black", title_font_color="black")
                fig_scatter.update_yaxes(showline=True, linecolor="black", tickcolor="black", tickfont_color="black", title_font_color="black")
                fig_scatter.update_layout(
                    height=650,
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01,
                                bgcolor="rgba(255,255,255,0.8)", bordercolor="lightgray", borderwidth=1,
                                font=dict(color="black")),
                    hoverlabel=dict(font=dict(color="black")),
                )
                _, col, _ = st.columns([1, 18, 1])
                with col:
                    st.plotly_chart(fig_scatter, width='stretch')


            # ── Graphique 2 : Van Krevelen (H/C vs O/C) ────────────────────────
            df_vk = df.dropna(subset=["Formula"]).copy()
            df_vk["_atoms"] = df_vk["Formula"].apply(_formula)
            df_vk["C"] = df_vk["_atoms"].apply(lambda d: d.get("C", 0))
            df_vk["H"] = df_vk["_atoms"].apply(lambda d: d.get("H", 0))
            df_vk["O"] = df_vk["_atoms"].apply(lambda d: d.get("O", 0))
            df_vk = df_vk[df_vk["C"] > 0].copy()
            df_vk["H/C"] = df_vk["H"] / df_vk["C"]
            df_vk["O/C"] = df_vk["O"] / df_vk["C"]

            st.subheader("Van Krevelen diagram (H/C vs O/C)")

            fig_vk = px.scatter(
                df_vk,
                x="O/C",
                y="H/C",
                color="Lipid_class",
                hover_data=["Lipid_name", "Formula", "Lipid_category"],
                labels={"O/C": "O/C ratio", "H/C": "H/C ratio"},
            )

            fig_vk.update_xaxes(showline=True, linecolor="black", tickcolor="black", tickfont_color="black", title_font_color="black")
            fig_vk.update_yaxes(showline=True, linecolor="black", tickcolor="black", tickfont_color="black", title_font_color="black")
            fig_vk.update_layout(
                height=750,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01,
                            bgcolor="rgba(255,255,255,0.8)", bordercolor="lightgray", borderwidth=1,
                            font=dict(color="black")),
            )

            _, col, _ = st.columns([1, 18, 1])
            with col:
                st.plotly_chart(fig_vk, width='stretch')

    else:
        with engine.connect() as conn:
            df = pd.read_sql_table(table, conn)
        st.subheader(f"Table : {table} - {len(df)} rows")
        if df.empty:
            st.info("This table contains no data yet.")
        else:
            columns = {
                "Precursor_MZ":     st.column_config.NumberColumn(format="%.6f"),
                "Neutral_mass":     st.column_config.NumberColumn(format="%.6f"),
                "MZ":               st.column_config.NumberColumn(format="%.6f"),
                "Molecular_weight": st.column_config.NumberColumn(format="%.6f"),
                "RT":               st.column_config.NumberColumn(format="%.4f"),
                "CCS":              st.column_config.NumberColumn(format="%.4f"),
                "Intensity":        st.column_config.NumberColumn(format="%.6f"),
            }
            st.dataframe(df, column_config=columns, width='stretch')

except Exception as e:
    logger.exception("Error loading table '%s'", table)
    st.error(f"Error loading table : {e}")