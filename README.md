# Lipid Database Project


# Architecture 

📁 projet/                           
├── 📁 data_cleaning/                     🠖 Traitement des tableurs d'annotations
  └── 📄 tableur_MS1.py     
├── 📁 data_loading/                      🠖 Peuplement de la base et export en .csv .msp (export à séparer)
  ├── 📄 data_MS1_1.py 
  ├── 📄 data_MS1_2.py 
  └── 📄 data_MS1_3.py 
├── 📁 database_app/                      🠖 Interface
  └── 📄 app.py 
├── 📁 database_modeling/                 🠖 Modélisation de la base de données
  └── 📄 Entity_Relationship.dbml 
├── 📁 database_models/                   🠖 Création de la structure de la base de données
  ├── 📄 __init__.py 
  ├── 📄 complete_model.py 
  ├── 📄 database.py 
  └── 📄 partial_model.py 
├── 📄 .gitignore 
└── 📄 README.md
