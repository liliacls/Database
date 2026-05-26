# BacLipidDB Project

BacLipidDB est une base de données relationnelle spécialisée dans l'annotation de lipides bactériens issus de spectrométrie de masse. Elle permet de stocker, intégrer, explorer et exporter des données lipidiques via une interface Streamlit.

---

# **Architecture**
```
BacLipidDB/
├──  📁.streamlit/
│       └── config.toml
├── 📄 config.py
├── 📄 environment.yml
├── 📄 README.md
├── 📁 app/
│       ├── 📄 Home.py
│       └── pages/
│           ├── 📄 1_Integration.py
│           ├── 📄 2_Database.py
│           └── 📄 3_Export.py
├── 📁 assets/
        └── pages/
├── 📁 models/
│       ├── __init__.py
│       └── 📄 model.py
├── 📁 utils/
│       ├── __init__.py
│       ├── 📄 neutral_mass.py
│       ├── 📄 molecular_weight.py
│       ├── 📄 msp_export.py
│       ├── 📄 precursor_type.py
│       └── 📄 loading_MS1.py

└── 📁 scripts/
        ├── init_db.pY
        ├── 📄 init_db.py
        ├── 📄 load_MS2_msp.py
        └── 📄 reset_db.py

```

---

# **Description des modules**

### `config.py`
Configuration globale du projet : chemin racine, URL de connexion à la base SQLite (`BacLipidDB.db`) et création du moteur SQLAlchemy partagé (`get_engine()`).

---

### `app/` - Interface utilisateur Streamlit
Pages de l'application web Streamlit accessibles depuis le navigateur.

| Fichier | Rôle |
|---|---|
| `Home.py` | Page d'accueil, présente les trois modules de l'application |
| `1_Integration.py` | Importe un fichier d'annotations et l'intègre dans la base de données |
| `2_Database.py` | Visualise le contenu des tables ou une vue complète de la base de données |
| `3_Export.py` | Filtre les données et les exporte en CSV (MS1) ou en MSP (MS2) compatible avec le logiciel MZmine |

---

### `models/` - Modèles de base de données (ORM)
Définit la structure de la base de données via SQLAlchemy.

| Fichier | Rôle |
|---|---|
| `model.py` | Déclare les 4 tables SQLite : `Detection`, `Fragment`, `Lipid`, `Annotation` et leurs relations |

---

### `utils/` - Fonctions utilitaires
Fonctions de calcul et d'insertion utilisées par les modules d'intégration (Module 1) et d'export (Module 3).

| Fichier | Rôle |
|---|---|
| `neutral_mass.py` | Calcule la masse neutre à partir du rapport m/z et du mode d'ionisation (positif/négatif) |
| `molecular_weight.py` | Calcule le poids moléculaire à partir de la formule brute via la librairie `molmass` |
| `precursor_type.py` | Déduit le type de précurseur (`[M+H]+` ou `[M-H]-`) à partir de la masse neutre et du m/z |
| `msp_export.py` | Génère le contenu d'un fichier `.msp` à partir des annotations MS2 filtrées |
| `loading_MS1.py` | Insère les données d'un DataFrame MS1 dans les tables `Detection`, `Lipid` et `Annotation` |

---

### `scripts/` - Scripts d'exécution ponctuelle
Scripts à lancer en ligne de commande pour initialiser, alimenter ou réinitialiser la base de données.

| Fichier | Rôle |
|---|---|
| `init_db.py` | Initialise la base de données et crée toutes les tables |
| `reset_db.py` | Supprime tous les enregistrements sans supprimer les tables |
| `load_MS2_msp.py` | Lit un fichier `.msp` MS2 et insère les détections, fragments et annotations dans la base |

---

# **Create the conda environment**
```bash
   conda create --file environment.yml
   conda activate lipid_database
```
