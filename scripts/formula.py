import pandas as pd
from molmass import Formula

INPUT_PATH = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto _Final.csv"
OUTPUT_PATH = "/home/liliacls/Documents/Stage/Data/Tableur_annotation/tableur_clean/LipidesAcineto _Final_Updated.csv"

df = pd.read_csv(INPUT_PATH)
original = df["Formula"].copy()
df["Formula"] = df["Formula"].apply(lambda f: Formula(str(f).strip()).formula)
modified = (df["Formula"] != original).sum()
df.to_csv(OUTPUT_PATH, index=False)
print(f"{modified}/{len(df)} formulas modified")
