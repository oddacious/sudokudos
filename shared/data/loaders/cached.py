"""Cached wrappers for data loaders that use Streamlit caching."""

from typing import Optional

import streamlit as st

from .gp import load_gp as _load_gp
from .wsc import load_wsc as _load_wsc
from .ratings import (
    load_ratings_timeseries as _load_ratings_timeseries,
    load_current_leaderboard as _load_current_leaderboard,
    load_alltime_leaderboard as _load_alltime_leaderboard,
    load_records as _load_records,
    load_ratings_metadata as _load_ratings_metadata,
    DEFAULT_RATINGS_DIR,
)


@st.cache_data
def load_gp(csv_directory="data/processed/gp", verbose=False, output_csv=None):
    """Load GP data with Streamlit caching."""
    return _load_gp(csv_directory, verbose, output_csv)


@st.cache_data
def load_wsc(csv_directory="data/raw/wsc/"):
    """Load WSC data with Streamlit caching."""
    return _load_wsc(csv_directory)


@st.cache_data
def load_ratings_timeseries(
    data_dir: str = DEFAULT_RATINGS_DIR,
    columns: Optional[tuple[str, ...]] = None,
):
    """Load ratings timeseries with Streamlit caching.

    Note: columns must be a tuple (not list) for hashability.
    """
    cols_list = list(columns) if columns else None
    return _load_ratings_timeseries(data_dir, cols_list)


@st.cache_data
def load_current_leaderboard(data_dir: str = DEFAULT_RATINGS_DIR):
    """Load current leaderboard with Streamlit caching."""
    return _load_current_leaderboard(data_dir)


@st.cache_data
def load_alltime_leaderboard(data_dir: str = DEFAULT_RATINGS_DIR):
    """Load all-time leaderboard with Streamlit caching."""
    return _load_alltime_leaderboard(data_dir)


@st.cache_data
def load_records(data_dir: str = DEFAULT_RATINGS_DIR):
    """Load career records with Streamlit caching."""
    return _load_records(data_dir)


@st.cache_data
def load_ratings_metadata(data_dir: str = DEFAULT_RATINGS_DIR):
    """Load ratings metadata with Streamlit caching."""
    return _load_ratings_metadata(data_dir)
