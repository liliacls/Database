# BacLipidAPP Project

L'application web locale Streamlit **BacLipidAPP** est développée afin d'interagir de différentes manières avec la base de données relationnelle SQLite **BacLipidDB**.
L'objectif est de centraliser les annotations lipidomiques réalisées dans l'équipe 1 "Analyse et modélisation" de l'Institu CARMeN (Chimie organique, Bioorganique, Réactivité et Analyse) et de l'équipde BRICS (Biofilms, Résistance, Interactions Cellules-Surfaces) du Laboratoire PBS (Polymères, Biopolymères, Surfaces). 
**BacLipidAPP** est composée de 5 modules qui permettent d'ajouter, de visualiser, de modifier et de supprimer les données dans 
**BacLipidDB**.

---

# **Architecture**
```
BacLipidDB/
├── 📁 .streamlit/
│       └── config.toml
├── 📄 config.py
├── 📄 Documentation.html
├── 📄 environment.yml
├── 📄 LICENSE
├── 📄 README.md
├── 📄 requirements.txt
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
├── 📁 Documentation/
│       ├── 📄 conf.py
│       ├── 📄 index.rst
│       ├── 📄 Home.rst
│       ├── 📄 1_Integration.rst
│       ├── 📄 2_BacLipidDB.rst
│       ├── 📄 3_Export.rst
│       ├── 📄 4_Resources.rst
│       ├── 📄 5_Management.rst
│       ├── 📄 model.rst
│       ├── 📄 api.rst
│       ├── 📄 Makefile
│       └── 📄 make.bat
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
| `1_Integration.py` | Permet d'importer un fichier d'annotations et de l'intégrer dans la base de données **BacLipidDB** |
| `2_BacLipidDB.py` | Permet de visualiser le contenu des tables ou une vue complète de la base de données |
| `3_Export.py` | Permet de filtrer les données et de les exporter en CSV (MS1) ou en MSP (MS2) compatible avec le logiciel MZmine |
| `4_Resources.py` | Fournit les fichiers modèles pour l'intégration, un guide des colonnes attendues et la gestion des adduits |
| `5_Management.py` | Permet d'éditer ou de supprimer des enregistrements déjà intégrés |

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
| `neutral_mass.py` | Calcule la masse neutre à partir du rapport *m/z* et de l'adduit (défini dans `adducts.json`) (utilisé par les pages 1 `1_Integration.py` et 4 `4_Resources.py`) |
| `molecular_weight.py` | Calcule la masse moléculaire moyenne à partir de la formule brute via la librairie python `molmass` (utilisé par les pages 1 `1_Integration.py` et 5 `5_Management.py`) |
| `monoisotopic.py` | Calcule la masse monoisotopique exacte à partir de la formule brute via la librairie python `molmass` (utilisé par les pages 1 `1_Integration.py` et 5 `5_Management.py`) |
| `msp_export.py` | Génère le contenu d'un fichier `.msp` à partir des annotations MS2 filtrées (utilisé par la page 3 `3_Export.py`) |
| `loading_MS1.py` | Insère les données d'un DataFrame MS1 dans les tables `Detection`, `Lipid` et `Annotation` (utilisé par la page 1 `1_Integration.py`) |
| `loading_MS2.py` | Lit un fichier `.msp` MS2 et insère les détections, fragments et annotations dans la base (utilisé par la page 1 `1_Integration.py`) |
| `data_access.py` | Charge la vue jointe complète (`Annotation` + `Lipid` + `Detection`) utilisée par les pages 2 `2_BacLipidDB.py`, 3 `3_Export.py` et 5 `5_Management.py` |
| `db_backup.py` | Crée une copie horodatée de `BacLipidDB.db` dans `backups/` avant chaque intégration ou modification (utilisé par la page 5 `5_Management.py`) |
| `history.py` | Lit/écrit `history.json`, l'historique des imports (ajout, consultation, suppression d'une entrée) (utilisé par les pages 1 `1_Integration.py`, 2 `2_BacLipidDB.py` et 5 `5_Management.py`) |
| `exceptions.py` | Exceptions personnalisées `PostIntegrationError` (commit réussi mais backup/historique en échec) (utilisé par la page 1 `1_Integration.py`) |

---

### `scripts/` - Scripts d'exécution ponctuelle
Scripts à lancer en ligne de commande pour initialiser ou réinitialiser la base de données.

| Fichier | Rôle |
|---|---|
| `init_db.py` | Initialise la base de données en créeant toutes les tables et leurs relations à partir de `models/model.py` (à lancer une seule fois) |
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

### Initialiser la base de données
À faire une seule fois, après avoir cloné le projet et activé l'environnement (conda ou venv). Ce script crée le fichier `BacLipidDB.db` et toutes les tables définies dans `models/model.py` :
```bash
python scripts/init_db.py
```
Si la base existe déjà, ce script ne fait rien. Pour vider une base existante sans supprimer les tables, voir `scripts/reset_db.py` :
```bash
python scripts/reset_db.py
```

---

# **Lancer l'application**

Une fois l'environnement activé et la base initialisée, lancer l'application Streamlit depuis la racine du projet :
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

# **Documentation**

La documentation technique (guide des modules Streamlit + référence API générée depuis les docstrings) est construite avec Sphinx, dans le dossier `Documentation/`. `sphinx` et `sphinx-rtd-theme` font partie des dépendances du projet (`requirements.txt` / `environment.yml`).

### Documentation utilisateur

Un guide utilisateur au format HTML (`Documentation.html`, à la racine du projet) présente chaque module de l'application (Home, Intégration, BacLipidDB, Export, Resources, Management) pas à pas, sans notion de code.

- Après un `git clone` du projet (voir [Récupérer le projet](#récupérer-le-projet)), ouvrir directement le fichier dans un navigateur :
```bash
xdg-open Documentation.html   # Linux
open Documentation.html       # macOS
start Documentation.html      # Windows
```
- Pour ne récupérer que ce fichier sans cloner tout le dépôt : sur la page du fichier sur GitHub, cliquer sur le bouton **Download raw file** (icône ⬇️), ou en ligne de commande :
```bash
curl -o Documentation.html https://raw.githubusercontent.com/liliacls/Database/main/Documentation.html
```

### Mettre à jour le contenu
- Pages Streamlit (`Home.rst`, `1_Integration.rst`, `2_BacLipidDB.rst`, `3_Export.rst`, `4_Resources.rst`, `5_Management.rst`) : à éditer manuellement dans `Documentation/` si le comportement d'une page change.
- Modèle de données (`model.rst`) : à éditer manuellement dans `Documentation/` si le schéma de `models/model.py` (tables, colonnes, relations) change.
- Référence API (`api.rst`) : générée automatiquement depuis les docstrings du code (`sphinx.ext.autodoc`). Pour l'enrichir, il suffit de mettre à jour les docstrings (format reST : `:param:`, `:return:`, `:rtype:`) dans `config.py`, `models/model.py`, `utils/*.py` et `scripts/*.py`.

### Regénérer la doc HTML
Depuis le dossier `Documentation/` :
```bash
cd Documentation
make html          # ne régénère que les pages dont la source (.rst / docstring) a changé
make clean html    # complet : supprime _build/ puis régénère toutes les pages
```
Le résultat est généré dans `Documentation/_build/html/` ; ouvrir `index.html` dans un navigateur pour la consulter.

### Lancer la doc en ligne de commande
Une fois `Documentation/_build/html/` généré, l'ouvrir directement depuis le terminal :
```bash
xdg-open Documentation/_build/html/index.html   # Linux
open Documentation/_build/html/index.html       # macOS
start Documentation/_build/html/index.html      # Windows
```

### Générer la doc en PDF
Nécessite une distribution LaTeX installée sur la machine (`latexmk`, `pdflatex`). Depuis le dossier `Documentation/` :
```bash
cd Documentation
make latexpdf
```
Le PDF est généré dans `Documentation/_build/latex/` (un seul fichier regroupant `index.rst` et toutes les pages liées via les toctrees).

---

# **License**

Ce projet est distribué sous licence [MIT](LICENSE).

---