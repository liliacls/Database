Management
===========

Fichier source : ``app/pages/5_Management.py``

.. note::
   Cette page contient la documentation du module Streamlit (``5_Management.py``).
   Le code c'est pas écrit sous forme de fonction, il n'est donc pas possible d'utiliser ``automodule``
   pour générer cette page automatiquement. La documentation ci-dessous est rédigée manuellement
   à partir du code source.

Vue d'ensemble
--------------

Ce module Streamlit (**MODULE 5**) permet de corriger ou de supprimer des données déjà
intégrées dans **BacLipidDB**, via deux sections indépendantes :

- **Edit & delete records** : édition cellule par cellule des annotations existantes, ou
  suppression de lignes individuelles.
- **Delete an entire import** : suppression en une fois de tout ce qu'un import donné a inséré
  en base, à partir de l'historique.

Une sauvegarde de la base (:func:`utils.db_backup.backup_database`) est systématiquement prise
avant toute modification, et chaque action destructrice ou modificatrice passe par une boîte de
dialogue de confirmation (``@st.dialog``).

Edit & delete records
----------------------

Chargement des données
~~~~~~~~~~~~~~~~~~~~~~~

``_load_database()`` s'appuie sur :func:`utils.data_access.load_database` (la même
requête jointe ``Annotation`` + ``Lipid`` + ``Detection`` que les pages **2_BacLipidDB** et
**3_Export**), dont elle ne conserve que les colonnes nécessaires à l'affichage et au report des
modifications en base : ``Annotation_ID``, ``Detection_ID``, ``Lipid_ID``, ``Lipid_name``,
``Formula``, ``Lipid_category``, ``Lipid_class``, ``Lipid_subclass``, ``Precursor_MZ``,
``Ionisation_mode``, ``Adduct``, ``Neutral_mass``, ``Molecular_weight``, ``Monoisotopic_mass``,
``MS_level``, ``Num_Peaks``, ``RT``, ``CCS``. Si le chargement échoue, un message ``st.error``
est affiché et la page s'arrête (``st.stop()``) ; si la base est vide, un message ``st.info`` est
affiché à la place.

Édition du tableau
~~~~~~~~~~~~~~~~~~~

Une colonne ``Delete`` (case à cocher) est ajoutée en tête du tableau affiché via
``st.data_editor``. Les colonnes ``Annotation_ID``, ``Detection_ID``, ``Lipid_ID``,
``Precursor_MZ``, ``Ionisation_mode``, ``Adduct``, ``Neutral_mass``, ``Molecular_weight``,
``Monoisotopic_mass`` et ``MS_level`` sont verrouillées (``disabled``). Restent donc modifiables :

- ``Lipid_name``, ``Lipid_category``, ``Lipid_class``, ``Lipid_subclass`` (``EDITABLE_LIPID_FIELDS``) ;
- ``Formula`` ;
- ``Num_Peaks``, ``RT``, ``CCS`` (``EDITABLE_DETECTION_FIELDS``).

``Precursor_MZ``, ``Ionisation_mode`` et ``Adduct`` ne sont pas éditables ici car les modifier
nécessiterait de recalculer ``Neutral_mass`` (dérivée uniquement de ces deux dernières colonnes),
recalcul qui n'est pas implémenté sur cette page.

Calcul du plan de modification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``_database_modif(original, edited)`` compare le tableau édité à l'original ligne par ligne et
construit un plan ``{updates, deletes, errors}`` :

- si la case ``Delete`` est cochée, la ligne (avec ses ``Annotation_ID``, ``Detection_ID``,
  ``Lipid_ID`` et son nom) part directement dans ``deletes``, sans autre vérification ;
- sinon, les colonnes de ``NON_EMPTY_COLUMNS`` (``Lipid_name``, ``Formula``, ``Precursor_MZ``)
  sont contrôlées : toute cellule vide ajoute un message dans ``errors`` ;
- les champs modifiés parmi ``EDITABLE_LIPID_FIELDS`` et ``EDITABLE_DETECTION_FIELDS`` sont
  collectés séparément (``lipid_fields`` / ``detection_fields``), car ils seront reportés sur
  deux tables différentes (``Lipid`` / ``Detection``) ;
- si ``Formula`` a changé, ``Molecular_weight`` et ``Monoisotopic_mass`` sont recalculées
  (:func:`utils.molecular_weight.molecular_weight`, :func:`utils.monoisotopic.monoisotopic_mass`),
  exactement comme lors de la complétion automatique du module d'intégration (**1_Integration**).
  Si le calcul échoue, un message est ajouté à ``errors`` et les masses ne sont pas mises à jour ;
- une ligne sans aucun champ modifié n'est ajoutée ni à ``updates`` ni à ``deletes``.

