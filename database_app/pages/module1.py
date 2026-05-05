import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys
import os

from database_loading.data_MS1_load import database_loading_MS1

from utils.exact_mass_calc import exact_mass_calculation
from utils.lipid_class_calc import lipid_class_calc
from utils.lipid_categorie_calc import lipid_category_calc
from utils.molecularw_calc import molecularw_calc

####################################################
# MODULE 1 : Page streamlit d'intégration de données
####################################################

# Chemin vers la base de données (à adapter selon votre environnement)
DB_PATH = "sqlite:////home/liliacls/Documents/Stage/Database/lipids.db"

# Colonnes obligatoire pour l'annotation MS1
REQUIRED_COLUMNS = ['Lipid_Name', 'Formula', 'Precursor_MZ']



#####################
# Interface streamlit
#####################

st.title(":blue[MODULE 1]: Intégration de données", text_alignment="center")
st. divider()

################################################################################

st.header(":blue[ETAPE 1]: - Paramétrages", text_alignment="left")
st. divider()

col1, col2, col3 = st.columns(3)

with col1:
    
    ms_level= st.selectbox(
        "Niveau d'annotation", 
        options=["MS1", "MS2", "MS3"],
        index=None,
        placeholder="Niveau MS",
        key="ms_level"
    )

with col2:
    
    ion_mode = st.selectbox(
        "Mode d'ionisation",
        options=["Positif", "Negatif"],
        index=None,
        placeholder="Mode d'ionisation",                    
        key="ion_mode"
    )

with col3:
    
    confidence_level = st.selectbox(
        "Niveau de confiance",
        options=[1, 2, 3, 4],
        index=None,
        placeholder="Niveau de confiance",
        key="confidence_level"
    )

if None in [ms_level, ion_mode, confidence_level]:
    st.warning("Veuillez renseigner tous les paramètres avant de continuer.", icon="⚠️")
    st.stop()
else:
    st.write("Vous avez sélectionné : ", ms_level, " - ", ion_mode, " - ", confidence_level, icon="✅")

if ms_level == "MS1":
    num_peaks = 0
else:
    num_peaks = None

################################################################################

st.header("ETAPE 2 - Chargement du fichier", text_alignment="left")
st. diviser()

uploaded_file = st.file_uploader(
    "Choisissez un fichier d'annotation",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
    key="file_uploader"
)

if uploaded_file is not None:
    try :
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success(f"Fichier chargé : {uploaded_file.name}")
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
else:
    st.stop()

################################################################################

st.header("ETAPE 3 - Vérification des colonnes obligatoires", text_alignment="left")
st. divider()
 
missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
 
if missing_columns:
    st.error(
        f"Le fichier ne contient pas les colonnes obligatoires suivantes : "
        f"**{', '.join(missing_columns)}**\n\n"
        f"Veuillez corriger votre fichier et le recharger."
    )
    st.stop()
else:
    st.success(f"Fichier valide : {len(df)} lignes détectées.", icon="✅")
    st.dataframe(df, use_container_width=True)

################################################################################

st.header("ETAPE 4 - Prévisualisation et complétion automatique", text_alignment="left")
st. diviser()

df["Exact_mass"] = df["Precursor_MZ"].apply(lambda mz: exact_mass_calculation(mz, ion_mode))
df["Molecular_weight"] = df["Formula"].apply(lambda f: molecularw_calc(f))
df["Lipid_class"] = df["Lipid_name"].apply(lambda n: lipid_class_calc(n))
df["Lipid_category"] = df["Lipid_class"].apply(lambda c: lipid_category_calc(c))
df["MS_level"] = ms_level
df["Num_Peaks"] = num_peaks

################################################################################

st.header("ETAPE 5 - Intégration dans la base de données", text_alignment="left")
st. diviser()

database_loading_MS1(df, confidence_level)
