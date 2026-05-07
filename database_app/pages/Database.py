import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "sqlite:////home/liliacls/Documents/Stage/Database/BacLipidDB.db"

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

# Connexion à la base
engine = create_engine(DB_PATH, echo=False)

# Boutons de sélection de table au dessus du tableau
table = st.radio(
    "Sélectionner une table",
    options=["Annotation", "Detection", "Fragment", "Lipid", "Vue complète"],
    horizontal=True,
    key="table_select"
)

st.divider()

# Chargement et affichage de la table sélectionnée
try:
    if table == "Vue complète":
        # Jointure des 3 tables principales
        query = """
            SELECT "
                l.Lipid_name, l.Formula, l.Lipid_class, l.Lipid_category,
                d.Precursor_MZ, d.Exact_mass, d.Molecular_weight,
                d.MS_level, d.Num_Peaks, d.RT, d.CCS,
                a.Confidence_level
            FROM Annotation a
            JOIN Lipid l ON a.Lipid_id = l.Lipids_ID
            JOIN Detection d ON a.Detection_id = d.Detection_ID
        """
        df = pd.read_sql(query, engine)
    else:
        df = pd.read_sql_table(table, engine)

    st.subheader(f"Table : {table} — {len(df)} lignes")
    st.dataframe(df, use_container_width=True, height=600)

except Exception as e:
    st.error(f"Erreur lors du chargement de la table : {e}")