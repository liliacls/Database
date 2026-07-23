"""
init_db.py
-----------
Create the database and all tables if they do not exist yet
Initialization script for the database "BacLipidDB.db"
Run this script only once to create the SQLite tables defined in models/model.py

Usage :
    python scripts/init_db.py
"""

import sys
from models.model import Base
from config import get_engine


def main():

    engine = get_engine()
    try:
        with engine.connect():
            print("Connection successful")
        Base.metadata.create_all(engine)
        print("Tables created successfully!")

    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
