Export
=======

Fichier source : ``app/pages/3_Export.py``

.. note::
   Cette page contient la documentation du module Streamlit (``3_Export.py``).
   La majorité du code n'est pas écrit sous forme de fonction, il n'est donc pas possible d'utiliser ``automodule``
   pour générer cette page automatiquement. La documentation ci-dessous est rédigée manuellement
   à partir du code source.

Vue d'ensemble
--------------

Ce module Streamlit (**MODULE 3**) permet de filtrer les annotations de
**BacLipidDB** par catégorie, classe et sous-classe lipidique, niveau MS,
mode d'ionisation et plage de m/z. Les annotations filtrées peuvent ensuite être visualisées
puis téléchargées dans des formats compatible avec MZmine .csv, .msp.


Chargement des données
------------------------

``_load_data(_engine)`` s'appuie sur :func:`utils.data_access.load_database` (la vue jointe
commune ``Annotation`` + ``Lipid`` + ``Detection``, mise en cache via ``st.cache_data(ttl=60)``
et partagée avec les pages 2_BacLipidDB et 5_Management), renomme certaines colonnes (``Lipid_name`` → ``name``,
``Formula`` → ``formula``, ``Precursor_MZ`` → ``mz``, ``Neutral_mass`` → ``neutral_mass``). Les lignes conservées sont :
``name``, ``formula``, ``Lipid_category``, ``Lipid_class``, ``Lipid_subclass``, ``mz``, ``neutral_mass``, ``MS_level``, ``Ionisation_mode``, ``Adduct``, ``RT``, ``CCS`` et
``Num_Peaks``. Les colonnes ``RT``/``CCS``/``Num_Peaks`` valent ``None`` si non renseignés en base, ``Num_Peaks`` n'est renseigné que pour les détections ``MS2``. Si le chargement échoue, un message ``st.error`` est affiché
(« *Unable to load data from the database: {e}* ») et la page s'arrête (``st.stop()``). Sinon si la base est vide, un message ``st.info`` est affiché à la place (« *The database contains no data yet.* »).

Filtres
-------

Les filtres sont répartis sur deux lignes de 3 colonnes (``st.columns``) :

- **Lipid category**, **Lipid class**, **Lipid subclass** (``st.multiselect``) : les valeurs
  possibles sont extraites des colonnes présente dans la base de données chargée. Une option
  ``(None)`` est ajoutée si la colonne contient des valeurs manquantes.
- **MS level** et **Ionisation mode** (``st.multiselect``) : mêmes principes mais sans option
  ``(None)`` car toutes les lignes ont une valeur pour ces colonnes.
- **Precursor m/z range** : deux ``st.number_input`` (``Min m/z`` / ``Max m/z``,
  format ``%.6f``), initialisés au min/max de la colonne ``mz``. Les deux valeurs sont triées (``min``/``max``) pour former ``mz_range``.

Application des filtres
-------------------------

Le DataFrame ``df_all`` est copié dans ``df_filtered``, puis chaque filtre est appliqué
l'un après l'autre (chaque étape réduit ``df_filtered`` obtenu à l'étape précédente) :

- **Lipid_category**, **Lipid_class**, **Lipid_subclass** : si aucune valeur n'est
  sélectionnée pour la colonne, aucun filtre n'est appliqué (toutes les lignes sont
  conservées). Sinon, seules les lignes dont la valeur figure parmi les filtres sélectionnés
  sont conservées. Si l'option ``(None)`` fait partie de la sélection, les lignes où la
  colonne est manquante (``NaN``) sont conservées en plus.
- **MS_level**, **Ionisation_mode** : même principe, mais sans option ``(None)`` (ces
  colonnes sont toujours renseignées). Aucun filtre n'est appliqué si la sélection est vide,
  sinon seules les lignes dont la valeur figure parmi les filtres sélectionnés sont conservées.
