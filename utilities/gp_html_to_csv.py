
import os
from io import StringIO
import re
import pandas as pd
import bs4
from bs4 import BeautifulSoup

def parse_year(filename, gp_input_directory, gp_output_directory):
    year = filename[-9:-5]
    if not year.isnumeric():
        raise ValueError(f"Relying on filenames for years, but found {year} in the year space in filename {filename}")

    file_path = os.path.join(gp_input_directory, filename)
    
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    tables = pd.read_html(StringIO(str(soup)))

    if len(tables) != 1:
        raise ValueError(f"Expected table count 1, found {len(tables)}")
    
    table = tables[0]

    rename = {}
    for round in range(1, 9):
        for label in ("position", "points", "rank. points"):
            rename[f'GP{round} {label}'] = f"GP_t{round} {label}"

    table.rename(columns=rename, inplace=True)
    table["year"] = year

    csv_filename = f"gp_{filename[:-5]}.csv"
    output_path = os.path.join(gp_output_directory, csv_filename)
    table.to_csv(output_path, index=False)
    print(f"Saved table from {filename} to {output_path}")

def parse_round(filename, gp_input_directory, gp_output_directory):
    file_path = os.path.join(gp_input_directory, filename)

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    year = filename[7:11]
    round_pattern = r"results\d{4}_r(\d+)\.html"
    match = re.search(round_pattern, filename)
    if not match:
        raise ValueError(f"Round number not found in filename \"{filename}\"")

    round_number = match.group(1)

    soup = BeautifulSoup(html_content, "html.parser")

    tables = pd.read_html(StringIO(str(soup)))

    if len(tables) != 1:
        raise ValueError(f"Expected table count 1, found {len(tables)}")

    table = tables[0]

    table = table[["#", "Name", "Country", "Nick", "Points"]].copy()
    table[f'GP_t{round_number} points'] = table["Points"]
    table[f'GP_t{round_number} rank. points'] = table["Points"]
    table[f'GP_t{round_number} position'] = table["#"]

    table["year"] = year
    table["round"] = round_number

    csv_filename = f"gp_{filename[:-5]}.csv"
    output_path = os.path.join(gp_output_directory, csv_filename)
    table.to_csv(output_path, index=False)
    print(f"Saved table from {filename} to {output_path}")

def parse_all_files():
    gp_input_directory = "data/raw/gp/"
    gp_output_directory = "data/processed/gp/"

    round_pattern = r"results\d{4}_r\d+\.html"
    year_pattern = r"results\d{4}.html"

    for filename in sorted(os.listdir(gp_input_directory)):
        if not filename.endswith(".html"):
            continue

        print(f"Parsing file {filename}")

        if re.fullmatch(year_pattern, filename):
            parse_year(filename, gp_input_directory, gp_output_directory)
        elif re.fullmatch(round_pattern, filename):
            parse_round(filename, gp_input_directory, gp_output_directory)
        else:
            raise ValueError(
                f"Filename {filename} not matching format relied upon for year extraction")

if __name__ == "__main__":
    parse_all_files()
