import sqlalchemy as db
import streamlit as st
import pandas as pd
import pyteomics
import sqlite3

# Creation and connection to the database
engine = db.create_engine('sqlite:///lipids.db')
conn = engine.connect()

