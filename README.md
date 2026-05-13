# BacLipidDB Project

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
├── 📁 services/
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
# **Create the conda environment**
```bash
   conda create --file environment.yml
   conda activate lipid_database
```
