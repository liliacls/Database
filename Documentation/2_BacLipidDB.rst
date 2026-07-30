BacLipidDB
============

Fichier source : ``app/pages/2_BacLipidDB.py``

.. note::
   Cette page contient la documentation du module Streamlit (``2_BacLipidDB.py``).
   La majorité du code n'est pas écrit sous forme de fonction, il n'est donc pas possible d'utiliser ``automodule`` 
   pour générer cette page automatiquement. La documentation ci-dessous est rédigée manuellement
   à partir du code source.

Vue d'ensemble
--------------

Ce module Streamlit (**MODULE 2**) permet d'explorer le contenu de la base de données
**BacLipidDB**, via un sélecteur (``st.radio``) proposant :

- une vue des 3 tables de la base de données : ``Detection``, ``Fragment``, ``Lipid`` ;
- **Full view** : une vue jointe combinant les champs des tables ``Detection``et ``Lipid``,
  colorée par lot d'import et accompagnée de 4 graphiques ;
- **History** : l'historique des imports passés.

Tables brutes
-------------

Pour ``Detection``, ``Fragment`` et ``Lipid``, le contenu de la table est lu
directement depuis BacLipidDB via :func:`pandas.read_sql_table` puis affiché avec
:func:`st.dataframe`. Les colonnes numériques suivantes sont formatées via
``st.column_config.NumberColumn`` :

- ``Precursor_MZ``, ``Neutral_mass``, ``MZ``, ``Intensity`` : 6 décimales
- ``Monoisotopic_mass`` : 8 décimales
- ``RT``, ``CCS`` : 4 décimales
- ``Molecular_weight`` : 0 décimale

Si la table ne contient aucune ligne, un message ``st.info("This table contains no data yet.")``
est affiché à la place.

Full view
---------

Importation des données
~~~~~~~~~~~~~~~~~~~~~~~~~

La fonction ``_load_data(_engine)`` s'appuie sur :func:`utils.data_access.load_database`
(requête SQLAlchemy commune sur ``Annotation``, avec chargement des relations avec les tables
``lipid`` et ``detection``, partagée avec les pages **3_Export** et **5_Management** pour éviter de
dupliquer cette requête). Cette fonction ne conserve que les colonnes :
``Detection_ID``, ``Lipid_name``, ``Formula``, ``FA_composition``, ``Lipid_class``,
``Lipid_subclass``, ``Lipid_category``, ``Precursor_MZ``, ``Adduct``, ``Neutral_mass``,
``Molecular_weight``, ``Monoisotopic_mass``, ``MS_level``, ``Ionisation_mode``, ``Num_Peaks``,
``RT``, ``CCS``. Les autres clé primaires (_ID) et étrangères (_id) ne sont pas affichées pour question de lisibilité. 

.. list-table:: Exemple
   :header-rows: 1
   :widths: 30 70

   * - Appel
     - Résultat
   * - ``load_database(engine)``
     - DataFrame complet : une ligne par ``Annotation``, avec en plus ``Annotation_ID`` et
       ``Lipid_ID``
   * - ``_load_data(engine)``
     - Le même DataFrame, restreint aux 17 colonnes listées ci-dessus

.. note::
   Avant affichage, la page ajoute deux colonnes supplémentaires à ce DataFrame, absentes de
   ``_load_data`` : ``Source_file`` (nom du fichier importé correspondant au lot d'import de la
   ligne, voir ci-dessous) et ``Import_group`` (voir `Groupe d'import`_). Ces deux colonnes sont
   donc visibles dans le tableau **Full view** affiché à l'utilisateur, en plus des 17 colonnes de
   ``_load_data``.

Colorisation par lot d'import
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chaque ligne du tableau **Full view** est colorée selon le fichier d'import (``History``)
auquel appartient sa ``Detection_ID`` :

- :func:`utils.history.load_history` charge l'historique des imports depuis ``history.json``
  (``config.HISTORY_PATH``, lu indirectement par ``load_history``) ;
- ``_batch_map(history)`` associe chaque ``Detection_ID`` à l'indice du lot
  d'import auquel il appartient (champ ``detection_ids`` de chaque entrée de l'historique) ;
- la colonne ``Source_file`` est construite à partir de ce même indice de lot, via un
  dictionnaire ``{indice: nom de fichier}`` dérivé de l'historique (``"Unknown"`` si la
  ``Detection_ID`` n'a pas de lot correspondant) ;
- la fonction ``_row_color(row)`` applique, via ``df.style.apply(..., axis=1)``, une couleur de
  fond calculée par ``_color(index)`` à chaque ligne selon son lot.