Le bouton **Apply changes** affiche les erreurs s'il y en a, un message ``st.info`` si le plan est
vide, ou stocke le plan dans ``st.session_state["pending_plan"]`` et déclenche un ``st.rerun()``
pour ouvrir la confirmation.

Confirmation et application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``_confirm_apply(plan)`` (``@st.dialog``) résume le nombre de lignes à mettre à jour et à
supprimer, avertit que les suppressions sont irréversibles depuis l'application (``Fragment``,
``Annotation``, ``Detection`` et ``Lipid`` liés) et liste les lignes concernées. Les boutons
**Confirm** / **Cancel** appellent respectivement ``_apply(plan)`` ou annulent, dans les deux
cas suivis d'un ``st.rerun()``.

``_apply(plan)`` prend d'abord une sauvegarde (``backup_database(label="manual_edit")``),
puis dans une session SQLAlchemy :

- pour chaque suppression, retire dans l'ordre les lignes liées de ``Fragment``, ``Annotation``,
  ``Detection`` puis ``Lipid`` (la base ne propageant pas ces suppressions automatiquement, elles
  sont faites manuellement, dans cet ordre pour respecter les dépendances de clés étrangères) ;
- pour chaque mise à jour, applique ``lipid_fields`` sur ``Lipid`` et ``detection_fields`` sur
  ``Detection`` (une requête ``update`` par table concernée, uniquement si le dictionnaire n'est
  pas vide) ;
- commit puis invalidation du cache (``load_database.clear()``), pour que les pages
  utilisant cette vue reflètent l'état à jour de la base.

Delete an entire import
-------------------------

L'historique des imports (:func:`utils.history.load_history`) est présenté dans un
``st.selectbox`` (``_label(i)`` formate chaque entrée : nom de fichier, date d'insertion, nombre
de lignes et intégrateur). Une fois un import sélectionné, le nombre d'enregistrements de ce lot
encore présents en base est recalculé (``session.query(Detection)...count()``) et affiché à côté
du nombre de lignes recensé au moment de l'import : les deux peuvent différer si des lignes de ce
lot ont déjà été supprimées individuellement via **Edit & delete records**.

Le bouton **Delete this import** stocke l'index sélectionné dans
``st.session_state["pending_history_delete"]`` et déclenche un ``st.rerun()`` pour ouvrir la
confirmation.

``_history_del(entry, index)`` (``@st.dialog``) avertit du nombre d'enregistrements qui
seront supprimés et rappelle qu'une sauvegarde est prise automatiquement. Les boutons
**Confirm deletion** / **Cancel** appellent respectivement ``_delete_import(entry, index)`` ou
annulent.

``_delete_import(entry, index)`` prend une sauvegarde
(``backup_database(label=f"delete_{entry.get('filename', 'import')}")``), puis dans une session
SQLAlchemy : récupère les ``Lipid_ID`` liés aux ``detection_ids`` de l'entrée (via ``Annotation``),
supprime les lignes de ``Fragment``, ``Annotation`` et ``Detection`` correspondant à ces
``detection_ids``, puis celles de ``Lipid`` correspondant aux ``Lipid_ID`` récupérés, commit,
invalide le cache (``load_database.clear()``), puis retire l'entrée de l'historique
(:func:`utils.history.remove_history`).

Fonctions internes
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Fonction
     - Description
   * - ``_load_database() -> pandas.DataFrame``
     - Charge la vue jointe Detection/Lipid/Annotation utilisée pour l'édition, restreinte aux
       colonnes nécessaires à l'affichage et au report des modifications.
   * - ``_database_modif(original, edited) -> dict``
     - Compare le tableau édité à l'original et construit le plan de modification
       ``{updates, deletes, errors}``.
   * - ``_apply(plan: dict) -> None``
     - Sauvegarde la base puis applique le plan (suppressions en cascade et mises à jour
       ciblées) dans une session SQLAlchemy.
   * - ``_confirm_apply(plan: dict) -> None``
     - Boîte de dialogue de confirmation pour le plan d'édition/suppression de lignes.
   * - ``_delete_import(entry: dict, index: int) -> None``
     - Supprime tous les enregistrements d'un lot d'import (Fragment/Annotation/Detection/Lipid)
       puis retire l'entrée de l'historique.
   * - ``_history_del(entry: dict, index: int) -> None``
     - Boîte de dialogue de confirmation pour la suppression d'un import entier.

Dépendances internes
----------------------

- :func:`utils.data_access.load_database`
- :func:`utils.db_backup.backup_database`
- :func:`utils.history.load_history`
- :func:`utils.history.remove_history`
- :func:`utils.molecular_weight.molecular_weight`
- :func:`utils.monoisotopic.monoisotopic_mass`
- :mod:`config` (``get_engine``)
