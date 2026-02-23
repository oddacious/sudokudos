"""Load ratings data exported from sudoku-ratings project.

This module provides functions to load pre-computed rating data files
for use in the sudokudos Streamlit app.

Expected files in the ratings data directory:
- ratings_timeseries.parquet: Rating history per solver per round
- leaderboard_current.parquet: Current active leaderboard
- leaderboard_alltime.parquet: All-time peak ratings
- records.parquet: Career records (wins, #1 counts, etc.)
- metadata.json: Export metadata
"""

import json
from pathlib import Path
from typing import Optional

import polars as pl


DEFAULT_RATINGS_DIR = "data/ratings"


def load_ratings_timeseries(
    data_dir: str = DEFAULT_RATINGS_DIR,
    columns: Optional[list[str]] = None,
) -> pl.DataFrame:
    """Load ratings timeseries data.

    Args:
        data_dir: Directory containing ratings files
        columns: Optional list of columns to select (for memory efficiency)

    Returns:
        DataFrame with columns:
        [user_pseudo_id, year, round, competition, comp_idx, rating, n_rounds,
         rank, rank_total, raw_points, adjusted_points]
    """
    path = Path(data_dir) / "ratings_timeseries.parquet"
    if columns:
        return pl.read_parquet(path, columns=columns)
    return pl.read_parquet(path)


def load_current_leaderboard(data_dir: str = DEFAULT_RATINGS_DIR) -> pl.DataFrame:
    """Load current active leaderboard.

    Args:
        data_dir: Directory containing ratings files

    Returns:
        DataFrame with columns:
        [rank, user_pseudo_id, rating, mean_adj_points, n_rounds,
         last_year, last_place, last_round_size]
    """
    path = Path(data_dir) / "leaderboard_current.parquet"
    return pl.read_parquet(path)


def load_alltime_leaderboard(data_dir: str = DEFAULT_RATINGS_DIR) -> pl.DataFrame:
    """Load all-time peak ratings leaderboard.

    Args:
        data_dir: Directory containing ratings files

    Returns:
        DataFrame with columns:
        [rank, user_pseudo_id, peak_rating, peak_year, peak_round,
         peak_competition, n_rounds]
    """
    path = Path(data_dir) / "leaderboard_alltime.parquet"
    return pl.read_parquet(path)


def load_records(data_dir: str = DEFAULT_RATINGS_DIR) -> pl.DataFrame:
    """Load career records.

    Args:
        data_dir: Directory containing ratings files

    Returns:
        DataFrame with columns:
        [user_pseudo_id, ones_count, best_streak, wins_count,
         total_adj_points, total_raw_points, total_rounds]
    """
    path = Path(data_dir) / "records.parquet"
    return pl.read_parquet(path)


def load_ratings_metadata(data_dir: str = DEFAULT_RATINGS_DIR) -> dict:
    """Load ratings export metadata.

    Args:
        data_dir: Directory containing ratings files

    Returns:
        Dict with keys:
        - version: Data format version
        - generated_at: ISO timestamp of export
        - method: Rating method used ('prior' or 'no-prior')
        - data_through: Latest competition (e.g., "2026 GP R2")
        - total_solvers: Total number of unique solvers
    """
    path = Path(data_dir) / "metadata.json"
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_solver_timeseries(
    solver_id: str,
    data_dir: str = DEFAULT_RATINGS_DIR,
) -> pl.DataFrame:
    """Get rating history for a specific solver.

    Args:
        solver_id: The solver's user_pseudo_id
        data_dir: Directory containing ratings files

    Returns:
        DataFrame filtered to specified solver, sorted by comp_idx
    """
    df = load_ratings_timeseries(data_dir)
    return (
        df.filter(pl.col("user_pseudo_id") == solver_id)
        .sort("comp_idx")
    )


def get_leaderboard_at_round(
    comp_idx: int,
    data_dir: str = DEFAULT_RATINGS_DIR,
    top_n: int = 10,
) -> pl.DataFrame:
    """Get leaderboard at a specific point in time.

    Args:
        comp_idx: Competition index to get leaderboard after
        data_dir: Directory containing ratings files
        top_n: Number of top solvers to return

    Returns:
        DataFrame with top N solvers at that point in time
    """
    df = load_ratings_timeseries(data_dir)

    # Get latest record per solver up to comp_idx
    latest = (
        df.filter(pl.col("comp_idx") <= comp_idx)
        .sort(["user_pseudo_id", "comp_idx"], descending=[False, True])
        .group_by("user_pseudo_id")
        .first()
    )

    # Sort by rating and return top N
    return (
        latest
        .sort("rating", descending=True)
        .head(top_n)
        .with_row_count("rank", offset=1)
    )
