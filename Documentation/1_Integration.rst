Data_Integration
=================

Fichier source : ``app/pages/1_Integration.py``

.. note::
   Cette page contient la documentation du module Streamlit (``1_Integration.py``).
   La majorité du code n'est pas écrit sous forme de fonction, il n'est donc pas possible d'utiliser ``automodule``
   pour générer cette page automatiquement. La documentation ci-dessous est rédigée manuellement
   à partir du code source.

Vue d'ensemble
--------------

Ce module Streamlit (**MODULE 1**) permet d'intégrer un fichier d'annotations
lipidiques, **MS1** ou **MS2**, dans la base de données **BacLipidDB**, via un
workflow guidé en 5 étapes affiché à la fois dans le corps de la page et dans
la barre latérale (icônes ✅ / ⬜). Le niveau MS choisi à l'étape 1 détermine
le format de fichier attendu et le chemin de traitement des étapes suivantes.

Colonnes du fichier d'entrée
-----------------------------

**Fichier MS1** (``.csv``/``.tsv``/``.xlsx``, une ligne = une annotation)

Colonnes obligatoires (``REQUIRED_COLUMNS``), doivent être présentes dans le fichier importé
(voir ``4_Resources.py``) :

- ``Lipid_Name``
- ``Formula``
- ``Precursor_MZ``
- ``Lipid_category``
- ``Lipid_class``
- ``Lipid_subclass``
- ``Adduct``

Parmi celles-ci, ``Lipid_Name``, ``Formula``, ``Precursor_MZ`` et ``Adduct``
(``NON_EMPTY_COLUMNS``) ne doivent contenir aucune cellule vide.

Colonnes optionnelles : ``RT``, ``CCS``. Si elles sont présentes dans le
fichier importé, elles sont conservées telles quelles dans le tableau et
transmises à :func:`utils.loading_MS1.DB_MS1`, qui les insère dans la table
``Detection`` (``None`` si absentes ou vides).

**Fichier MS2** (``.csv``/``.tsv`` organisé en blocs empilés, un bloc = un scan)

Le fichier est parsé par :func:`utils.loading_MS2.ms2_parsing`, qui valide
elle-même chaque bloc. Chaque bloc commence par une ligne d'en-tête
``Scan #<identifiant>`` dont l'identifiant est extrait sous la clé
``scan_id``. Ce ``scan_id`` n'est utilisé qu'en interne (voir
`Workflow`_, étape 4) : il n'est ni affiché ni modifiable dans l'application.
Champs obligatoires par scan : ``Lipid_Name``,
``Precursor_MZ``, ``Formula``, ``Adduct``, ``Lipid_category``,
``Lipid_class``, ``Lipid_subclass``, ``Num_peaks``, suivis d'un en-tête
``m/z`` / ``Intensity`` et d'au moins une ligne de fragment. Champs optionnels :
``FA_composition``, ``RT``, ``CCS``.

Éléments d'interface communs
-----------------------------

- **Barre latérale** : récapitulatif du workflow (icône par étape) et bouton
  **Reset 🔄**, qui effectue trois actions :

  - remet les widgets de l'étape 1 à ``None`` (``ms_level``, ``ion_mode``) et à ``""``
    (``integrator_name``, ``file_row_name``) ;
  - supprime de ``st.session_state`` toutes les clés calculées listées dans
    ``RESET_KEYS``, ce qui efface l'état des étapes 2 à 5 ;
  - incrémente ``UPLOADER_VERSION``, ce qui change la ``key`` du widget
    ``st.file_uploader`` de l'étape 2
    (``key=f"file_uploader_{st.session_state.get(UPLOADER_VERSION, 0)}"``) et
    le vide ainsi indirectement - voir :doc:`Home`, section
    *Fonctionnement général de Streamlit*, pour le détail de ce mécanisme
    (``st.file_uploader`` n'autorisant pas d'écriture directe dans
    ``st.session_state``).

- **En-tête** : bandeau ``MODULE 1 : Data integration page``.
- **Barre de progression** : nombre d'étapes complétées sur 5.
- **Encadré d'aide** (``st.expander``) : résumé du workflow en 5 points.

Workflow
--------

