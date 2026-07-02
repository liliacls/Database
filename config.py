"""
config.py
-----------
Configuration file for the BacLipidDB application.

# Documentation :
# - @st.cache_resource : https://docs.streamlit.io/1.55.0/develop/api-reference/caching-and-state/st.cache_resource#input-widgets
# - create_engine : https://docs.sqlalchemy.org/en/21/core/engines.html
"""

from pathlib import Path
import streamlit as st
from sqlalchemy import create_engine

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent

# Database path
DB_PATH = f"sqlite:///{PROJECT_ROOT / 'BacLipidDB.db'}"

# History file path
HISTORY_PATH = PROJECT_ROOT / "history.json"


@st.cache_resource
def get_engine():
    """Create and cache the SQLAlchemy engine for the SQLite database connection."""
    return create_engine(DB_PATH, echo=False)