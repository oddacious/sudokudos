"""Loads data from European Sudoku Championship (ESC) events."""

import os
import re

import polars as pl

COUNTRY_TYPO_MAP = {
    "Hungargy": "Hungary",
    "Hungaria": "Hungary",
    "Slovaka": "Slovakia",
    "UN": "Unknown",
}

def load_eurosudoku(csv_directory="data/raw/eurosudoku"):
    """Load all ESC CSV files from a directory and return a combined DataFrame."""
    frames = []

    for filename in sorted(os.listdir(csv_directory)):
        if not filename.endswith(".csv"):
            continue
        match = re.match(r"eurosudoku_(\d{4})\.csv", filename)
        if not match:
            continue
        year = int(match.group(1))
        path = os.path.join(csv_directory, filename)
        df = _load_single_year(path, year)
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"No eurosudoku_YYYY.csv files found in {csv_directory}")

    return pl.concat(frames, how="diagonal")


def _load_single_year(path, year):
    """Load a single ESC CSV and return a normalised DataFrame for that year."""
    raw = pl.read_csv(path, infer_schema_length=200)

    # Determine round count from R-columns present
    round_cols = [c for c in raw.columns if re.fullmatch(r"R\d+", c)]
    num_rounds = len(round_cols)

    rename = {
        "Rank": "ESC_rank",
        "Unofficial": "ESC_unofficial_rank",
        "Sum": "ESC_total",
    }
    for i, col in enumerate(round_cols, start=1):
        rename[col] = f"ESC_t{i} points"

    df = raw.rename(rename)

    # Rank column arrives as strings (empty = non-European entry); cast to nullable Int64
    if df["ESC_rank"].dtype == pl.Utf8 or df["ESC_rank"].dtype == pl.String:
        df = df.with_columns(
            pl.col("ESC_rank").replace("", None).cast(pl.Int64)
        )
    else:
        df = df.with_columns(pl.col("ESC_rank").cast(pl.Int64))

    df = df.with_columns([
        pl.col("ESC_unofficial_rank").cast(pl.Int64),
        pl.col("ESC_total").cast(pl.Float64),
        pl.lit(year).alias("year").cast(pl.Int64),
    ])

    for i in range(1, num_rounds + 1):
        col = f"ESC_t{i} points"
        df = df.with_columns(pl.col(col).cast(pl.Float64))

    # Normalise country typos
    df = df.with_columns(
        pl.col("Country").replace(COUNTRY_TYPO_MAP).alias("Country")
    )

    # Drop columns not needed downstream
    keep = (
        ["Name", "Country", "year", "ESC_rank", "ESC_unofficial_rank", "ESC_total"]
        + [f"ESC_t{i} points" for i in range(1, num_rounds + 1)]
    )
    return df.select(keep)
