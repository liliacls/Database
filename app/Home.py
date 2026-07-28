import logging
import streamlit as st
from sqlalchemy import func
from sqlalchemy.orm import Session
from pathlib import Path

from models.model import Detection
from config import get_engine, DB_FILE

st.set_page_config(layout="wide")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=60)
def statistics():
    """
    Calcule les statistiques résumées de la base de données, mises en cache pendant 60 secondes.
    Compte les détections MS1 et MS2 dans la base de données et calcule la taille sur disque du fichier de base de données.

    :return: Un dictionnaire avec les clés ``ms1`` (int, nombre de détections MS1),
        ``ms2`` (int, nombre de détections MS2) et ``db_size`` (str,
        taille lisible du fichier), ou ``None`` si les
        statistiques n'ont pas pu être calculées.
    :rtype: dict | None
    """
    try:
        with Session(get_engine()) as s:
            ms1 = (
                s.query(func.count(Detection.Detection_ID))
                .filter(Detection.MS_level == "MS1")
                .scalar()
                or 0
            )
            ms2 = (
                s.query(func.count(Detection.Detection_ID))
                .filter(Detection.MS_level == "MS2")
                .scalar()
                or 0
            )
        DBsize = DB_FILE.stat().st_size
        size_mb = DBsize / (1024 * 1024)
        db_size = f"{size_mb:.1f} Mo" if size_mb >= 1 else f"{DBsize / 1024:.1f} Ko"
        return {"ms1": ms1, "ms2": ms2, "db_size": db_size}
    except Exception:
        logger.exception("Unable to compute statistics")
        return None


logo_path = Path(__file__).parent.parent / "assets" / "APP.svg"

_, col_center, _ = st.columns([1, 1, 1])
with col_center:
    if logo_path.exists():
        st.image(str(logo_path), width="stretch")

# ── Description ────────────────────────────────────────────────────────────────
st.markdown(
    """
<p style="text-align: center;">
<strong>BacLipidAPP</strong> is a local web application for the integration, exploration, modification and export of lipidomic data from <strong>BacLipidDB</strong>.
</p>
""",
    unsafe_allow_html=True,
)
st.divider()

# ── Modules ─────────────────────────────────────────────────────────────────────
st.subheader("Available modules")
st.write("")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    with st.container(border=True):
        st.page_link("pages/1_Integration.py", label="MODULE 1")
        st.markdown("##### ⬇️ Integrate data")
        st.write("Import annotation files and integrate them into the database.")

with col2:
    with st.container(border=True):
        st.page_link("pages/2_BacLipidDB.py", label="MODULE 2")
        st.markdown("##### ⛁ BacLipidDB")
        st.write("Browse individual tables or explore a full joined view.")

with col3:
    with st.container(border=True):
        st.page_link("pages/3_Export.py", label="MODULE 3")
        st.markdown("##### ⬆️ Export data")
        st.write("Export data from the database in the desired format.")

with col4:
    with st.container(border=True):
        st.page_link("pages/4_Resources.py", label="MODULE 4")
        st.markdown("##### 📖 Resources")
        st.write("Column guide for building integration files.")

with col5:
    with st.container(border=True):
        st.page_link("pages/5_Management.py", label="MODULE 5")
        st.markdown("##### ✏️ Manage data")
        st.write("Correct, delete records already integrated into the database.")

st.write("")
st.divider()

# ── Statistiques ────────────────────────────────────────────────────────────────
st.subheader("Database overview")
st.write("")

stats = statistics()

if stats is None:
    st.warning("Unable to connect to the database.")
else:
    _, col1, col2, col3, _ = st.columns([1, 2, 2, 2, 1])

    with col1:
        with st.container(border=True):
            st.metric("MS1 detections", f"{stats['ms1']:,}")

    with col2:
        with st.container(border=True):
            st.metric("MS2 detections", f"{stats['ms2']:,}")

    with col3:
        with st.container(border=True):
            st.metric("Database size", stats["db_size"])

st.write("")
st.divider()
