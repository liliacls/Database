# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = 'BacLipidAPP'
copyright = '2026, Lilia CHALES'
author = 'Lilia CHALES'

version = '1.0.0'
release = '1.0.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for LaTeX/PDF output ---------------------------------------------
# pdflatex ne sait pas rendre les emojis utilisés dans le texte, substitution par des symboles LaTeX équivalents pour le PDF.
latex_elements = {
    'preamble': r'''
\usepackage{newunicodechar}
\newunicodechar{✅}{\checkmark}
\newunicodechar{❌}{\texttimes}
\newunicodechar{⬜}{\ensuremath{\square}}
\newunicodechar{🔄}{}
''',
}