1. **Settings**
   Sélection du niveau MS (``ms_level`` : ``MS1`` ou ``MS2``), du mode
   d'ionisation (``ion_mode`` : ``Positive`` / ``Negative``), du nom de
   l'intégrateur (``integrator_name``) et du nom du fichier expérimental
   d'origine (``file_row_name``). Tant que ces quatre champs ne sont pas
   renseignés, la page s'arrête (``st.stop()``).

   Une fois la complétion automatique de l'étape 4 effectuée (``df_complete``
   présent en session), ces quatre champs sont verrouillés (``disabled``)
   afin de garantir la cohérence entre les colonnes calculées et les réglages
   utilisés pour les calculer.

2. **File upload**
   Chargement d'un fichier via ``st.file_uploader`` (clé versionnée par
   ``UPLOADER_VERSION`` pour pouvoir être réinitialisé par le bouton
   **Reset**), dont les types acceptés dépendent du niveau MS choisi à
   l'étape 1 : ``.xlsx``, ``.csv`` ou ``.tsv`` pour ``MS1``, ``.csv`` ou
   ``.tsv`` uniquement pour ``MS2`` (``ms2_parsing`` ne sait lire que du
   texte délimité, pas le format binaire ``.xlsx``). Le rechargement du fichier (parsing) n'est
   déclenché que si son identifiant  (``uploaded_file.file_id``) ou le
   niveau MS (``df_ms_level``) diffère de la dernière valeur connue.

   - ``MS2`` → :func:`utils.loading_MS2.ms2_parsing` (liste de scans stockée
     sous la clé ``ms2``) ;
   - ``MS1`` → :func:`pandas.read_csv` (``.csv``/``.tsv``) ou
     :func:`pandas.read_excel` (``.xlsx``), stocké sous la clé ``ms1``.

   Le chargement d'un nouveau fichier efface les clés ``RELOAD_RESET_KEYS`` (résultats
   calculés en aval) ainsi que la donnée de l'autre niveau MS (``ms1`` si l'on
   bascule vers ``MS2``, ``ms2`` si l'on bascule vers ``MS1``), tout en
   conservant les réglages de l'étape 1.

   Pour ``MS1`` uniquement, les colonnes ``STRIP_COLUMNS`` (``Lipid_category``,
   ``Lipid_class``, ``Lipid_subclass``), si elles sont présentes dans le
   fichier, sont immédiatement débarrassées des espaces superflus en début/fin
   de valeur (``str.strip()``). Ceci évite que des valeurs identiques mais
   diversement espacées (ex. ``"Glycerophospholipids"`` et
   ``"Glycerophospholipids "``) ne soient comptées comme des catégories,
   classes ou sous-classes distinctes dans la légende des histogrammes de
   l'étape 4.

3. **Verification**

   - **MS2** : la validation est effectuée par ``ms2_parsing``. La page affiche
     directement un tableau des scans parsés (``st.expander``,
     colonnes ``Precursor_MZ``, ``Formula``, ``Lipid_Name``,
     ``FA_composition``, ``Adduct``, ``Lipid_category``, ``Lipid_class``,
     ``Lipid_subclass``, ``RT``, ``CCS``, ``Num_Peaks``).
   - **MS1** : contrôle, dans l'ordre, la présence de toutes les colonnes de
     ``REQUIRED_COLUMNS``, l'absence de cellules vides dans
     ``NON_EMPTY_COLUMNS``, puis la validité numérique de la colonne
     ``Precursor_MZ`` (:func:`pandas.to_numeric`, conversion en ``float``).

   En cas d'erreur, un message détaillé est affiché et la page s'arrête.
   L'utilisateur doit corriger puis recharger son fichier.

