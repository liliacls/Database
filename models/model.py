from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    """
    Classe de base déclarative pour tous les modèles ORM de BacLipidDB.

    Toutes les classes mappées (:class:`Detection`, :class:`Fragment`, :class:`Lipid`,
    :class:`Annotation`) héritent de cette classe afin que SQLAlchemy puisse collecter
    leurs métadonnées et générer les tables de la base de données correspondantes.
    """
    

class Detection(Base):
    """
    Une détection MS1 ou MS2 unique (ion observé lors d'une analyse).

    Stocke le m/z du précurseur, le mode d'ionisation, l'adduit, le temps de
    rétention et la CCS. Liée à zéro ou plusieurs lignes :class:`Fragment` quand
    ``MS_level`` vaut "MS2", et à une :class:`Annotation`.
    """

    __tablename__ = "Detection"
    Detection_ID: Mapped[int] = mapped_column(primary_key=True)

    Precursor_MZ: Mapped[float] = mapped_column()       # m/z de l'ion (Da), appelé "précurseur" par cohérence avec MS2, mais en MS1 ce n'est pas un véritable précurseur puisqu'il n'y a pas de fragmentation
    MS_level: Mapped[str] = mapped_column()           # "MS1" (précurseur seul) ou "MS2" (avec spectre de fragments)
    Ionisation_mode: Mapped[str] = mapped_column()      # "Positive" ou "Negative"
    Adduct: Mapped[str] = mapped_column()               # adduit du précurseur
    Num_Peaks: Mapped[int | None] = mapped_column()   # nombre de fragments (MS2 uniquement)
    Neutral_mass: Mapped[float] = mapped_column()     # masse neutre dérivée de Precursor_MZ et de l'adduit (Da)
    RT: Mapped[float | None] = mapped_column()          # temps de rétention (minutes)
    CCS: Mapped[float | None] = mapped_column()         # section efficace de collision (Å²)

    # Relation 1→N : une détection peut être associée à plusieurs fragments (MS2 uniquement)
    fragments: Mapped[list["Fragment"]] = relationship(back_populates="detection")

    # Relation 1→1 : une détection est associée à une seule annotation
    annotation: Mapped["Annotation"] = relationship(back_populates="detection")

    def __repr__(self):
        return f"Detection(Detection_ID={self.Detection_ID}, Precursor_MZ={self.Precursor_MZ}, MS_level={self.MS_level}, Ionisation_mode={self.Ionisation_mode}, Adduct={self.Adduct}, Num_Peaks={self.Num_Peaks}, Neutral_mass={self.Neutral_mass}, RT={self.RT}, CCS={self.CCS})"


class Fragment(Base):
    """
    Un pic d'ion fragment (m/z, intensité) appartenant à un spectre MS2.

    Chaque ligne est rattachée à la :class:`Detection` dans laquelle elle a été mesurée.
    """

    __tablename__ = "Fragment"
    Fragment_ID: Mapped[int] = mapped_column(primary_key=True)
    Detection_id: Mapped[int] = mapped_column(ForeignKey("Detection.Detection_ID"))

    MZ: Mapped[float | None] = mapped_column()          # m/z de l'ion fragment (Da)
    Intensity: Mapped[float | None] = mapped_column()   # intensité du pic de fragment

    # Relation N→1 : un fragment est rattaché à une seule détection
    detection: Mapped["Detection"] = relationship(back_populates="fragments")

    def __repr__(self):
        return f"Fragment(Fragment_ID={self.Fragment_ID}, Detection_id={self.Detection_id}, MZ={self.MZ}, Intensity={self.Intensity})"


class Lipid(Base):
    """
    Une entité lipidique identifiée par son nom, sa formule et sa classification LIPID MAPS.

    Indépendante de toute détection donnée ; liée à la :class:`Detection` dans
    laquelle elle a été identifiée via une seule :class:`Annotation`.
    """

    __tablename__ = "Lipid"
    Lipid_ID: Mapped[int] = mapped_column(primary_key=True)

    Lipid_name: Mapped[str] = mapped_column()
    Lipid_category: Mapped[str | None] = mapped_column()  # catégorie LIPID MAPS
    Lipid_class: Mapped[str | None] = mapped_column()     # classe LIPID MAPS
    Lipid_subclass: Mapped[str | None] = mapped_column()  # sous-classe LIPID MAPS
    Formula: Mapped[str] = mapped_column()
    FA_composition: Mapped[str | None] = mapped_column()  # composition en acides gras
    Molecular_weight: Mapped[float] = mapped_column()     # masse moléculaire moyenne (Da)
    Monoisotopic_mass: Mapped[float] = mapped_column()    # masse monoisotopique exacte (Da)

    # Relation 1→1 : un lipide est associé à une seule annotation
    annotation: Mapped["Annotation"] = relationship(back_populates="lipid")

    def __repr__(self):
        return f"Lipid(Lipid_ID={self.Lipid_ID}, Lipid_name='{self.Lipid_name}', Lipid_category='{self.Lipid_category}', Lipid_class='{self.Lipid_class}', Lipid_subclass='{self.Lipid_subclass}', Formula='{self.Formula}', FA_composition='{self.FA_composition}', Molecular_weight={self.Molecular_weight}, Monoisotopic_mass={self.Monoisotopic_mass})"


class Annotation(Base):
    """
    Table de jointure liant un :class:`Lipid` à une :class:`Detection`.

    Représente l'identification d'un ion détecté comme un lipide donné.
    """

    __tablename__ = "Annotation"
    Annotation_ID: Mapped[int] = mapped_column(primary_key=True)
    Lipid_id: Mapped[int] = mapped_column(ForeignKey("Lipid.Lipid_ID"), unique=True)
    Detection_id: Mapped[int] = mapped_column(
        ForeignKey("Detection.Detection_ID"), unique=True
    )

    # Relation N→1 : une annotation est rattachée à un seul lipide
    lipid: Mapped["Lipid"] = relationship(back_populates="annotation")

    # Relation N→1 : une annotation est rattachée à une seule détection
    detection: Mapped["Detection"] = relationship(back_populates="annotation")

    def __repr__(self):
        return f"Annotation(Annotation_ID={self.Annotation_ID}, Lipid_id={self.Lipid_id}, Detection_id={self.Detection_id})"