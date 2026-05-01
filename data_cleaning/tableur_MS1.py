import pandas as pd
import re

# Chemins des fichiers 
PATH = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/LipidesAcineto.xlsx"
OUTPUT = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv"
OUTPUT_EXCLUS = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto_exclus.csv"

# Masse du proton (H⁻)
H_NEGATIF = 1.008489

# Liste des classes de lipides à conserver
LIPIDES = [
    'PE', 'PG', 'MLCL', 'CL', 'PA', 'LipA6P2', 'LipA7P2', 'NAPE', 'LipA6P2PE',
    'LipA7P2PE', 'PAGPE', 'LipA6P', 'PGox', 'aPG', 'cycPGP', 'LPA', 'DLCL', 'PPA',
    'MLCLox', 'LipIVA', 'LPG', 'LPE', 'LipA5P2', 'PGP', 'CPA', 'LipA6PPE', 'CLox',
    'LipA5P2PE', 'LipX3', 'LipX4', 'LipA7P', 'LipA7PPE', 'CPG', 'DaPG', 'LipA6P2PE-KDO',
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
        4.  Suppression du mot 'Precurser' dans la colonne Name.
        5.  Exclusion des lignes dont Formula ou Name contient '?'.
        6.  Exclusion des lignes dont Name contient ' ou ' (ambiguïté d'annotation).
        7.  Exclusion des fragments et adduits (mots-clés 'Fragment' ou '+').
        8.  Exclusion des lignes dont Name contient - H20,  -2H20
        9.  Exclusion des lignes dont le préfixe de Name ne correspond à aucune classe de lipides référencée dans LIPIDES.
        10.  La colonne 'Precursor_MZ' est calculée en soustrayant la masse du proton (H⁻) à la masse expérimentale, 
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
    exclus.append(df[NA].copy().assign(raison_exclusion='ligne vide:'))
    df = df[~NA]

    # Correction : Remplacement des valeurs 'w' par None
    df['Name'] = df['Name'].replace('w', None)

    # Correction : Nettoyage des tiret long (–) par des tiret ASCII (-) et des espaces en trop
    cols_obj = df.select_dtypes(include='object').columns
    df[cols_obj] = df[cols_obj].apply(lambda col: col.str.strip())

    # Suppression du mot "precurser" pour nettoyer la cellule
    df['Name'] = df['Name'].str.replace('Precurser', '', regex=False).str.strip()

    # Filtrage : Suppression des lignes avec '?'  annotation incertaine
    interrogation = (
        df['Formula'].str.contains(r'\?', na=False) |
        df['Name'].str.contains(r'\?', na=False)
    )
    exclus.append(df[interrogation].copy().assign(raison_exclusion='contient "?":'))
    df = df[~interrogation]

    # Filtrage : Suppression des lignes contenant " ou " : annotation ambiguë
    OU = df['Name'].str.contains(' ou ', regex=False, na=False)
    exclus.append(df[OU].copy().assign(raison_exclusion='contient "ou":'))
    df = df[~OU]

    # Filtrage : Suppression des fragments et adduits
    FRAG = df['Name'].str.contains(r'Fragment|\+', regex=True, na=False)
    exclus.append(df[FRAG].copy().assign(raison_exclusion='fragment ou adduit:'))
    df = df[~FRAG]
    
    # Filtrage : Suppression des lignes contenant - H20 ou - 2H20
    H2O = df['Name'].str.contains(r'–\s*\d*H2O', regex=True, na=False)
    exclus.append(df[H2O].copy().assign(raison_exclusion='contient "eau":'))
    df = df[~H2O]

    # Filtrage : Suppresion des lignes non lipidiques
    pattern = r'^(?:' + '|'.join(re.escape(l) for l in LIPIDES) + r')\b'
    lipides = df['Name'].str.contains(pattern, na=False, regex=True)
    exclus.append(df[~lipides].copy().assign(raison_exclusion='non lipide:'))
    df = df[lipides].copy()

    # Conversion de la colonne 'masse_experimentale' en numérique pour évitér les erreurs lors du calcul du rapport m/z
    df['masse_experimentale'] = pd.to_numeric(df['masse_experimentale'], errors='coerce')
    
    # Filtrage : Suppression des lignes avec une masse expérimentale invalide (NaN après conversion)
    mask_invalid = df['masse_experimentale'].isna()
    exclus.append(df[mask_invalid].copy().assign(raison_exclusion='masse invalide:'))
    df = df[~mask_invalid]

    # Calcul du rapport m/z précurseur (mode négatif)
    df['Precursor_MZ'] = df['masse_experimentale'] - H_NEGATIF

    # Consolidation de toutes les lignes exclues
    df_exclus = pd.concat(exclus, ignore_index=True)

    return df, df_exclus, exclus

# ─── Point d'entrée ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df, df_exclus, exclus = clean_MS1(PATH)

    df.to_csv(OUTPUT, index=False, encoding='utf-8')
    df_exclus.to_csv(OUTPUT_EXCLUS, index=False, encoding='utf-8')
    
    print("\nRésumé filtrage")
    print("---------------")
    print(f"Nombre de lipides gardés: {len(df)}")
    print(f"Lignes exclues : {len(df_exclus)}")
    for e in exclus:
        if not e.empty:
            print(e['raison_exclusion'].iloc[0], len(e))
    else:
        print("(filtre vide)", 0)