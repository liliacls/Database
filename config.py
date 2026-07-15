from pathlib import Path
import streamlit as st
from sqlalchemy import create_engine, event

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent

# Database path
DB_FILE = PROJECT_ROOT / "BacLipidDB.db"
DB_PATH = f"sqlite:///{DB_FILE}"

# History file path
HISTORY_PATH = PROJECT_ROOT / "history.json"

# Directory where database snapshots are stored (one per import)
BACKUP_DIR = PROJECT_ROOT / "backups"


@st.cache_resource
def get_engine():
    """Create and cache the SQLAlchemy engine for the SQLite database connection."""
    engine = create_engine(DB_PATH, echo=False)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine