Resources
==========

Fichier source : ``app/pages/4_Resources.py``

.. note::
   Cette page contient la documentation du module Streamlit (``4_Resources.py``).
   La majorité du code n'est pas écrit sous forme de fonction, il n'est donc pas possible d'utiliser ``automodule``
   pour générer cette page automatiquement. La documentation ci-dessous est rédigée manuellement
   à partir du code source.

Vue d'ensemble
--------------

Ce module Streamlit (**MODULE 4**) sert de guide pour préparer les fichiers
d'intégration destinés au :doc:`1_Integration` (**MODULE 1**). Il présente,
pour les niveaux **MS1** et **MS2**, la liste des colonnes attendues avec
leur type et leur caractère obligatoire/optionnel, propose un fichier modèle
téléchargeable pour chaque niveau. Il liste également les adduits acceptés dans la
colonne ``Adduct`` et permet d'en ajouter ou d'en supprimer.

Guide des colonnes MS1
-------------------------

``st.dataframe`` affiche un tableau statique (``guide_ms1``) décrivant les
colonnes attendues dans un fichier d'intégration **MS1** : ``Precursor_MZ``,
``Adduct``, ``Formula``, ``FA_composition``, ``Lipid_Name``,
``Lipid_category``, ``Lipid_class``, ``Lipid_subclass``, ``RT`` et ``CCS``,
avec pour chacune son type et si elle est obligatoire (✅) ou optionnelle (❌).
Seules ``FA_composition``, ``RT`` et ``CCS`` sont optionnelles (à laisser
vides si non disponibles).

Modèle MS1
-----------

Un ``st.download_button`` génère et propose au téléchargement
``BacLipidDB_MS1_template.csv`` : un DataFrame d'une seule ligne (``template_ms1``)
illustrant les 7 colonnes obligatoires et les 2 colonnes optionnelles
(``RT``, ``CCS``) laissées vides, converti en CSV en mémoire via
``io.StringIO``.

Guide des colonnes MS2
-------------------------

Un fichier d'intégration **MS2** est organisé en blocs empilés verticalement,
un bloc par scan, séparés par une ligne vide. Chaque bloc commence par une
ligne ``Scan #<id>``, suivie d'une ligne ``Label,Value`` par champ (ordre
libre), puis de l'en-tête ``m/z,Intensity`` et des lignes de fragments
(``st.code`` affiche ce format en exemple).

``st.dataframe`` affiche ensuite un tableau statique (``guide_ms2``) décrivant
les colonnes/champs attendus : ``Scan #<id>``, ``Precursor_MZ``, ``Adduct``,
``Formula``, ``FA_composition``, ``Lipid_Name``, ``Lipid_category``,
``Lipid_class``, ``Lipid_subclass``, ``Num_peaks``, ``m/z``, ``Intensity``,
``RT`` et ``CCS``. Seules ``FA_composition``, ``RT`` et ``CCS`` sont
optionnelles (à supprimer entièrement du bloc si non disponibles, contrairement
au MS1 où elles sont laissées vides). ``Num_peaks`` doit correspondre au
nombre de lignes ``m/z``/``Intensity`` du bloc.

Modèle MS2
-----------

Un ``st.download_button`` génère et propose au téléchargement
``BacLipidDB_MS2_template.csv`` : deux scans d'exemple (``template_ms2``,
liste de lignes écrites via ``csv.writer`` dans un ``io.StringIO``) séparés
par une ligne vide. Le premier scan inclut les champs optionnels ``RT`` et
``CCS`` ; le second montre que ces lignes peuvent être omises entièrement
quand ces valeurs ne sont pas disponibles.

Adduits
--------

Table des adduits
~~~~~~~~~~~~~~~~~~~

``st.dataframe`` affiche la table des adduits acceptés dans la colonne
``Adduct`` (intégration MS1 et MS2), construite à partir de
:data:`utils.neutral_mass.ADDUCT_SHIFTS` et :data:`utils.neutral_mass.ADDUCT_SIGNS` :
nom de l'adduit, décalage de masse en Da (``Mass shift``), opération à
appliquer au m/z pour obtenir la masse neutre (``m/z - shift`` si
``ADDUCT_SIGNS[name] == -1``, ``m/z + shift`` sinon) et indicateur ``Custom``
(✅ si l'adduit provient de :func:`utils.neutral_mass.list_custom_adducts`,
❌ s'il s'agit d'un adduit natif).

Ajout d'un adduit personnalisé
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Un formulaire (``st.form``) permet de saisir un nom d'adduit
(``st.text_input``, ex. ``[M+Cl]-``), un décalage de masse en Da
(``st.number_input``) et le type de formation (``st.radio``) : « Addition »
(ex. ``[M+H]+``, ``[M+Na]+``) ou « Loss » (ex. ``[M-H]-``). Le signe transmis
à :func:`utils.neutral_mass.add_custom_adduct` vaut ``-1`` pour une addition
et ``1`` pour une perte, conformément à la convention de
:func:`utils.neutral_mass.neutral_mass` (``mz + sign * shift``). En cas de
succès, un message ``st.success`` est affiché et la page est rechargée
(``st.rerun()``) ; en cas d'erreur (nom vide/déjà utilisé, décalage non
strictement positif...), un message ``st.error`` affiche l'exception levée
par :func:`utils.neutral_mass.add_custom_adduct`.

Les adduits personnalisés sont persistés dans ``adducts.json`` (``config.ADDUCTS_PATH``)
et restent donc disponibles d'une session à l'autre.

Suppression d'un adduit personnalisé
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Si au moins un adduit personnalisé existe, un ``st.selectbox`` (liste des
adduits renvoyés par :func:`utils.neutral_mass.list_custom_adducts`) et un
bouton **Remove** permettent de le retirer via
:func:`utils.neutral_mass.remove_custom_adduct`, puis de recharger la page
(``st.rerun()``). Les adduits natifs (``BUILTIN_ADDUCT_SHIFTS``) ne peuvent
pas être supprimés.

Fonctions internes
-------------------

Ce module ne définit aucune fonction interne : l'ensemble du code s'exécute
au niveau du script (délégation directe aux fonctions de
:mod:`utils.neutral_mass`).

Dépendances internes
----------------------

- :mod:`utils.neutral_mass` (``ADDUCT_SHIFTS``, ``ADDUCT_SIGNS``,
  ``add_custom_adduct``, ``list_custom_adducts``, ``remove_custom_adduct``)
