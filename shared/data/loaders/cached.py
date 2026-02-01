"""Cached wrappers for data loaders that use Streamlit caching."""

import streamlit as st

from .gp import load_gp as _load_gp
from .wsc import load_wsc as _load_wsc


@st.cache_data
def load_gp(csv_directory="data/processed/gp", verbose=False, output_csv=None):
    """Load GP data with Streamlit caching."""
    return _load_gp(csv_directory, verbose, output_csv)


@st.cache_data
def load_wsc(csv_directory="data/raw/wsc/"):
    """Load WSC data with Streamlit caching."""
    return _load_wsc(csv_directory)
