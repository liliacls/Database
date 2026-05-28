from pathlib import Path
import streamlit as st
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).parent
DB_PATH = f"sqlite:///{PROJECT_ROOT / 'BacLipidDB.db'}"
HISTORY_PATH = PROJECT_ROOT / "import_history.json"


@st.cache_resource
def get_engine():
    return create_engine(DB_PATH, echo=False)
