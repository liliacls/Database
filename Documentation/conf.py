# Fichier de configuration pour le générateur de documentation Sphinx.

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Informations sur le projet -----------------------------------------------------

project = 'BacLipidAPP'
copyright = '2026, Lilia CHALES'
author = 'Lilia CHALES'

version = '1.0.0'
release = '1.0.0'

# -- Configuration générale ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
autodoc_member_order = 'bysource'

# -- Options pour la sortie HTML -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
