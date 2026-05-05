# Lipid Database Project


# **Architecture**
```
projet/
├── 📁 data_cleaning/          → Traitement des tableurs d'annotations
│   └── 📄 tableur_MS1.py
├── 📁 data_loading/           → Peuplement de la base de données
│   ├── 📄 data_MS1_1.py
│   ├── 📄 data_MS1_2.py
    └── 📄 data_MS1_3.py
├── 📁 data_export/            → Export en .csv et .msp
│   └── 📄 data_MS1_3.py
├── 📁 database_app/           → Interface
│   └── 📄 app.py
├── 📁 database_modeling/      → Modélisation de la base de données
│   └── 📄 Entity_Relationship.dbml
├── 📁 database_models/        → Création de la structure de la base de données
│   ├── 📄 complete_model.py
│   ├── 📄 database.py
│   └── 📄 partial_model.py
├── 📄 .gitignore
├── 📄 README.md
└── 📄 environment.yml
```
# **Create the conda environment**
```bash
   conda create --file environment.yml
   conda activate lipid_database
```
