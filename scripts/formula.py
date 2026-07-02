"""
formula.py
-----------
Normalize chemical formulas in a CSV column to molmass's canonical notation

Usage :
    python scripts/formula.py <input.csv> [-o output.csv] [-c COLUMN]

Examples :
    python scripts/formula.py data.csv
    python scripts/formula.py data.csv -o data_normalized.csv -c Formula

Documentation :
    - molmass : python -m pydoc molmass
    - argparse : https://docs.python.org/3/library/argparse.html
"""

import argparse
import sys
import pandas as pd
from molmass import Formula, FormulaError

def normalize_formula(formula: str) -> str:
    """
    Return the canonical notation for a single chemical formula.

    :param formula: raw formula string.
    :type formula: str
    :return: canonical formula string, or the original value if it cannot be parsed.
    :rtype: str
    """
    try:
        return Formula(str(formula).strip()).formula
    except (FormulaError, ValueError):
        return formula


def normalize_csv(input_path: str, output_path: str, column: str) -> None:
    """
    Read a CSV, normalize the formulas in the given column, and write the result.

    :param input_path: path to the source CSV file.
    :type input_path: str
    :param output_path: path to write the updated CSV file.
    :type output_path: str
    :param column: name of the column containing the formulas.
    :type column: str
    :raises SystemExit: if the input file or the column cannot be read.
    """
    try:
        df = pd.read_csv(input_path)
    except (FileNotFoundError, pd.errors.ParserError) as ex:
        print(f"Error: could not read '{input_path}': {ex}")
        sys.exit(1)

    if column not in df.columns:
        print(f"Error: column '{column}' not found in '{input_path}'.")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    original = df[column].copy()
    df[column] = df[column].apply(normalize_formula)
    modified = (df[column] != original).sum()

    df.to_csv(output_path, index=False)
    print(f"{modified}/{len(df)} formulas modified")
    print(f"Saved to '{output_path}'")

def main():

    parser = argparse.ArgumentParser(description="Normalize chemical formulas in a CSV column.")
    parser.add_argument("input", help="path to the input CSV file")
    parser.add_argument("-o", "--output", help="path to the output CSV file (default: overwrite input)")
    parser.add_argument("-c", "--column", default="Formula", help="name of the formula column (default: Formula)")
    args = parser.parse_args()

    output_path = args.output if args.output else args.input
    normalize_csv(args.input, output_path, args.column)


if __name__ == "__main__":
    main()
