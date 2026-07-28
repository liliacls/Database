import colorsys
import html
import logging
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.engine import Engine

from config import get_engine, PROJECT_ROOT
from utils.data_access import load_database
from utils.history import load_history

logger = logging.getLogger(__name__)

def _color(index: int) -> str:
    """
    Génère une couleur pastel pour un index de lot sans boucler sur une
    palette de taille fixe. L'index correspond au numéro de l'import de
    fichier (numéro de lot).

    :param index: index du lot
    :type index: int
    :return: chaîne de couleur hexadécimale
    :rtype: str
    """

    hue = (index * 0.618) % 1.0
    r, g, b = colorsys.hls_to_rgb(hue, 0.85, 0.55)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))

# logo de BacLipidDB
logo_path = PROJECT_ROOT / "assets" / "DB.svg"

_, col, _ = st.columns([1, 1, 1])
with col:
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

    - **Detection / Fragment / Lipid** - view the raw content of each individual table.
    - **Full view** - a joined view combining Detection, Lipid and Annotation. Rows are colored by import batch.
    - **History** - the list of past imports (filename, date, MS level, ionization mode, number of rows, submitted by).""")

engine = get_engine()

table = st.radio(
    "Select a table",
    options=["Detection", "Fragment", "Lipid", "Full view", "History"],
    horizontal=True,
    key="table_select",
)

st.divider()

def _formula(formula: str) -> dict:
    """
    Analyse une formule chimique en un dict associant symbole d'élément -> nombre d'atomes.

    :param formula: formule chimique
    :type formula: str
    :return: correspondance entre symbole d'élément et nombre d'atomes.
    :rtype: dict
    """
    counts = {}
    for element, num in re.findall(r'([A-Z][a-z]?)(\d*)', str(formula)):
        if element:
            counts[element] = counts.get(element, 0) + (int(num) if num else 1)
    return counts

def _load_data(_engine: Engine) -> pd.DataFrame:
    """
    Charge et met en cache les tables Annotation, Lipid, Detection via la fonction dans `data_access.py`.
    Seul Detection_ID est conservé comme colonne d'identifiant.

    :param _engine: moteur SQLAlchemy connecté à la base de données
    :type _engine: sqlalchemy.engine.Engine
    :return: DataFrame avec une ligne par Annotation, jointe avec son Lipid et sa Detection.
    :rtype: pandas.DataFrame
    """
    return load_database(_engine)[[
        "Detection_ID", "Lipid_name", "Formula", "FA_composition", "Lipid_class",
        "Lipid_subclass", "Lipid_category", "Precursor_MZ", "Adduct", "Neutral_mass",
        "Molecular_weight", "Monoisotopic_mass", "MS_level", "Ionisation_mode",
        "Num_Peaks", "RT", "CCS",
    ]]

def _batch_map(history: list[dict]) -> dict[int, int]:
    """
    Associe chaque Detection_ID à l'index du lot d'import auquel il appartient.

    Utilisé pour colorer les lignes de "Full view" selon le lot d'import (voir _color).
    Les index de lot sont assignés via enumerate(history), donc batch_id suit
    l'ordre des entrées dans history (0 pour le premier import, 1 pour le
    second, etc.).

    :param history: historique des imports, tel que retourné par load_history().
    :type history: list[dict]
    :return: correspondance entre Detection_ID et index de lot.
    :rtype: dict[int, int]
    """
    mapping = {}
    for batch_id, entry in enumerate(history):
        for detection_id in entry.get("detection_ids", []):
            mapping[detection_id] = batch_id
    return mapping

try:
    if table == "History":

        history = load_history()
        if not history:
            st.info("No imports recorded yet.")
        else:
            df_history = pd.DataFrame([
                {
                    "Filename":         e.get("filename", "-"),
                    "Date":             pd.to_datetime(e.get("inserted")),
                    "MS level":         e.get("ms_level"),
                    "Ionisation mode":  e.get("ionisation_mode"),
                    "Rows inserted":    e.get("num_rows"),
                    "Submitted by":     e.get("integrator") or "-",
                }
                for e in history
            ])
            st.subheader("History")
            st.dataframe(
                df_history,
                column_config={"Rows inserted": st.column_config.NumberColumn(format="%d")},
                width='stretch',
            )

    elif table == "Full view":
        df = _load_data(engine)

        st.subheader(f"Table : Full view - {len(df)} rows")
        if df.empty:
            st.info("This table contains no data yet.")
        else:
            history = load_history()
            id_caption = _batch_map(history)
            df = df.reset_index(drop=True)
            caption_values = df["Detection_ID"].map(id_caption).values
            last_batch_id = len(history) - 1 if history else None

            def _group(batch_id: float) -> str:
                """
                Classe l'index de lot d'une ligne dans un groupe d'import, utilisé pour
                assigner à la ligne une catégorie de couleur dans la table "Full view".

                :param batch_id: index de lot de la ligne (à partir de ``id_caption``),
                    ou NaN si le Detection_ID de la ligne n'a pas de lot correspondant
                :type batch_id: float
                :return: "Latest import", "Other imports" ou "Unknown"
                :rtype: str
                """
                if pd.isna(batch_id):
                    return "Unknown"
                return "Latest import" if int(batch_id) == last_batch_id else "Other imports"

            df["Import_group"] = pd.Series(caption_values).apply(_group)
            COLORS = {
                "Latest import": "#e34948",
                "Other imports": "#2a78d6",
                "Unknown": "#898781",
            }

            columns = {
                "Precursor_MZ":      st.column_config.NumberColumn(format="%.6f"),
                "Neutral_mass":      st.column_config.NumberColumn(format="%.6f"),
                "Molecular_weight":  st.column_config.NumberColumn(format="%.0f"),
                "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f"),
                "RT":                st.column_config.NumberColumn(format="%.4f"),
                "CCS":               st.column_config.NumberColumn(format="%.4f"),
            }

            def _row_color(row: pd.Series) -> list[str]:
                """
                Fonction de style pour ``df.style.apply(..., axis=1)`` : retourne
                la couleur de fond CSS à appliquer à chaque cellule d'une ligne
                de la table, selon le lot d'import auquel la ligne appartient.

                :param row: une ligne du DataFrame "Full view", telle que passée
                    par le Styler pandas (``row.name`` est l'index positionnel
                    de la ligne, utilisé pour retrouver son lot via ``caption_values``)
                :type row: pandas.Series
                :return: liste de chaînes CSS ``"background-color: #rrggbb"``,
                    une par colonne, ou des chaînes vides si le lot est inconnu
                :rtype: list[str]
                """
                caption = caption_values[row.name]
                if pd.isna(caption):
                    return [""] * len(row)
                batch_color = _color(int(caption))
                return [f"background-color: {batch_color}"] * len(row)

            style = df.style.apply(_row_color, axis=1)
            st.dataframe(style, column_config=columns, width='stretch')

            if history:
                with st.expander("color caption"):
                    for i, entry in enumerate(history):
                        batch_color = _color(i)
                        submitted_by = entry.get("integrator")
                        by_suffix = f", by {html.escape(submitted_by)}" if submitted_by else ""
                        filename = html.escape(entry.get("filename", "-"))
                        st.markdown(
                            f'<span style="background-color:{batch_color};padding:2px 12px;border-radius:4px;">'
                            f'&nbsp;</span>&nbsp; **File {i + 1}** - {filename} '
                            f'({entry.get("inserted", "")}, {entry.get("num_rows", "-")} rows{by_suffix})',
                            unsafe_allow_html=True,
                        )

            # ── Graphique 1 : Molecular weight vs Neutral mass ─────────────────

            df_plot = df.dropna(subset=["Neutral_mass", "Monoisotopic_mass"]).copy()
            if not df_plot.empty:
                df_plot["Delta (Da)"] = df_plot["Neutral_mass"] - df_plot["Monoisotopic_mass"]
                df_plot["Error (ppm)"] = (df_plot["Delta (Da)"] / df_plot["Monoisotopic_mass"]) * 1e6

            st.subheader("Measured neutral mass vs. theoretical monoisotopic mass (Da)")
            if df_plot.empty:
                st.info("No rows with both Neutral_mass and Monoisotopic_mass to plot.")
            else:
                fig_scatter = px.scatter(
                    df_plot,
                    x="Monoisotopic_mass",
                    y="Neutral_mass",
                    color="Import_group",
                    color_discrete_map=COLORS,
                    hover_data=["Lipid_name", "Lipid_class", "Delta (Da)", "Error (ppm)"],
                    labels={
                        "Monoisotopic_mass": "Monoisotopic mass (Da)",
                        "Neutral_mass": "Precursor neutral mass (Da)",
                        "Import_group": "Import",
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

            # ── Graphiques 2 & 3 : Mass error (ppm / Da) vs neutral mass ────────

            st.subheader("Mass error (ppm) vs. precursor neutral mass")
            if df_plot.empty:
                st.info("No rows with both Neutral_mass and Monoisotopic_mass to plot.")
            else:
                fig_scatter = px.scatter(
                    df_plot,
                    x="Neutral_mass",
                    y="Error (ppm)",
                    color="Import_group",
                    color_discrete_map=COLORS,
                    hover_data=["Lipid_name", "Lipid_class", "Error (ppm)"],
                    labels={
                        "Error (ppm)": "Mass error (ppm)",
                        "Neutral_mass": "Precursor neutral mass (Da)",
                        "Import_group": "Import",
                    },
                )

                _, col, _ = st.columns([1, 18, 1])
                with col:
                    st.plotly_chart(fig_scatter, width='stretch')

                st.subheader("Mass error (Da) vs. precursor neutral mass")

                fig_scatter = px.scatter(
                    df_plot,
                    x="Neutral_mass",
                    y="Delta (Da)",
                    color="Import_group",
                    color_discrete_map=COLORS,
                    hover_data=["Lipid_name", "Lipid_class", "Delta (Da)"],
                    labels={
                        "Delta (Da)": "Mass error (Da)",
                        "Neutral_mass": "Precursor neutral mass (Da)",
                        "Import_group": "Import",
                    },
                )

                _, col, _ = st.columns([1, 18, 1])
                with col:
                    st.plotly_chart(fig_scatter, width='stretch')

                st.subheader("Mass error table")
                df_error = (
                    df_plot[["Lipid_name", "Formula", "Neutral_mass", "Monoisotopic_mass", "Delta (Da)", "Error (ppm)"]]
                    .sort_values("Error (ppm)", key=lambda s: s.abs(), ascending=False)
                    .reset_index(drop=True)
                )
                st.dataframe(
                    df_error,
                    column_config={
                        "Neutral_mass":      st.column_config.NumberColumn(format="%.6f"),
                        "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f"),
                        "Delta (Da)":        st.column_config.NumberColumn(format="%.6f"),
                        "Error (ppm)":       st.column_config.NumberColumn(format="%.4f"),
                    },
                    width='stretch',
                )

            # ── Graphique 4 : Van Krevelen (H/C vs O/C) ────────────────────────

            df_vk = df.dropna(subset=["Formula"]).copy()
            df_vk["_atoms"] = df_vk["Formula"].apply(_formula)
            df_vk["C"] = df_vk["_atoms"].apply(lambda d: d.get("C", 0))
            df_vk["H"] = df_vk["_atoms"].apply(lambda d: d.get("H", 0))
            df_vk["O"] = df_vk["_atoms"].apply(lambda d: d.get("O", 0))
            df_vk = df_vk[df_vk["C"] > 0].copy()
            df_vk["H/C"] = df_vk["H"] / df_vk["C"]
            df_vk["O/C"] = df_vk["O"] / df_vk["C"]

            st.subheader("Van Krevelen diagram (H/C vs O/C)")
            if df_vk.empty:
                st.info("No rows with a parsable Formula to plot.")
            else:
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
                "Precursor_MZ":      st.column_config.NumberColumn(format="%.6f"),
                "Neutral_mass":      st.column_config.NumberColumn(format="%.6f"),
                "MZ":                st.column_config.NumberColumn(format="%.6f"),
                "Monoisotopic_mass": st.column_config.NumberColumn(format="%.8f"),
                "Molecular_weight":  st.column_config.NumberColumn(format="%.0f"),
                "RT":                st.column_config.NumberColumn(format="%.4f"),
                "CCS":               st.column_config.NumberColumn(format="%.4f"),
                "Intensity":         st.column_config.NumberColumn(format="%.6f"),
            }
            st.dataframe(df, column_config=columns, width='stretch')

except Exception as e:
    logger.exception("Error loading table '%s'", table)
    st.error(f"Error loading table : {e}")