Exemple (``_batch_map``)
`````````````````````````

.. code-block:: pycon

   >>> history = [
   ...     {"filename": "batch1.csv", "detection_ids": [101, 102, 103]},
   ...     {"filename": "batch2.csv", "detection_ids": [104, 105]},
   ... ]
   >>> _batch_map(history)
   {101: 0, 102: 0, 103: 0, 104: 1, 105: 1}

``_color(index)`` ne repose pas sur une palette figée : la teinte (``hue``) est calculée
par ``(index * 0.618) % 1.0`` (technique du *golden angle* avec le nombre d'or conjugé *0.618*) puis convertie en couleur pastel via :func:`colorsys.hls_to_rgb` (luminosité 0.85,
saturation 0.55 fixes).

Exemple (``_color(1)``)
````````````````````````

#. ``hue = (1 * 0.618) % 1.0 = 0.618``
#. :func:`colorsys.hls_to_rgb` (0.618, 0.85, 0.55) convertit HLS en RGB (flottants dans [0, 1)) :
   ``r = 0.7675``, ``g = 0.8157``, ``b = 0.9325``
#. chaque flottant est mis à l'échelle [0, 255] et arrondi à l'entier le plus proche :
   ``r = 196``, ``g = 208``, ``b = 238``
#. chaque entier est formaté en paire hexadécimale sur 2 chiffres : ``196 = c4``,
   ``208 = d0``, ``238 = ee`` → ``#c4d0ee``

Un encadré **color caption** (``st.expander``) rappelle, pour chaque fichier importé, sa
couleur, son nom, sa date d'import, son nombre de lignes et son intégrateur.

.. note::
   Cette coloration par lot ne concerne que les lignes du tableau **Full view**. Les graphiques 1 à 3 (masses),
   plus bas, utilisent un code couleur différent, à 3 catégories fixes : voir `Groupe d'import`_.

Exemple
```````

Soit un historique de 2 imports, et ``df`` (après ``reset_index``) contenant 4 lignes. Pour
chaque ligne, ``caption_values[row.name]`` donne le lot d'import de sa ``Detection_ID`` :

.. list-table::
   :header-rows: 1
   :widths: 10 15 20 25 20

   * - ``row.name``
     - ``Detection_ID``
     - ``caption_values[row.name]``
     - Lot d'import
     - Couleur appliquée
   * - 0
     - 1
     - 0.0
     - Import 1 (plus ancien)
     - ``#eec4c4``
   * - 1
     - 2
     - 1.0
     - Import 2 (dernier import)
     - ``#c4d0ee``
   * - 2
     - 3
     - NaN
     - aucun (``Detection_ID`` absente de l'historique)
     - aucune (cellule non colorée)
   * - 3
     - 4
     - 0.0
     - Import 1 (plus ancien)
     - ``#eec4c4``

Pour la ligne d'index 1, ``_row_color`` lit ``caption_values[1] = 1.0``, en déduit la couleur
du lot 1 via ``_color(1)`` et l'applique à toutes les cellules de cette ligne.

.. note::
   En usage normal, ce cas (``Detection_ID`` absente de l'historique) ne devrait pas se
   produire : chaque intégration (``1_Integration.py``) ajoute automatiquement une entrée à
   ``history.json`` listant les ``Detection_ID`` insérées. Il ne survient qu'en cas
   d'incohérence entre la base et ``history.json``. La ligne 3 de l'exemple ci-dessus illustre le comportement du code face à un scénario inattendu.

Groupe d'import
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les graphiques 1 à 3 ne colorent pas les points par lot d'import individuel
comme le tableau **Full view**, mais par groupe, via une colonne ``Import_group`` calculée par
``_group(batch_id)`` à partir de ``caption_values`` et de l'indice du dernier lot
(``last_batch_id = len(history) - 1``) :

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - ``_group(batch_id)``
     - Condition
     - Couleur (``COLORS``)
   * - ``"Unknown"``
     - ``batch_id`` est ``NaN`` (``Detection_ID`` absente de l'historique)
     - ``#898781`` (gris)
   * - ``"Latest import"``
     - ``int(batch_id) == last_batch_id``
     - ``#e34948`` (rouge)
   * - ``"Other imports"``
     - tout autre ``batch_id``
     - ``#2a78d6`` (bleu)

Exemple
`````````````````

Avec le même historique de 2 imports que ci-dessus (``last_batch_id = 1``) :

.. list-table::
   :header-rows: 1
   :widths: 15 20 30 20

   * - ``Detection_ID``
     - ``caption_values``
     - ``_group(...)``
     - Couleur
   * - 1
     - 0.0
     - ``"Other imports"``
     - ``#2a78d6``
   * - 2
     - 1.0
     - ``"Latest import"``
     - ``#e34948``
   * - 3
     - NaN
     - ``"Unknown"``
     - ``#898781``

