import streamlit as st
import pandas as pd
import sys
import os

# Ajoute la racine du projet au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from data_loading.data_MS1_load import database_loading_MS1

from utils.lipid_class_calc import lipid_class_calculation, lipid_category_calculation
from utils.molecularw_calc import molecularw_calculation  
from utils.exact_mass_calc import exact_mass_calculation

# _________________________________Description du MODULE 1__________________________________________________________________

# Partie 1 : 
# En premier l'utilisateur sélectionne le niveau d'annotation, le mode d'ionisation et le niveau de confiance de l'annotation. 
# Ces paramètres vont être utilisés par la suite. Le niveau d'annotation permettra de mettre le "Num_Peaks" à 0 si l'annotation est MS1.
# Le code devra être ajusté après ajout des données MS2 pour prendre le nombre de fragment en compte.
# Le niveau d'annotation permettra de completer "MS_level".
# Le mode d'ionisation (+ Precursor_MZ) permettra de calculer la masse neutre "Exact_Mass".

# Partie 2 :
# L'utilisateur charge son fichier d'annotation au format .xlsx/ .csv ou .tsv.
# Le fichier doit contenir dans l'ordre : "Precursor_MZ", "Lipid_name" et "Formula". 
# Les colonnes "RT" et "CCS" sont optionnelles.
# Un fichier type sera intégré dans le projet comme exemple. 

# Partie 3 : 
# Cette étape permet de vérifier si le fichier chargé est conforme. 
# Si ce n'est pas le cas l'utilisateur devra modifier son fichier et charger à nouveau son fichier.

# Partie 4 :
# Une fois que le tableur est valide, l'utilisateur lance la complétion automatique.
# Appel des fonctions lipid_class_calculation, lipid_category_calculation, molecularw_calculation et exact_mass_calculation depuis ./utils.
# Le tableur complet va ensuite s'afficher, cette étape permet à l'utilisateur de vérifier les données, compléter les données manquantes et supprimer des lignes.
# Le tableur ne pourra pas être intégré à la base de données si des informations sont manquantes.
# Un résumé s'affiche une fois que le tableau est validé avec un résumé les classes et les catégories des lipides. 

# Partie 5 :
# Intégration automatique dans les tables Detection, Lipid et Annotation de la base de données.

####################################################
# MODULE 1 : Data integration page
####################################################

# Colonnes obligatoire pour l'annotation MS1
REQUIRED_COLUMNS = ['Lipid_Name', 'Formula', 'Precursor_MZ']

# _________________________________Interface streamlit__________________________________________________________________

st.markdown("""
    <style>
    .module {
        border: 2px solid #1F77B4;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    <div class="module">
        <h1><span style="color:#1F77B4">MODULE 1</span> : Data integration page</h1>
    </div>
""", unsafe_allow_html=True)