4. **Completion**
   Au clic sur **Run automatic completion**, calcul des colonnes dérivées :

   - ``Molecular_weight`` (via :func:`utils.molecular_weight.molecular_weight`)
     et ``Monoisotopic_mass`` (via :func:`utils.monoisotopic.monoisotopic_mass`),
     à partir de ``Formula``. Si une formule est invalide, la page affiche une erreur et s'arrête sans stocker le
     résultat.
   - ``Adduct`` et ``Neutral_mass``, résolus pour toutes les lignes/tous les
     scans d'un coup par :func:`utils.neutral_mass.resolve_adducts` (voir
     `Fonctions internes`_). Si un ou plusieurs adduits sont invalides, la
     page liste chaque ligne/scan en erreur et s'arrête sans stocker les
     résultats, même ceux valides. L'utilisateur doit corriger les adduits dans le fichier et recharger.
   - Pour ``MS1`` uniquement : ``MS_level`` (valeur fixe ``ms_level``),
     ``Num_Peaks`` (fixé à ``0``), ``Ionisation_mode`` (valeur fixe
     ``ion_mode``). Pour ``MS2``, seul ``Num_Peaks`` provient réellement du
     fichier parsé (nombre de fragments de chaque scan, issu du champ
     ``Num_peaks`` de son bloc). ``Ionisation_mode`` reste fixé à la valeur
     choisie en étape 1 (``ion_mode``), exactement comme pour MS1.
     ``MS_level`` vaut simplement ``"MS2"``.

   Le tableau résultat (``df_complete``) est ensuite modifiable via
   ``st.data_editor``. Les colonnes calculées ou fixées (``Precursor_MZ``,
   ``Neutral_mass``, ``Molecular_weight``, ``Monoisotopic_mass``, ``Formula``,
   ``MS_level``, ``Num_Peaks``, ``Ionisation_mode``, ``Adduct``) sont en
   lecture seule. Restent donc modifiables :

   - **MS1** : ``Lipid_Name``, ``Lipid_category``, ``Lipid_class``,
     ``Lipid_subclass``, ``RT``, ``CCS`` ;
   - **MS2** : ``Lipid_Name``, ``FA_composition``, ``Lipid_category``,
     ``Lipid_class``, ``Lipid_subclass``, ``RT``, ``CCS``.

   Le ``scan_id`` de chaque bloc MS2 (voir `Colonnes du fichier d'entrée`_)
   n'apparaît pas dans ce tableau : il reste uniquement dans
   ``st.session_state["ms2"]`` et n'est utilisé qu'en interne, à l'étape 5,
   pour associer chaque ligne éditée au scan correspondant par position.

   Le nombre de lignes est figé pour MS2 (``num_rows="fixed"``, un scan = une
   ligne) et modifiable pour MS1 (``num_rows="dynamic"``, suppression de
   lignes possible).

   Pour MS1, un ``st.caption`` rappelle que la suppression de ligne est
   possible mais pas l'ajout. Les lignes créées via le bouton **+** de
   l'éditeur ne peuvent pas être validées car ``Formula``, ``Precursor_MZ`` et
   ``Adduct`` sont verrouillés (colonnes calculées non saisissables
   manuellement). Pour ajouter un lipide, il faut corriger le fichier source
   et le recharger (étape 2).

   Le bouton **Validate data** revérifie l'absence de cellules vides dans
   ``NON_EMPTY_COLUMNS`` sur les données éditées avant de les stocker dans
   ``df_validated``. Une fois validées, un résumé est affiché : métriques
   (nombre total de lipides, de catégories, classes et sous-classes) et trois
   histogrammes horizontaux (:func:`plotly.express.bar`, couleur selon
   ``CHART_COLOR_SCALE``) répartissant les lipides par catégorie, classe et
   sous-classe.