Graphique 1 - Masse mesurée vs masse théorique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nuage de points (:func:`plotly.express.scatter`) de ``Neutral_mass`` (masse neutre mesurée,
calculée à partir de ``Precursor_MZ`` et de l'adduit ``Adduct``) en fonction de ``Monoisotopic_mass`` (masse monoisotopique théorique
du lipide de référence calculée à partir de la formule chimique), coloré par ``Import_group``
(voir `Groupe d'import`). Le survol affiche ``Lipid_name``, ``Lipid_class``, l'écart
``Delta (Da)`` (``Neutral_mass - Monoisotopic_mass``) et l'erreur ``Error (ppm)``
(``Delta / Monoisotopic_mass * 1e6``). Une droite ``y = x`` (:class:`plotly.graph_objects.Scatter`,
trait pointillé) sert de référence visuelle pour l'écart entre les masses.

Graphique 2 - Erreur de masse (ppm) vs masse neutre
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nuage de points (:func:`plotly.express.scatter`) de l'erreur relative ``Error (ppm)`` (même
calcul que pour le graphique 1) en fonction de ``Neutral_mass``, coloré par ``Import_group``. Le
survol affiche ``Lipid_name``, ``Lipid_class`` et ``Error (ppm)``.

Graphique 3 - Erreur de masse (Da) vs masse neutre
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Même principe que le graphique 2, mais en ordonnée l'écart absolu ``Delta (Da)`` (au lieu de
l'erreur relative ``Error (ppm)``), toujours en fonction de ``Neutral_mass`` et coloré par
``Import_group``. Le survol affiche ``Lipid_name``, ``Lipid_class`` et ``Delta (Da)``.

Ce graphique est suivi d'un tableau **Mass error table** listant ``Lipid_name``, ``Formula``,
``Neutral_mass``, ``Monoisotopic_mass``, ``Delta (Da)``, ``Error (ppm)`` et ``Source_file``
(nom du fichier d'import, voir `Colorisation par lot d'import`_), trié par valeur
absolue de ``Error (ppm)`` décroissante, pour faire ressortir en premier les annotations dont la
masse mesurée s'écarte le plus de la masse théorique.

Graphique 4 - Diagramme de Van Krevelen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nuage de points H/C en fonction de O/C, coloré par ``Lipid_class``. Les ratios atomiques
sont calculés à partir de la colonne ``Formula`` : ``_formula(formula)`` parse la formule
chimique (regex ``([A-Z][a-z]?)(\d*)``) en un dictionnaire élément → nombre d'atomes, dont on
extrait les comptes de C, H et O (0 si absent). Seules les lignes avec au moins un atome de
carbone (``C > 0``) sont conservées, afin d'éviter une division par zéro sur ``H/C`` et ``O/C``.

Exemple (parsing de formule)
`````````````````````````````

.. list-table::
   :header-rows: 1
   :widths: 25 30 10 10 10 15

   * - ``Formula``
     - ``_formula(formula)``
     - C
     - H
     - O
     - H/C, O/C
   * - ``C42H82NO8P``
     - ``{"C": 42, "H": 82, "N": 1, "O": 8, "P": 1}``
     - 42
     - 82
     - 8
     - 1.952, 0.190

History
-------

Affiche, via :func:`pandas.DataFrame` construit à partir de :func:`utils.history.load_history`,
la liste des imports passés : nom de fichier, date (:func:`pandas.to_datetime`), niveau MS, mode
d'ionisation, nombre de lignes insérées et nom de l'intégrateur. Si
l'historique est vide, un message ``st.info("No imports recorded yet.")`` est affiché à la place.

Fonctions internes
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Fonction
     - Description
   * - ``_load_data(_engine: Engine) -> pd.DataFrame``
     - Charge la vue jointe complète via :func:`utils.data_access.load_database` et n'en
       conserve que certaines colonnes.
   * - ``_formula(formula: str) -> dict``
     - Parse une formule chimique en un dictionnaire symbole d'élément → nombre d'atomes.
   * - ``_batch_map(history: list[dict]) -> dict[int, int]``
     - Associe chaque ``Detection_ID`` à l'indice du lot d'import auquel il appartient
       (utilisé pour la colorisation de **Full view**).
   * - ``_group(batch_id: float) -> str``
     - Classe le lot d'import d'une ligne dans l'une des 3 catégories ``"Latest import"``,
       ``"Other imports"`` ou ``"Unknown"``, utilisées pour colorer les graphiques 1 à 3 (voir
       `Groupe d'import`_).
   * - ``_row_color(row: pd.Series) -> list[str]``
     - Callback de style (``df.style.apply(..., axis=1)``) qui renvoie la couleur de fond CSS
       à appliquer à chaque cellule d'une ligne de **Full view**, selon son lot d'import.
   * - ``_color(index: int) -> str``
     - Génère une couleur pastel (hex) pour un indice de lot, en espaçant les teintes par le
       nombre d'or conjugué (*golden angle*) plutôt que via une palette figée (voir
       `Colorisation par lot d'import`_).

Dépendances internes
----------------------

- :func:`utils.data_access.load_database`
- :func:`utils.history.load_history`
- :mod:`config` (``get_engine``, ``PROJECT_ROOT`` importés directement ; ``HISTORY_PATH`` est
  utilisé indirectement, à l'intérieur de ``load_history``)