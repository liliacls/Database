import streamlit as st
import pandas as pd
import sys
import os


# L'utilisateur sélectionne le niveau d'annotation, le mode d'ionisation et le niveau de confiance de l'annotation. 
# Ces paramètres vont être utilisés par la suite. Le niveau d'annotation permettra de déterminer "Num_Peaks", si c'est MS1 la valeur sera 0. 
# Le niveau d'annotation permettra de completer "MS_level". Le mode d'ionisation permettra de calculer la masse neutre "Exact_Mass".

# L'utilisateur charge son fichier d'annotation au format .xlsx/ .csv /.tsv
# Le fichier doit contenir dans l'ordre : "Precursor_MZ", "Lipid_name" et "Formula". Les colonnes "RT" et "CCS" sont optionnelles.
# Un fichier type sera intégré dans le projet afin de d'exemple


# Ajoute la racine du projet au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from data_loading.data_MS1_load import database_loading_MS1

from utils.lipid_class_calc import lipid_class_calculation, lipid_category_calculation
from utils.molecularw_calc import molecularw_calculation  
from utils.exact_mass_calc import exact_mass_calculation

####################################################
# MODULE 1 : Page streamlit d'intégration de données
####################################################

# Colonnes obligatoire pour l'annotation MS1
REQUIRED_COLUMNS = ['Lipid_Name', 'Formula', 'Precursor_MZ']


# _________________________________Interface streamlit__________________________________________________________________

st.title(":blue[MODULE 1] : Intégration de données", text_alignment="center")
st. divider()

# _________________________________ETAPE 1______________________________________________________________________________

st.header(":blue[ETAPE 1] - Paramétrages", text_alignment="left")
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
    st.success(f"Vous avez sélectionné : {ms_level} - {ion_mode} - {confidence_level}", icon="✅")

# _________________________________ETAPE 2______________________________________________________________________________

st.header("ETAPE 2 - Chargement du fichier", text_alignment="left")
st.divider()

# Zone de chargement du fichier
uploaded_file = st.file_uploader(
    "Choisissez un fichier d'annotation",
    type=["csv", "xlsx", "tsv"],
    accept_multiple_files=False,
    key="file_uploader"
)

# Si aucun fichier n'est chargé les étapes suivantes sont bloquées
if uploaded_file is None:
    st.stop()

# Lecture du fichier selon son format
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".tsv"):
        df = pd.read_csv(uploaded_file, sep='\t')
    else:
        df = pd.read_excel(uploaded_file)

    # Sauvegarde du dataframe dans la session pour les étapes suivantes
    st.session_state["df"] = df
    st.success(f"Fichier chargé : {uploaded_file.name} - {len(df)} lignes détectées.", icon="✅")

except Exception as e:
    st.error(f"Erreur lors du chargement du fichier : {e}")
    st.stop()

# Récupération du dataframe pour les étapes suivantes
df = st.session_state["df"]

# _________________________________ETAPE 3______________________________________________________________________________

st.header("ETAPE 3 - Vérification des colonnes obligatoires", text_alignment="left")
st.divider()

# Vérifie que toutes les colonnes obligatoires sont présentes dans le fichier
missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
    # Bloque l'intégration si des colonnes obligatoires sont manquantes
    st.error(
        f"Le fichier ne contient pas les colonnes obligatoires suivantes : "
        f"**{', '.join(missing_columns)}**\n\n"
        f"Veuillez corriger votre fichier et le recharger."
    )
    st.stop()
else:
    # Affiche le tableau brut pour que l'utilisateur vérifie son fichier
    st.success(f"Fichier valide", icon="✅")
    st.dataframe(df, use_container_width=True)

# _________________________________ETAPE 4______________________________________________________________________________

st.header("ETAPE 4 - Prévisualisation et complétion automatique", text_alignment="left")
st.divider()

# Bouton pour déclencher la complétion automatique des champs manquants
if st.button("Lancer la complétion automatique", type="primary", use_container_width=True):

    # Calcul de la masse exacte (masse neutre) depuis le Precursor_MZ et le mode d'ionisation
    try:
        df["Exact_mass"] = df["Precursor_MZ"].apply(lambda mz: exact_mass_calculation(mz, ion_mode))
    except Exception as e:
        st.error(f"Erreur lors du calcul de la masse exacte : {e}")
        st.stop()

    # Calcul du poids moléculaire depuis la formule brute
    try:
        df["Molecular_weight"] = df["Formula"].apply(lambda f: molecularw_calculation(f))
    except Exception as e:
        st.error(f"Erreur lors du calcul du poids moléculaire : {e}")
        st.stop()

    # Inférence de la classe lipidique depuis le nom du lipide
    try:
        df["Lipid_class"] = df["Lipid_Name"].apply(lambda n: lipid_class_calculation(n))
    except Exception as e:
        st.error(f"Erreur lors de l'inférence de la classe lipidique : {e}")
        st.stop()

    # Inférence de la catégorie lipidique depuis la classe
    try:
        df["Lipid_category"] = df["Lipid_class"].apply(lambda c: lipid_category_calculation(c))
    except Exception as e:
        st.error(f"Erreur lors de l'inférence de la catégorie lipidique : {e}")
        st.stop()

    # Définition de Num_Peaks : 0 si MS1, None sinon
    if ms_level == "MS1":
        num_peaks = 0
    else:
        num_peaks = None

    # Ajout des colonnes MS_level et Num_Peaks au dataframe
    df["MS_level"] = ms_level
    df["Num_Peaks"] = num_peaks

    # Sauvegarde du dataframe complété dans la session
    st.session_state["df_complete"] = df
    st.success("Complétion automatique réussie !")

# Bloque l'affichage du tableau si la complétion n'a pas encore été lancée
if "df_complete" not in st.session_state:
    st.stop()

# Affichage du tableau complété et éditable — l'utilisateur peut modifier ou supprimer des lignes
df_edite = st.data_editor(
    st.session_state["df_complete"],
    use_container_width=True,
    num_rows="dynamic",  # permet la suppression de lignes
    key="editor_integration"
)

if st.button("Valider les données", type="primary", use_container_width=True):

    # Vérifie la présence de cases vides dans le tableau
    if df_edite.isnull().any().any():
        colonnes_vides = df_edite.columns[df_edite.isnull().any()].tolist()
        st.warning(
            f"Le tableau contient des cases vides dans les colonnes : "
            f"**{', '.join(colonnes_vides)}**",
            icon="⚠️"
        )
    else:
        # Sauvegarde du tableau validé pour l'intégration en base
        st.session_state["df_valide"] = df_edite
        st.success(f"{len(df_edite)} lignes validées !", icon="✅")

# _________________________________ETAPE 5______________________________________________________________________________

st.header("ETAPE 5 - Intégration dans la base de données", text_alignment="left")
st.divider()

# Bloque l'intégration si l'utilisateur n'a pas validé les données en étape 4
if "df_valide" not in st.session_state:
    st.warning("Veuillez valider les données en étape 4 avant de continuer.", icon="⚠️")
    st.stop()

# Bouton de lancement de l'intégration
if st.button("Intégrer les données", type="primary", use_container_width=True):
    try:
        # Insertion des lignes validées dans les tables Detection, Lipid et Annotation
        database_loading_MS1(st.session_state["df_valide"], confidence_level)
        st.success("Intégration réussie !", icon="✅")
        st.balloons()
    except Exception as e:
        st.error(f"Erreur lors de l'intégration dans la base de données : {e}")