5. **Integration**
   Insertion des données validées dans les tables ``Detection``, ``Lipid``,
   ``Annotation`` (et ``Fragment`` pour MS2) :

   - **MS1** : :func:`utils.loading_MS1.DB_MS1` reçoit directement le
     DataFrame validé (``df_validated``).
   - **MS2** : le tableau ``df_validated`` ne contient que les colonnes de
     métadonnées affichées à l'étape 4. Les fragments (m/z/intensité) de
     chaque scan, eux, n'existent que dans ``st.session_state["ms2"]`` (liste
     de dictionnaires produite par le parsing) : ils n'apparaissent jamais
     dans ce tableau.

     Or :func:`utils.loading_MS2.DB_MS2` a besoin des dictionnaires complets
     pour insérer les fragments en base. La page reporte donc d'abord les
     valeurs de ``df_validated`` (potentiellement modifiées par
     l'utilisateur) dans les dictionnaires de ``st.session_state["ms2"]``.
     Chaque ligne du tableau est associée au scan de même position
     (``scans[pos]``). Cette correspondance par position est fiable car
     ``num_rows="fixed"`` empêche tout ajout ou suppression de ligne à
     l'étape 4 : l'ordre reste donc identique entre les deux structures.

     Seuls les champs présents dans le tableau (``lipid_name``,
     ``fa_composition``, ``lipid_category``, ``lipid_class``,
     ``lipid_subclass``, ``rt``, ``ccs``, ``molecular_weight``,
     ``monoisotopic_mass``, ``neutral_mass``, ``adduct``, ``ion_mode``) sont
     ainsi écrasés dans chaque dictionnaire de scan. Les fragments, absents
     du tableau, restent donc inchangés. :func:`utils.loading_MS2.DB_MS2`
     est ensuite appelée avec cette liste de scans mise à jour.

   Dans les deux cas, la fonction reçoit également le nom du fichier importé,
   ``integrator_name`` et ``file_row_name``, et se charge en interne de
   l'historique et de la sauvegarde de la base. En cas de succès,
   ``integration_done`` passe à ``True`` et des ballons (``st.balloons``)
   sont affichés une seule fois (flag ``show_balloons`` consommé via
   ``st.session_state.pop``). Une fois l'intégration finie, une nouvelle intégration est proposée
   (bouton **Reset** de la barre latérale).

   Si :func:`utils.loading_MS1.DB_MS1` ou :func:`utils.loading_MS2.DB_MS2`
   lève une :class:`utils.exceptions.PostIntegrationError`, les données sont
   déjà commitées en base (l'intégration a réussi), mais la sauvegarde ou
   l'écriture de l'historique post-commit a échoué. Ce cas est traité comme un
   succès partiel : ``integration_done`` passe quand même à ``True`` (sans
   ballons), et le message de l'exception est stocké dans
   ``integration_warning`` puis affiché sous forme d'avertissement
   (``st.warning``) précisant qu'il ne faut **pas** réintégrer le fichier
   (les données sont déjà en base) et qu'il faut utiliser le bouton
   **Reset** pour repartir sur une nouvelle intégration. Toute autre
   exception (donnée non commitée) affiche une erreur simple
   (``st.error``) et arrête la page sans modifier ``integration_done``.

État de session (``st.session_state``)
----------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Constante
     - Clé ``session_state``
     - Description
   * - —
     - ``ms_level``, ``ion_mode``, ``integrator_name``, ``file_row_name``
     - Paramètres choisis à l'étape 1 (clés des widgets correspondants)
   * - ``MS1``
     - ``ms1``
     - DataFrame brut chargé à l'étape 2 (MS1 uniquement)
   * - ``MS2``
     - ``ms2``
     - Liste de scans parsés à l'étape 2 (MS2 uniquement)
   * - ``DF_ID``
     - ``df_file_id``
     - Identifiant du fichier chargé, utilisé pour détecter un nouvel upload
   * - ``DF_MS_LEVEL``
     - ``df_ms_level``
     - Niveau MS utilisé lors du dernier parsing, pour détecter un changement de niveau
   * - ``COLUMNS_VALID``
     - ``columns_valid``
     - Booléen indiquant que la vérification des colonnes obligatoires (étape 3) a réussi
   * - ``DF_COMPLETE``
     - ``df_complete``
     - DataFrame avec les colonnes dérivées calculées (étape 4)
   * - ``DF_VALID``
     - ``df_validated``
     - DataFrame validé par l'utilisateur, prêt pour l'intégration
   * - ``INTEGRATION_DONE``
     - ``integration_done``
     - Booléen indiquant que l'intégration en base a été effectuée
   * - ``EDITOR``
     - ``editor_integration``
     - Clé du widget ``st.data_editor`` utilisé à l'étape 4
   * - ``UPLOADER_VERSION``
     - ``uploader_version``
     - Compteur incrémenté par le bouton **Reset** pour recréer un ``st.file_uploader`` vide

``RESET_KEYS`` (utilisé par le bouton **Reset**) regroupe l'ensemble des clés
calculées (``MS1``, ``MS2``, ``DF_ID``, ``DF_MS_LEVEL``, ``DF_COMPLETE``,
``DF_VALID``, ``INTEGRATION_DONE``, ``COLUMNS_VALID``, ``EDITOR``) ;
``RELOAD_RESET_KEYS`` n'en contient qu'un sous-ensemble (``DF_COMPLETE``,
``DF_VALID``, ``INTEGRATION_DONE``, ``COLUMNS_VALID``, ``EDITOR``), utilisé
lors du chargement d'un nouveau fichier (ou d'un changement de niveau MS) pour
conserver les réglages de l'étape 1 et le fichier tout juste chargé.

Fonctions internes
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Fonction
     - Description
   * - ``_workflow(done: bool) -> str``
     - Retourne l'icône ``"✅"`` si ``done`` est vrai, sinon ``"⬜"``. Utilisée
       pour afficher l'état de chaque étape dans la barre latérale.

Ce module ne définit pas de fonction interne pour la résolution des adduits :
la page appelle directement, à l'étape 4, la fonction importée
:func:`utils.neutral_mass.resolve_adducts` (voir ci-dessous).

Résolution des adduits (étape 4)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:func:`utils.neutral_mass.resolve_adducts` résout l'adduit et la masse neutre
pour un lot d'enregistrements ``(label, lipid_name, precursor_mz,
raw_adduct)``. En interne, elle s'appuie sur une fonction privée du module
qui normalise/valide l'adduit, puis sur une autre qui calcule la masse
neutre à partir du ``Precursor_MZ`` et de l'adduit résolu.

