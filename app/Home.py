"""
Home.py
-------
Page d'accueil de BacLipidDB.
"""

import logging
import streamlit as st

st.set_page_config(layout="wide")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

st.markdown("""
    <style>
        
    .module {
        border: 5px solid #000000;
        border-radius: 10px;
        text-align: center;
        padding: 10px;
        background-color: #1F77B4;
    }
    .card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
        height: 100%;
    }
    .card h3 {
        color: #1F77B4;
        margin-top: 0;
    }
    .card .module-number {
        font-size: 0.85em;
        color: #888;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .step {
        background-color: #eef4fb;
        border-left: 4px solid #1F77B4;
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 6px;
    }
    </style>

    <div class="module">
        <h1><span style="color:#ffffff">BacLipidDB</span></h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# ── Description ────────────────────────────────────────────────────────────────
st.markdown("""
**BacLipidDB** est une base de données relationnelle spécialisée dans l'annotation de 
lipides bactériens issus de plusieurs plateformes analytiques de spectrométrie de masse. 
Elle est conçue pour stocker, intégrer, explorer et exporter des données lipidiques.
""")
st.divider()

# ── Modules ─────────────────────────────────────────────────────────────────────
st.subheader("Modules disponibles")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.caption("MODULE 1")
        st.markdown("##### 📥 Integration")
        st.write("Importez des fichiers d'annotations et intégrez-les dans la base.")

with col2:
    with st.container(border=True):
        st.caption("MODULE 2")
        st.markdown("##### ⛁ Database")
        st.write("Visualisez le contenu des tables individuellement ou explorez une vue complète.")

with col3:
    with st.container(border=True):
        st.caption("MODULE 3")
        st.markdown("##### 📤 Export")
        st.write("Exportez les données de la base au format souhaité pour une utilisation externe.")

st.write("")
st.divider()