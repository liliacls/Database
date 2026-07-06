"""
Home.py
-------
Page d'accueil de BacLipidDB.
"""

import logging
import streamlit as st
from sqlalchemy import func
from sqlalchemy.orm import Session
from pathlib import Path

from models.model import Detection
from config import get_engine

st.set_page_config(layout="wide")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


@st.cache_data(ttl=60)
def statistics():
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
        DBsize = Path(__file__).parent.parent.joinpath("BacLipidDB.db").stat().st_size
        size_mb = DBsize / (1024 * 1024)
        db_size = f"{size_mb:.1f} Mo" if size_mb >= 1 else f"{DBsize / 1024:.1f} Ko"
        return {"ms1": ms1, "ms2": ms2, "db_size": db_size}
    except Exception:
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
<strong>BacLipidAPP</strong> is a web application for the integration, exploration and export of lipidomic data from <strong>BacLipidDB</strong>.
</p>
""",
    unsafe_allow_html=True,
)
st.divider()

# ── Modules ─────────────────────────────────────────────────────────────────────
st.subheader("Available modules")
st.write("")

col1, col2, col3 = st.columns(3)

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

st.write("")
st.divider()

# ── Statistics ──────────────────────────────────────────────────────────────────
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
