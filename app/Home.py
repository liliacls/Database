"""
Home.py
-------
Page d'accueil de BacLipidDB.
"""

import logging
import streamlit as st
from sqlalchemy import func
from sqlalchemy.orm import Session

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.model import Detection
from config import get_engine

st.set_page_config(layout="wide")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

@st.cache_data(ttl=60)
def stats():
    try:
        with Session(get_engine()) as s:
            ms1 = s.query(func.count(Detection.Detection_ID)).filter(Detection.MS_level == "MS1").scalar() or 0
            ms2 = s.query(func.count(Detection.Detection_ID)).filter(Detection.MS_level == "MS2").scalar() or 0
        DBsize = Path(__file__).parent.parent.joinpath("BacLipidDB.db").stat().st_size
        size_mb = DBsize / (1024 * 1024)
        db_size = f"{size_mb:.1f} Mo" if size_mb >= 1 else f"{DBsize / 1024:.1f} Ko"
        return {"ms1": ms1, "ms2": ms2, "db_size": db_size}
    except Exception:
        return None

logo_path = Path(__file__).parent.parent / "assets" / "logoDB.svg"
if logo_path.exists():
    col = st.columns([1, 4, 1])
    with col[1]:
        st.image(str(logo_path), use_container_width=True)

st.write("")

# ── Description ────────────────────────────────────────────────────────────────
st.markdown("""
**BacLipidDB** is a relational database specialized in the annotation of
bacterial lipids from multiple mass spectrometry analytical platforms.
It is designed to store, integrate, explore and export lipidomic data.
""")
st.divider()

# ── Modules ─────────────────────────────────────────────────────────────────────
st.subheader("Available modules")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.page_link("pages/1_Integration.py", label="MODULE 1")
        st.markdown("##### 📥 Integration")
        st.write("Import annotation files and integrate them into the database.")

with col2:
    with st.container(border=True):
        st.page_link("pages/2_Database.py", label="MODULE 2")
        st.markdown("##### ⛁ Database")
        st.write("Browse individual tables or explore a full joined view.")

with col3:
    with st.container(border=True):
        st.page_link("pages/3_Export.py", label="MODULE 3")
        st.markdown("##### 📤 Export")
        st.write("Export data from the database in the desired format.")

st.write("")
st.divider()

# ── Statistics ──────────────────────────────────────────────────────────────────
st.subheader("Database overview")
st.write("")

stats = stats()

if stats is None:
    st.warning("Unable to connect to the database.")
else:
    _, col1, col2, _ = st.columns([1, 2, 2, 1])

    with col1:
        with st.container(border=True):
            st.metric("MS1 detections", f"{stats['ms1']:,}")

    with col2:
        with st.container(border=True):
            st.metric("MS2 detections", f"{stats['ms2']:,}")

st.write("")
st.divider()