Paramètres
   ``records``
      Itérable de tuples ``(label, lipid_name, precursor_mz, raw_adduct)`` :

      - ``label`` (*str*) : identifiant lisible de la ligne/du scan pour les
        messages d'erreur (ex. ``"Row 3"`` pour MS1, ``"Scan 12"`` pour MS2) ;
      - ``lipid_name`` (*str*) : nom du lipide, ré-inséré dans le message
        d'erreur pour faciliter la correction du fichier ;
      - ``precursor_mz`` (*float*) : m/z du précurseur ;
      - ``raw_adduct`` (*str* ou *None*) : valeur brute de l'adduit telle que
        lue dans le fichier, avant normalisation.

Retour
   Un triplet ``(adducts, masses, errors)`` de listes alignées sur
   ``records`` :

   - ``adducts`` : adduit normalisé (ex. ``"[M+H]+"``), ou ``None`` si la
     résolution a échoué pour cette entrée ;
   - ``masses`` : masse neutre en Daltons (6 décimales), ou ``None`` en cas
     d'échec ;
   - ``errors`` : liste des messages d'erreur (un par entrée en échec),
     préformatés en ``"{label} ({lipid_name}) : {message}"``, prête à être
     affichée telle quelle par la page (une entrée par ligne dans
     ``st.error``).

   Une entrée échoue (adduit/masse à ``None``, message ajouté à ``errors``) si
   l'adduit brut est manquant ou non reconnu. La liste des adduits acceptés
   n'est pas figée : elle comprend les deux adduits natifs ``"[M+H]+"`` et
   ``"[M-H]-"``, plus tout adduit personnalisé ajouté via la page
   **Resources** (:func:`utils.neutral_mass.add_adduct`/``remove_adduct``,
   persistés dans ``adducts.json``). Les autres entrées du lot
   continuent d'être traitées : un seul appel à ``resolve_adducts`` permet
   donc de collecter *toutes* les erreurs d'adduit du fichier en une fois,
   plutôt que de s'arrêter à la première.

Exemple
   .. code-block:: python

      >>> records = [
      ...     ("Row 0", "PE 34:1", 700.500000, "[M+H]+"),
      ...     ("Row 1", "PC 32:0", 750.500000, "XYZ"),   # adduit invalide
      ... ]
      >>> adducts, masses, errors = resolve_adducts(records)
      >>> adducts
      ['[M+H]+', None]
      >>> masses
      [699.492724, None]
      >>> errors
      ["Row 1 (PC 32:0) : Unsupported adduct 'XYZ'. Accepted values : [M+H]+, [M-H]-."]

   Dans l'étape 4 de la page, ``records`` est construit différemment selon le
   niveau MS :

   .. code-block:: python

      # MS1 : une ligne de DataFrame par enregistrement
      adducts, neutral_masses, e_adduct = resolve_adducts(
          (f"Row {idx}", row["Lipid_Name"], row["Precursor_MZ"], row.get("Adduct"))
          for idx, row in df.iterrows()
      )

      # MS2 : un scan par enregistrement
      adducts, n_mass, e_adduct = resolve_adducts(
          (f"Scan {data['scan_id']}", data["lipid_name"], data["precursor_mz"], data.get("adduct"))
          for data in ms2
      )

Dépendances internes
----------------------

- :mod:`utils.loading_MS1`
- :mod:`utils.loading_MS2`
- :mod:`utils.molecular_weight`
- :mod:`utils.monoisotopic`
- :mod:`utils.neutral_mass`