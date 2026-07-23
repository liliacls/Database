# BacLipidDB Project

BacLipidDB est une base de données relationnelle spécialisée dans l'annotation de lipides bactériens issus de spectrométrie de masse. Elle permet de stocker, intégrer, explorer et exporter des données lipidiques via une interface Streamlit.

---

# **Architecture**
```
BacLipidDB/
├── 📁 .streamlit/
│       └── config.toml
├── 📄 config.py
├── 📄 environment.yml
├── 📄 requirements.txt
├── 📄 adducts.json
├── 📄 history.json
├── 📄 README.md
├── 📁 app/
│       ├── 📄 Home.py
│       └── 📁 pages/
│           ├── 📄 1_Integration.py
│           ├── 📄 2_BacLipidDB.py
│           ├── 📄 3_Export.py
│           ├── 📄 4_Resources.py
│           └── 📄 5_Management.py
├── 📁 assets/
│       ├── 📄 APP.svg
│       └── 📄 DB.svg
├── 📁 models/
│       ├── __init__.py
│       └── 📄 model.py
├── 📁 utils/
│       ├── __init__.py
│       ├── 📄 neutral_mass.py
│       ├── 📄 molecular_weight.py
│       ├── 📄 monoisotopic.py
│       ├── 📄 msp_export.py
│       ├── 📄 loading_MS1.py
│       ├── 📄 loading_MS2.py
│       ├── 📄 data_access.py
│       ├── 📄 db_backup.py
│       ├── 📄 history.py
│       └── 📄 exceptions.py
└── 📁 scripts/
        ├── 📄 init_db.py
        └── 📄 reset_db.py
```

---

# **Description des modules**

### `config.py`
Configuration globale du projet : chemin racine, URL de connexion à la base SQLite (`BacLipidDB.db`), chemins des fichiers `history.json`, `adducts.json` et du dossier `backups/`, et création du moteur SQLAlchemy partagé (`get_engine()`).

---

### `app/` - Interface utilisateur Streamlit
Pages de l'application web Streamlit accessibles depuis le navigateur.

| Fichier | Rôle |
|---|---|
| `Home.py` | Page d'accueil, présente les cinq modules de l'application |
| `1_Integration.py` | Importe un fichier d'annotations et l'intègre dans la base de données |
| `2_BacLipidDB.py` | Visualise le contenu des tables ou une vue complète de la base de données |
| `3_Export.py` | Filtre les données et les exporte en CSV (MS1) ou en MSP (MS2) compatible avec le logiciel MZmine |
| `4_Resources.py` | Fournit les fichiers modèles pour l'intégration, un guide des colonnes attendues et la gestion des adduits custom |
| `5_Management.py` | Édite ou supprime des enregistrements déjà intégrés, et permet de retirer une intégration entière depuis l'historique |

---

### `models/` - Modèles de base de données (ORM)
Définit la structure de la base de données via SQLAlchemy.

| Fichier | Rôle |
|---|---|
| `model.py` | Déclare les 4 tables SQLite : `Detection`, `Fragment`, `Lipid`, `Annotation` et leurs relations |

---

### `utils/` - Fonctions utilitaires
Fonctions de calcul, d'insertion et de maintenance utilisées par les différents modules de l'application.

| Fichier | Rôle |
|---|---|
| `neutral_mass.py` | Calcule la masse neutre à partir du rapport m/z et de l'adduit (built-in ou custom, défini dans `adducts.json`) |
| `molecular_weight.py` | Calcule le poids moléculaire moyen à partir de la formule brute via la librairie `molmass` |
| `monoisotopic.py` | Calcule la masse monoisotopique à partir de la formule brute via la librairie `molmass` |
| `msp_export.py` | Génère le contenu d'un fichier `.msp` à partir des annotations MS2 filtrées |
| `loading_MS1.py` | Insère les données d'un DataFrame MS1 dans les tables `Detection`, `Lipid` et `Annotation` |
| `loading_MS2.py` | Lit un fichier `.msp` MS2 et insère les détections, fragments et annotations dans la base |
| `data_access.py` | Charge la vue jointe complète (`Annotation` + `Lipid` + `Detection`) utilisée par les pages de visualisation |
| `db_backup.py` | Crée une copie horodatée de `BacLipidDB.db` dans `backups/` avant chaque intégration ou modification |
| `history.py` | Lit/écrit `history.json`, l'historique des imports (ajout, consultation, suppression d'une entrée) |
| `exceptions.py` | Exceptions personnalisées, notamment `PostIntegrationError` (commit réussi mais backup/historique en échec) |

---

### `scripts/` - Scripts d'exécution ponctuelle
Scripts à lancer en ligne de commande pour initialiser ou réinitialiser la base de données.

| Fichier | Rôle |
|---|---|
| `init_db.py` | Initialise la base de données et crée toutes les tables (à lancer une seule fois) |
| `reset_db.py` | Supprime tous les enregistrements sans supprimer les tables, et vide `history.json` |

---

# **Installation**

### Récupérer le projet
```bash
git clone https://github.com/liliacls/Database.git
cd Database
```

### Option 1 - Avec conda (recommandé)
`environment.yml` fixe la version de Python (3.12) et toutes les dépendances.
```bash
conda env create -f environment.yml
conda activate lipid_database
```
Pour mettre à jour l'environnement après une modification de `environment.yml` :
```bash
conda env update -f environment.yml --prune
```

### Option 2 - Avec pip
Nécessite Python 3.12 déjà installé. Dans un environnement virtuel dédié :
```bash
python3.12 -m venv .venv
source .venv/bin/activate   # sous Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

---

# **Lancer l'application**

```bash
streamlit run app/Home.py
```

L'application est alors accessible sur [http://localhost:8501](http://localhost:8501).

### Fichiers générés à l'exécution
Ces fichiers/dossiers ne sont pas versionnés (voir `.gitignore`) et sont créés automatiquement au fil de l'utilisation :

| Fichier / dossier | Créé par | Contenu |
|---|---|---|
| `history.json` | Module 1 (Intégration) | Historique des imports |
| `adducts.json` | Module 4 (Ressources) | Adduits ajoutés par l'utilisateur |
| `backups/` | Modules 1 et 5 | Sauvegardes horodatés de `BacLipidDB.db` avant chaque intégration/modification |

---