# Bouton de réinitialisation à zéro
st.write("")
if st.button("Reset 🔄", type="secondary"):
    for key in ["df", "df_complete", "df_valide", "integration_done"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# _________________________________ETAPE 1______________________________________________________________________________

st.header(":blue[STEP 1] - Settings", text_alignment="left")
st. divider()

col1, col2, col3 = st.columns(3)

with col1:
    
    ms_level= st.selectbox(
        "Annotation level",
        options=["MS1", "MS2", "MS3"],
        index=None,
        placeholder="Annotation level",
        key="ms_level"
    )

with col2:
    
    ion_mode = st.selectbox(
        "Ionization mode",
        options=["Positive", "Negative"],
        index=None,
        placeholder="Ionization mode",
        key="ion_mode"
    )

with col3:
    
    confidence_level = st.selectbox(
        "Confidence level",
        options=[1, 2, 3, 4],
        index=None,
        placeholder="Confidence level",
        key="confidence_level"
    )

if None in [ms_level, ion_mode, confidence_level]:
    st.warning("Please fill in all parameters before continuing.", icon="⚠️")
    st.stop()
else:
    st.success(f"Selected : {ms_level} - {ion_mode} - {confidence_level}", icon="✅")

# _________________________________ETAPE 2______________________________________________________________________________

st.header(":blue[STEP 2] - File upload", text_alignment="left")
st.divider()

# Zone de chargement du fichier
uploaded_file = st.file_uploader(
    "Choose an annotation file",
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
    st.success(f"File loaded : {uploaded_file.name} - {len(df)} rows detected.", icon="✅")

except Exception as e:
    st.error(f"Error loading file : {e}")
    st.stop()

# Récupération du dataframe pour les étapes suivantes
df = st.session_state["df"]

# _________________________________ETAPE 3______________________________________________________________________________

st.header(":blue[STEP 3] - Required columns verification", text_alignment="left")
st.divider()

# Vérifie que toutes les colonnes obligatoires sont présentes dans le fichier
missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
    # Bloque l'intégration si des colonnes obligatoires sont manquantes
    st.error(
        f"The file is missing the following required columns : "
        f"**{', '.join(missing_columns)}**\n\n"
        f"Please correct your file and reload it."
    )
    st.stop()
else:
    # Affiche le tableau brut pour que l'utilisateur vérifie son fichier
    st.success(f"Valid file", icon="✅")
    st.dataframe(df, use_container_width=True)

# _________________________________ETAPE 4______________________________________________________________________________

st.header(":blue[STEP 4] - Preview and automatic completion", text_alignment="left")
st.divider()

# Bouton visible uniquement si la complétion n'a pas encore été lancée
if "df_complete" not in st.session_state:
    if st.button("Run automatic completion", type="primary", use_container_width=True):

        # Calcul de la masse exacte (masse neutre) depuis le Precursor_MZ et le mode d'ionisation
        try:
            df["Exact_mass"] = df["Precursor_MZ"].apply(lambda mz: exact_mass_calculation(mz, ion_mode))
        except Exception as e:
            st.error(f"Error calculating exact mass : {e}")
            st.stop()

        # Calcul du poids moléculaire depuis la formule brute
        try:
            df["Molecular_weight"] = df["Formula"].apply(lambda f: molecularw_calculation(f))
        except Exception as e:
            st.error(f"Error calculating molecular weight : {e}")
            st.stop()

        # Inférence de la classe lipidique depuis le nom du lipide
        try:
            df["Lipid_class"] = df["Lipid_Name"].apply(lambda n: lipid_class_calculation(n))
        except Exception as e:
            st.error(f"Error inferring lipid class : {e}")
            st.stop()

        # Inférence de la catégorie lipidique depuis la classe
        try:
            df["Lipid_category"] = df["Lipid_class"].apply(lambda c: lipid_category_calculation(c))
        except Exception as e:
            st.error(f"Error inferring lipid category : {e}")
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
        st.success("Automatic completion successful !")
        st.rerun()

# Bloque l'affichage du tableau si la complétion n'a pas encore été lancée
if "df_complete" not in st.session_state:
    st.stop()

# Affichage du tableau complété et éditable
df_edite = st.data_editor(
    st.session_state["df_complete"],
    use_container_width=True,
    num_rows="dynamic",
    key="editor_integration"
)

if st.button("Validate data", type="primary", use_container_width=True):
    # Vérifie la présence de cases vides dans le tableau
    if df_edite.isnull().any().any():
        colonnes_vides = df_edite.columns[df_edite.isnull().any()].tolist()
        st.warning(
            f"The table contains empty cells in the following columns : "
            f"**{', '.join(colonnes_vides)}**",
            icon="⚠️"
        )
    else:
        # Sauvegarde du tableau validé pour l'intégration en base
        st.session_state["df_valide"] = df_edite
        st.success("Data validated !", icon="✅")

# Résumé des données validées
if "df_valide" in st.session_state:
    st.subheader("Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**By lipid class :**")
        st.dataframe(
            st.session_state["df_valide"]["Lipid_class"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Class", "Lipid_class": "Count"}),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("**By lipid category :**")
        st.dataframe(
            st.session_state["df_valide"]["Lipid_category"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Category", "Lipid_category": "Count"}),
            use_container_width=True,
            hide_index=True
        )

    st.info(f"Total : **{len(st.session_state['df_valide'])}** lipids to integrate.")

# _________________________________ETAPE 5______________________________________________________________________________

st.header(":blue[ETAPE 5] - Database integration", text_alignment="left")
st.divider()

# Bloque l'intégration si l'utilisateur n'a pas validé les données en étape 4
if "df_valide" not in st.session_state:
    st.warning("Please validate the data in step 4 before continuing.", icon="⚠️")
    st.stop()

# Bouton de lancement de l'intégration (désactivé après une intégration réussie)
if st.button("Integrate data", type="primary", use_container_width=True,
             disabled=st.session_state.get("integration_done", False)):
    try:
        # Insertion des lignes validées dans les tables Detection, Lipid et Annotation
        database_loading_MS1(st.session_state["df_valide"], confidence_level)
        
        # Mémorise que l'intégration a été faite pour bloquer le bouton
        st.session_state["integration_done"] = True
        st.success("Integration successful !")
        st.balloons()
    except Exception as e:
        st.error(f"Error during database integration {e}")