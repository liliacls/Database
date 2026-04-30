import pandas as pd

# Chemins des fichiers 
PATH = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/LipidesAcineto.xlsx"
OUTPUT = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto2.csv"
OUTPUT_EXCLUS = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto_exclus.csv"

# Masse du proton (H⁻)
H_NEGATIF = 1.008489

# Liste des classes de lipides à conserver
LIPIDES = [
    'PE', 'PG', 'MLCL', 'CL', 'PA', 'LipA6P2', 'LipA7P2', 'NAPE', 'LipA6P2PE',
    'LipA7P2PE', 'PAGPE', 'LipA6P', 'PGox', 'aPG', 'cycPGP', 'LPA', 'DLCL', 'PPA',
    'MLCLox', 'LipIVA', 'LPG', 'LPE', 'LipA5P2', 'PGP', 'CPA', 'LipA6PPE', 'CLox',
    'LipA5P2PE', 'LipX3', 'LipA7P', 'LipA7PPE', 'CPG', 'DaPG', 'LipA6P2PE-KDO',
    'LipA6P2-KDO', 'CDP-PA34:1', 'CDP-PA32:1', 'LcycPGP', 'UDP'
]

def clean_MS1(PATH):
    """
    Lit le fichier Excel brut, supprime les colonnes non pertinentes, renomme les colonnes restantes, 
    puis applique une série de filtres pour ne conserver que les lignes pertinentes. 
    Les lignes rejetées sont rassemblées dans un DataFrame séparé avec la raison de leur exclusion.

    Les étapes de filtrage, dans l'ordre, sont :
        1.  Suppression des lignes contenant au moins une valeur manquante.
        2.  Remplacement de 'w' par None dans la colonne Name.
        3.  Nettoyage des tirets spéciaux et des espaces superflus.
        4.  Exclusion des lignes dont Name contient 'Precurser' (ion précurseur).
        5.  Exclusion des lignes dont Formula ou Name contient '?'.
        6.  Exclusion des lignes dont Name contient ' ou ' (ambiguïté d'annotation).
        7.  Exclusion des fragments et adduits (mots-clés 'Fragment' ou '+').
        8.  Exclusion des lignes dont le préfixe de Name ne correspond à aucune classe de lipides référencée dans LIPIDES.
        9.  La colonne 'Precursor_MZ' est calculée en soustrayant la masse du proton (H⁻) à la masse expérimentale, 
            pour obtenir le rapport m/z en mode d'ionisation négatif.

    :param PATH: Chemin vers le fichier Excel d'annotation à nettoyer (.xlsx).
    :type PATH: str
    :return: Un tuple "(df, df_exclus)' où 'df' contient les lignes validées avec la colonne 'Precursor_MZ' calculée, 
            et 'df_exclus' contient toutes les lignes rejetées avec une colonne 'raison_exclusion'.
    :rtype: tuple[pd.DataFrame, pd.DataFrame]
    """

    # Chargement du fichier
    df = pd.read_excel(PATH)

    # Mise en forme des colonnes : suppression des colonnes non pertinentes
    df = df.drop(columns=['m/z', 'intensity', 'Unnamed: 9', 'diff', 'code', '%intensity'])

    # Mise en forme des colonnes : renommage des colonnes
    df = df.rename(columns={
        'Formula'    : 'Name',
        'Unnamed: 4' : 'Formula',
        'm exp'      : 'masse_experimentale',
        'm theor'    : 'masse_theorique'
    })

    # Filtrage : accumulateur des lignes rejetées 
    exclus = []

    # Filtrage : Suppression des lignes vides
    NA = df.isnull().any(axis=1)
    exclus.append(df[NA].copy().assign(raison_exclusion='ligne vide'))
    df = df[~NA]

    # Correction : Remplacement des valeurs 'w' par None
    df['Name'] = df['Name'].replace('w', 'None')

    # Correction : Nettoyage des tiret long (–) par des tiret ASCII (-) et des espaces en trop
    df['Name'] = df['Name'].str.replace('–', '-', regex=False).str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

    # Suppression du mot precurseur pour nettoyer la cellule
    df['Name'] = df['Name'].str.replace('Precurser', '', regex=False).str.strip()

    # Filtrage : Suppression des lignes avec '?'  annotation incertaine
    interrogation = (
        df['Formula'].str.contains(r'\?', na=False) |
        df['Name'].str.contains(r'\?', na=False)
    )
    exclus.append(df[interrogation].copy().assign(raison_exclusion='contient ?'))
    df = df[~interrogation]

    # Filtrage : Suppression des lignes contenant " ou " : annotation ambiguë
    OU = df['Name'].str.contains(' ou ', regex=False, na=False)
    exclus.append(df[OU].copy().assign(raison_exclusion='contient ou'))
    df = df[~OU]

    # Filtrage : Suppression des fragments et adduits
    FRAG = df['Name'].str.contains(r'Fragment|\+', regex=True, na=False)
    exclus.append(df[FRAG].copy().assign(raison_exclusion='fragment ou adduit'))
    df = df[~FRAG]

    # Filtrage : Suppresion des lignes non lipidiques
    pattern = '|'.join([f'^{l}' for l in LIPIDES])
    lipides = df['Name'].str.contains(pattern, na=False)
    exclus.append(df[~lipides].copy().assign(raison_exclusion='non lipide'))
    df = df[lipides].copy()

    # Calcul du rapport m/z précurseur (mode négatif)
    df['Precursor_MZ'] = df['masse_experimentale'] - H_NEGATIF

    # Consolidation de toutes les lignes exclues
    df_exclus = pd.concat(exclus, ignore_index=True)

    return df, df_exclus

# ─── Point d'entrée ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df, df_exclus = clean_MS1(PATH)

    df.to_csv(OUTPUT, index=False)
    print(f"Fichier nettoyé enregistré sous : {OUTPUT}")
    print(f"Nombre de lipides gardés        : {len(df)}")

    df_exclus.to_csv(OUTPUT_EXCLUS, index=False)
    print(f"\nLignes exclues ({len(df_exclus)}) enregistrées sous : {OUTPUT_EXCLUS}")