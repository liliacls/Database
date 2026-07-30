Home
=====

Fichier source : ``app/Home.py``

.. note::
   Cette page contient la documentation du module Streamlit (``Home.py``).
   La majorité du code n'est pas écrit sous forme de fonction, il n'est donc pas possible d'utiliser ``automodule``
   pour générer cette page automatiquement. La documentation ci-dessous est rédigée manuellement
   à partir du code source.

Vue d'ensemble
--------------

Cette page est la page d'accueil de **BacLipidAPP**. Elle affiche le logo de
l'application, une description générale, des liens vers les cinq modules
disponibles (:doc:`1_Integration`, :doc:`2_BacLipidDB`, :doc:`3_Export`,
:doc:`4_Resources`, :doc:`5_Management`) ainsi qu'un aperçu synthétique du
contenu de **BacLipidDB**.

Logo et description
--------------------

Le logo (``assets/APP.svg``) est affiché centré (``st.columns``).
Une description de l'application est ensuite affichée via ``st.markdown``
(HTML autorisé via ``unsafe_allow_html=True``).

Modules disponibles
--------------------

Cinq encadrés (``st.container(border=True)``), répartis sur ``st.columns(5)``,
présentent chacun un module et pointent vers sa page (``st.page_link``) :

- **MODULE 1** : lien vers ``pages/1_Integration.py``, intégration des données.
- **MODULE 2** : lien vers ``pages/2_BacLipidDB.py``, exploration de la base de données **BacLipidDB**
- **MODULE 3** : lien vers ``pages/3_Export.py``, export des données dans des formats compatibles avec MZmine.
- **MODULE 4** : lien vers ``pages/4_Resources.py``, guide des colonnes pour les fichiers d'intégration.
- **MODULE 5** : lien vers ``pages/5_Management.py``, correction/suppression des enregistrements déjà intégrés.

Aperçu de la base de données
------------------------------

La fonction ``_statistics()`` (mise en cache via ``st.cache_data(ttl=60)``)
interroge la base de données via une session SQLAlchemy et retourne :

- le nombre de détections ``MS1`` (``Detection.MS_level == "MS1"``) ;
- le nombre de détections ``MS2`` (``Detection.MS_level == "MS2"``) ;
- la taille du fichier ``BacLipidDB.db`` (formatée en Ko ou Mo selon sa taille).

En cas d'erreur de connexion, la fonction retourne ``None`` et le message
``st.warning("Unable to connect to the database.")`` est affiché à la place
des métriques. Sinon, les trois valeurs sont affichées via ``st.metric`` dans
des encadrés (``st.container(border=True)``), avec pour libellés respectifs
``"MS1 detections"``, ``"MS2 detections"`` et ``"Database size"``.

Fonctions internes
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Fonction
     - Description
   * - ``_statistics() -> dict | None``
     - Calcule et met en cache le nombre de détections ``MS1``/``MS2`` et la
       taille du fichier de base de données. Retourne ``None`` en cas d'erreur.

Dépendances internes
----------------------

- :mod:`models.model` (``Detection``)
- :mod:`config` (``get_engine``)

Fonctionnement général de Streamlit
--------------------------------------

Cette section décrit deux mécanismes de Streamlit qui reviennent dans
plusieurs modules de l'application.

**Le rerun**

À chaque interaction de l'utilisateur (clic sur un bouton, changement de
valeur d'un widget, etc.), Streamlit **réexécute l'intégralité du script
Python de haut en bas**. Il n'y a pas de gestion d'événements comme dans une
application web classique, ce qui signifie que le code d'une page est rejoué à chaque
interaction, y compris les widgets déjà affichés.

**``st.session_state`` et la ``key`` des widgets**

Puisque le script est rejoué en entier à chaque interaction, Streamlit a
besoin d'un moyen d'associer un widget (ex. ``st.file_uploader(...)``)
rappelé lors d'un rerun à la valeur qu'il avait lors du rerun précédent.
Cette association se fait via la ``key`` du widget : c'est elle qui permet
de retrouver la valeur précédente (fichier déposé, texte saisi, tableur...) et de la
lui réattribuer, plutôt que de le réinitialiser à chaque fois.

C'est ce que permet ``st.session_state`` : c'est un dictionnaire persistant,
propre à chaque session utilisateur qui survit aux reruns (contrairement
aux variables Python classiques). On peut se le représenter comme une armoire à casiers, où
chaque ``key`` de widget désigne un casier précis. Par exemple, quand le script appelle
``st.file_uploader(key="mon_widget")`` Streamlit vérifie si le casier
``"mon_widget"`` contient déjà une valeur (issue d'un rerun précédent) :
si oui, il l'utilise pour réafficher le widget dans son état existant
sinon, il crée le casier et l'initialise.

Pour la plupart des widgets (``st.selectbox``, ``st.text_input``...), on
peut aussi écrire directement dans ``st.session_state`` pour changer leur
valeur par programmation (ex. les remettre à ``None``/``""`` depuis un
bouton Reset). Mais certains widgets (``st.file_uploader``, ``st.button``) **interdisent** cette écriture directe (Streamlit
lève une exception). Pour les vider malgré tout depuis le code, la seule
solution est de changer leur ``key`` : Streamlit regarde alors dans un
casier différent vide. Par exemple l'usage d'un compteur
de version (ex. ``UPLOADER_VERSION``) inclus dans la ``key`` pour forcer la
recréation d'un widget vide.

Exemple concret tiré de la page **Integration** (``pages/1_Integration.py``) :

- Au premier passage, ``st.session_state`` ne contient pas encore la clé
  ``"uploader_version"``, donc ``st.session_state.get(UPLOADER_VERSION, 0)``
  vaut ``0``. Le widget est créé avec ``key="file_uploader_0"``. Si
  l'utilisateur dépose un fichier, celui-ci est rangé dans le casier
  ``"file_uploader_0"``.
- Quand l'utilisateur clique sur **Reset 🔄**, le code exécute
  ``st.session_state[UPLOADER_VERSION] = st.session_state.get(UPLOADER_VERSION, 0) + 1``,
  ce qui fait passer le compteur de ``0`` à ``1``, puis appelle ``st.rerun()``.
- Au rerun suivant, la ``key`` est réévaluée et vaut désormais
  ``"file_uploader_1"``. Ce casier n'a jamais été utilisé : il est vide, et le
  widget s'affiche donc vide. Le casier ``"file_uploader_0"`` existe toujours
  quelque part (avec l'ancien fichier dedans), mais n'est plus consulté
  puisque la clé du widget a changé.