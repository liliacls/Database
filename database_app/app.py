import streamlit as st
import pandas as pd
import sys
import sqlalchemy

"""
Detection :
- Precursor_MZ --> OBLIGATOIRE dans le fichier d'annotation
- Scan --> pas pris en compte pour l'instant
- MS_level --> à indiquer sur l'interface
- Num_peaks --> Si MS1 alors indiquer 0
- Energie_collision --> pas pris en compte pour l'instant
- Exact_mass --> La masse neutre n'est pas obligé d'être indiquée dans le fichier d'annotation, elle peut être calculée à partir du Precursor_MZ et du mode d'ionisation
- Molecular_weight --> calcul à partir de la formule
- RT --> à indiquer si connu
- CCS --> à indiquer si connu

Annotation :
- Confidence_level --> à voir

Lipid :
- Lipid_name --> OBLIGATOIRE dans le fichier d'annotation
- Lipid_class --> inféérement automatiquement à partir de la formule
- Lipid_categorie --> inféré automatiquement à partir de la formule
- Formula --> OBLIGATOIRE dans le fichier d'annotation

Bouton : 

- Choix du fichier d'annotation à intégrer
- Lancement de l'intégration --> visualiser les données intégrées dans la base de données
- Lancement de l'exportation --> visualiser les fichier avant de le télécharger
- Téléchargement du fichier

Système d'intégration de données issues du tableur d'annotation : 
- Paramètres globaux (Niveau d'annotation (MS_level), mode ionisation, niveau annotation)
- Chargement du fichier
- Prévisualisation + complétion automatique des champs manquants + possibilité de les modifier à la main)
- Validation / suppression de lignes
- Intégration finale dans la base de données
+ Gestion des erreurs de fichier

Système de génération du fichier pour l'annotation :
- Paramètres de tri des données par l'utilisateur
- Prévisalisation du fichier à exporter
- Téléchargement du fichier

Visualisation de la base de données quand l'utilisateur le souhaite. 

"""




