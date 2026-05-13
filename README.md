# BacLipidDB Project

BacLipidDB est une base de données relationnelle spécialisée dans l'annotation de lipides bactériens issus de spectrométrie de masse. Elle permet de stocker, intégrer, explorer et exporter des données lipidiques via une interface Streamlit.

---

# **Architecture**
```
BacLipidDB/
├── 📄 .streamlit/config.toml
├── 📄 config.py
├── 📄 environment.yml
├── 📁 app/
│       ├── Home.py
│       └── pages/
│           ├── 📄 1_Integration.py
│           ├── 📄 2_Database.py
│           └── 📄 3_Export.py
├── 📁 models/
│       ├── __init__.py
│       └── 📄 model.py
├── 📁 integration/
│       ├── __init__.py
│       └── 📄 loading.py
├── 📁 utils/
│       ├── __init__.py
│       ├── 📄 exact_mass.py
│       ├── 📄 lipid_class.py
│       └── 📄 molecular_weight.py
└── 📁 scripts/
        ├── init_db.py
        ├── 📄 clean_MS1.py
        ├── 📄 load_MS1.py
        └── 📄 export_MS1.py

```

---

# **Description des modules**

### `config.py`
Centralise la configuration globale du projet : chemin racine et URL de connexion à la base SQLite (`BacLipidDB.db`).

---

### `app/` — Interface utilisateur Streamlit
Pages de l'application web accessibles depuis le navigateur.

| Fichier | Rôle |
|---|---|
| `Home.py` | Page d'accueil, présente les trois modules de l'application |
| `1_Integration.py` | Importe un fichier d'annotations et l'intègre dans la base |
| `2_Database.py` | Visualise le contenu des tables et explore la base |
| `3_Export.py` | Extrait les données de la base et les exporte en CSV compatible MZmine |

---

### `models/` — Modèles de base de données (ORM)
Définit la structure de la base de données via SQLAlchemy.

| Fichier | Rôle |
|---|---|
| `model.py` | Déclare les 4 tables SQLite : `Detection`, `Fragment`, `Lipid`, `Annotation` et leurs relations |

---

### `integration/` — Intégration des données
Couche intermédiaire entre l'interface utilisateur et la base de données.

| Fichier | Rôle |
|---|---|
| `loading.py` | Insère les données d'un DataFrame MS1 dans les tables `Detection`, `Lipid` et `Annotation` via une transaction SQLAlchemy |

---

### `utils/` — Fonctions de calcul
Fonctions utilitaires utilisées dans le module "1_Integration.py" de l'application web

| Fichier | Rôle |
|---|---|
| `exact_mass.py` | Calcule la masse monoisotopique neutre à partir du rapport m/z et du mode d'ionisation (positif/négatif) |
| `lipid_class.py` | Détermine la classe lipidique et la catégorie à partir du nom du lipide |
| `molecular_weight.py` | Calcule le poids moléculaire à partir de la formule brute via la librairie `molmass` |

---

### `scripts/` — Scripts d'exécution ponctuelle
Scripts à lancer en ligne de commande, indépendants de l'interface Streamlit.

| Fichier | Rôle |
|---|---|
| `init_db.py` | Initialise la base de données et crée toutes les tables |
| `clean_MS1.py` | Nettoie et filtre un le fichier Excel brut d'annotations |
| `load_MS1.py` | Charge un CSV nettoyé et insère toutes les entrées dans la base de données |
| `export_MS1.py` | Extrait les données de la base et les exporte en CSV compatible MZmine |

---

# **Create the conda environment**
```bash
   conda create --file environment.yml
   conda activate lipid_database
```
