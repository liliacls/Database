from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DB_PATH = f"sqlite:///{PROJECT_ROOT / 'BacLipidDB.db'}"
