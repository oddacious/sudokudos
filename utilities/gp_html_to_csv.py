
import os
from io import StringIO
import pandas as pd
import bs4
from bs4 import BeautifulSoup

gp_input_directory = "data/raw/gp/"
gp_output_directory = "data/processed/gp/"

for filename in sorted(os.listdir(gp_input_directory)):
    if not filename.endswith(".html"):
        continue

    print(f"Parsing file {filename}")

    if len(filename) < 10:
        raise ValueError(f"Filename {filename} not matching format relied upon for year extraction")
    
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