- **mz** : seules les lignes dont la valeur de ``mz`` est comprise entre les deux bornes
  de ``mz_range`` (bornes incluses) sont conservées. Ce filtre est toujours appliqué
  (les bornes valent par défaut le min/max de la colonne, donc rien n'est exclu tant que
  l'utilisateur ne les modifie pas).

Aperçu
------

``st.subheader`` affiche le nombre de lignes filtrées. Si aucune ligne ne correspond,
un message ``st.warning`` est affiché et la page s'arrête. Sinon, un extrait des colonnes
``name``, ``formula``, ``mz``, ``MS_level``, ``RT``, ``CCS`` et ``Num_Peaks`` est affiché
via ``st.dataframe`. ``Num_Peaks`` vaut ``None`` pour les lignes ``MS1`` (le nombre de pics n'a de sens qu'en MS2).

Téléchargement
--------------

Trois boutons de téléchargement (``st.columns`` à 3 colonnes) :

- **CSV (MS1 + MS2)** : colonnes ``neutral_mass``, ``mz``, ``formula``, ``name`` de
  l'ensemble de ``df_filtered``, exportées en CSV. Toujours disponible dès que des données sont présentes dans BacLipidDB.

- **MSP (MS2)** : disponible uniquement si ``df_filtered`` contient au moins une ligne
  ``MS2`` (bouton ``st.button`` désactivé sinon). Généré par ``generate_msp()`` (mise en
  cache via ``st.cache_data(ttl=60)``), qui délègue à :func:`utils.msp_export.generate_msp`
  avec les catégories, classes et sous-classes sélectionnées, ``mz_range`` ainsi que les
  modes d'ionisation sélectionnés (``selected_ionisation_modes``). Le filtre **MS level**
  choisi par l'utilisateur n'est en revanche pas transmis à cette fonction : elle filtre
  elle-même en dur sur ``Detection.MS_level == "MS2"``, si bien que ce filtre n'aurait de
  toute façon aucun effet sur cet export. Cette fonction ne conserve que les annotations ``MS2`` possédant au moins un fragment, et écrit
  pour chacune un bloc ``Name``/``PrecursorMZ``/``MW``/``ExactMass``/``Ion_mode``/``RT``/``CCS``/``Num Peaks``
  (``RT``/``CCS`` omis si absents) suivi de la liste des fragments (``MZ Intensity``).
  ``Ion_mode`` reprend le mode d'ionisation de la détection, encodé comme dans les fichiers
  MSP de LipidMaps (``P`` pour ``Positive``, ``N`` pour ``Negative``).
- **CSV (CCS + RT)** : disponible uniquement si ``df_filtered`` contient au moins une ligne
  avec à la fois ``RT`` et ``CCS`` renseignés (bouton désactivé sinon). Colonnes
  ``neutral_mass``, ``mz``, ``formula``, ``name``, ``RT``, ``CCS`` des lignes concernées,
  qu'il s'agisse d'annotations ``MS1`` ou ``MS2``. MZmine n'acceptant pas un CSV MS1 où
  certaines lignes ont des valeurs RT/CCS et d'autres non, cet export est volontairement
  séparé du CSV MS1 + MS2 ci-dessus.

Chaque fichier est nommé ``annotation_export_<niveau>_<date du jour AAAAMMJJ>.<ext>``
(``MS1+MS2``, ``MS2`` ou ``CCS_RT``).

Fonctions internes
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Fonction
     - Description
   * - ``_load_data(_engine: Engine) -> pandas.DataFrame``
     - Recadre et renomme les colonnes utiles de la vue jointe renvoyée par
       :func:`utils.data_access.load_database`.
   * - ``generate_msp(_engine, categories, classes, sub_classes, mz_range, ionisation_modes) -> str``
     - Met en cache l'appel à :func:`utils.msp_export.generate_msp` pour l'export MSP
       des détections MS2 correspondant aux filtres.

Dépendances internes
----------------------

- :func:`utils.data_access.load_database`
- :mod:`config` (``get_engine``)
- :func:`utils.msp_export.generate_msp`