Modèle de données
===================

Fichier source : ``models/model.py``

.. note::
   Ce module définit les modèles SQLAlchemy (ORM) de **BacLipidDB**. Contrairement aux
   pages Streamlit, il est structuré en classes documentées : voir :class:`models.model.Detection`,
   :class:`models.model.Fragment`, :class:`models.model.Lipid` et :class:`models.model.Annotation`
   pour la référence générée automatiquement (``autoclass``). Cette page complète cette
   référence par une vue d'ensemble du schéma et des relations entre les tables.

Vue d'ensemble
--------------

Le module définit les 4 tables de la base de données via ``DeclarativeBase`` :

- ``Detection``  : signal détecté par le spectromètre de masse.
- ``Fragment``   : ions fragments associés à une détection (MS2 uniquement).
- ``Lipid``      : lipide de référence (nom, classe, catégorie, formule).
- ``Annotation`` : association entre une détection et un lipide candidat.

Relations
---------

.. list-table::
   :header-rows: 1
   :widths: 40 15 45

   * - Relation
     - Cardinalité
     - Description
   * - ``Detection`` → ``Fragment``
     - 1 → N
     - Un signal peut produire plusieurs fragments (MS2 uniquement).
   * - ``Detection`` → ``Annotation``
     - 1 → 1
     - Un signal correspond à une seule annotation.
   * - ``Lipid`` → ``Annotation``
     - 1 → 1
     - Un lipide est associé à une seule annotation.

Table ``Detection``
--------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Colonne
     - Type
     - Description
   * - ``Detection_ID``
     - ``int``
     - Clé primaire.
   * - ``Precursor_MZ``
     - ``float``
     - m/z de l'ion précurseur (Da).
   * - ``MS_level``
     - ``str``
     - ``"MS1"`` (précurseur seul) ou ``"MS2"`` (avec spectre de fragmentation).
   * - ``Ionisation_mode``
     - ``str``
     - ``"Positive"`` ou ``"Negative"``.
   * - ``Adduct``
     - ``str | None``
     - Adduit du précurseur.
   * - ``Num_Peaks``
     - ``int | None``
     - Nombre de pics de fragments (MS2 uniquement).
   * - ``Neutral_mass``
     - ``float``
     - Masse neutre dérivée de ``Precursor_MZ`` et du mode d'ionisation (Da).
   * - ``RT``
     - ``float | None``
     - Temps de rétention (minutes).
   * - ``CCS``
     - ``float | None``
     - Section efficace de collision (Ų).

Table ``Fragment``
--------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Colonne
     - Type
     - Description
   * - ``Fragment_ID``
     - ``int``
     - Clé primaire.
   * - ``Detection_id``
     - ``int``
     - Clé étrangère vers ``Detection.Detection_ID``.
   * - ``MZ``
     - ``float | None``
     - m/z de l'ion fragment (Da).
   * - ``Intensity``
     - ``float | None``
     - Intensité du pic de fragment.

Table ``Lipid``
------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Colonne
     - Type
     - Description
   * - ``Lipid_ID``
     - ``int``
     - Clé primaire.
   * - ``Lipid_name``
     - ``str``
     - Nom du lipide.
   * - ``Lipid_category``
     - ``str | None``
     - Catégorie LIPID MAPS.
   * - ``Lipid_class``
     - ``str | None``
     - Classe LIPID MAPS.
   * - ``Lipid_subclass``
     - ``str | None``
     - Sous-classe LIPID MAPS.
   * - ``Formula``
     - ``str``
     - Formule chimique.
   * - ``Molecular_weight``
     - ``float``
     - Masse moléculaire moyenne (Da).
   * - ``Monoisotopic_mass``
     - ``float``
     - Masse monoisotopique (Da).

Table ``Annotation``
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Colonne
     - Type
     - Description
   * - ``Annotation_ID``
     - ``int``
     - Clé primaire.
   * - ``Lipid_id``
     - ``int``
     - Clé étrangère (unique) vers ``Lipid.Lipid_ID``.
   * - ``Detection_id``
     - ``int``
     - Clé étrangère (unique) vers ``Detection.Detection_ID``.

Conventions
-----------

- Les clés primaires sont nommées avec le suffixe ``_ID``.
- Les clés étrangères sont nommées avec le suffixe ``_id``.
- Chaque classe définit un ``__repr__`` pour afficher un objet de façon lisible lors du débogage.

Voir aussi
----------

Documentation SQLAlchemy :

- `DeclarativeBase <https://docs.sqlalchemy.org/en/21/orm/declarative_styles.html>`_
- `Mapped <https://docs.sqlalchemy.org/en/21/orm/mapping_styles.html#orm-mapping-styles>`_
- `mapped_column <https://docs.sqlalchemy.org/en/21/orm/mapping_api.html#sqlalchemy.orm.Mapper.columns>`_
- `relationship, ForeignKey <https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html>`_
