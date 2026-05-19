"""
clean_MS1.py
------------
Nettoyage et filtrage du tableur d'annotation MS1 brut (LipidesAcineto.xlsx).

Transformations appliquées (du plus au moins discriminant) :
    1.  Suppression des colonnes non pertinentes : m/z, intensity, diff, %intensity, col J.
    2.  Renommage : Formula → Lipid_Name | col E → Formula | m exp → Precursor_MZ.
    3.  Suppression des lignes où Lipid_Name, Formula ou Precursor_MZ est absent.
    4.  Conservation uniquement des lipides dont le préfixe est dans LIPIDES.
    5.  Suppression des adduits (+).
    6.  Suppression des lipides + (O)
    7.  Suppression des lipides + ;O
    8.  Suppression des lignes contenant " ou "
    9.  Suppression des tirets longs
    10. Suppression des variantes -O
    11. Suppression des lignes dont Lipid_Name commence par "C13".
    12. Suppression des lignes dont Lipid_Name contient "Fragment".
    13. Suppression des lignes dont Lipid_Name se termine par "Précurseur" ou "Precurser".
    14. Suppression des lignes dont Lipid_Name contient des parenthèses.

Usage :
    python scripts/clean_MS1.py
"""

import re
import pandas as pd
from pathlib import Path

PATH          = Path('/home/liliacls/Documents/Stage/Data/Tableur_annotation/LipidesAcineto.xlsx')
OUTPUT        = Path('/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto.csv')
OUTPUT_EXCLUS = Path('/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto_exclus.csv')

LIPIDES = [
    'PE', 'PG', 'MLCL', 'CL', 'PA', 'LipA6P2', 'LipA7P2', 'NAPE', 'LipA6P2PE',
    'LipA7P2PE', 'PAGPE', 'LipA6P', 'PGox', 'aPG', 'cycPGP', 'LPA', 'DLCL', 'PPA',
    'MLCLox', 'LipIVA', 'LPG', 'LPE', 'LipA5P2', 'PGP', 'CPA', 'LipA6PPE', 'CLox',
    'LipA5P2PE', 'LipX3', 'LipX4', 'LipX', 'LipA7P', 'LipA7PPE', 'CPG', 'DaPG',
    'LipA6P2PE-KDO', 'LipA6P2-KDO', 'CDP-PA34:1', 'CDP-PA32:1', 'LcycPGP', 'UDP',
]

REQUIRED_COLUMNS = ['Lipid_Name', 'Formula', 'Precursor_MZ']


def clean_MS1(path: Path):
    """Lit le fichier Excel brut et applique les filtres de nettoyage MS1.

    :param path: Chemin vers le fichier Excel brut (.xlsx)
    :type path: Path
    :return: Tuple (df_clean, df_exclus, exclus) — données valides, exclues et détail des filtres
    :rtype: tuple[pd.DataFrame, pd.DataFrame, list]
    """
    df = pd.read_excel(path)

    # ── Mise en forme ─────────────────────────────────────────────────────────

    df = df.drop(columns=['m/z', 'intensity', 'm theor', 'diff', '%intensity', 'code', 'Unnamed: 9'])

    df = df.rename(columns={
        'Formula'    : 'Lipid_Name',
        'Unnamed: 4' : 'Formula',
        'm exp'      : 'Precursor_MZ',
    })

    # ── Filtrage (du plus au moins discriminant) ───────────────────────────────

    exclus = []

    def exclure(mask, raison):
        exclus.append(df[mask].copy().assign(raison_exclusion=raison))
        return df[~mask]

    # 1. Colonnes obligatoires manquantes
    df = exclure(df[REQUIRED_COLUMNS].isnull().any(axis=1), 'colonne obligatoire manquante')

    # 2. Conservation des lipides connus uniquement
    pattern = r'^(?:' + '|'.join(re.escape(l) for l in sorted(LIPIDES, key=len, reverse=True)) + r')\b'
    lipides_connus = df['Lipid_Name'].str.contains(pattern, na=False, regex=True)
    fragment_valide = df['Lipid_Name'].str.match(r'^Fragment\s+\S', na=False)
    df = exclure(~(lipides_connus | fragment_valide), 'classe lipidique inconnue')

    # 3. Adduits (contient "+")
    df = exclure(df['Lipid_Name'].str.contains(r'\+', regex=True, na=False), 'adduit (+)')

    # 4. Variants (O) — plasmalogènes / éthers
    df = exclure(df['Lipid_Name'].str.contains(r'\(O\)', regex=True, na=False), 'contient (O)')

    # 5. Variants ;O — lipides oxydés
    df = exclure(df['Lipid_Name'].str.contains(r';O', regex=False, na=False), 'contient ;O')

    # 7. Tirets longs (–, —)
    df = exclure(df['Lipid_Name'].str.contains(r'–|—', regex=True, na=False), 'tiret long')

    # 8. Variante -O isolée (hors notation éther e\dO)
    df = exclure(df['Lipid_Name'].str.contains(r'\d-O\d*(?=[\s\-]|$)', regex=True, na=False), 'contient -O')

    # 9. Noms commençant par "C13"
    df = exclure(df['Lipid_Name'].str.startswith('C13', na=False), 'C13')

    # 10. Noms contenant "Fragment"
    df = exclure(df['Lipid_Name'].str.contains('Fragment', regex=False, na=False), 'Fragment')

    # 11. Noms se terminant par "Précurseur" ou "Precurser"
    df = exclure(df['Lipid_Name'].str.endswith(('Précurseur', 'Precurser'), na=False), 'Précurseur')

    # 12. Noms contenant des parenthèses
    df = exclure(df['Lipid_Name'].str.contains(r'\(', regex=True, na=False), 'contient des parenthèses')

    df_exclus = pd.concat(exclus, ignore_index=True)

    return df, df_exclus, exclus


if __name__ == "__main__":
    df, df_exclus, exclus = clean_MS1(PATH)

    df.to_csv(OUTPUT, index=False, encoding='utf-8')
    df_exclus.to_csv(OUTPUT_EXCLUS, index=False, encoding='utf-8')

    print("\nRésumé filtrage")
    print("---------------")
    print(f"Lignes conservées : {len(df)}")
    print(f"Lignes exclues    : {len(df_exclus)}")
    for e in exclus:
        if not e.empty:
            print(f"  {e['raison_exclusion'].iloc[0]:<40} {len(e)}")