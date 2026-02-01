# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Run the application locally (available at http://localhost:8501)
streamlit run home.py

# Install dependencies
pip install -r requirements.txt
```

Load tests are available in `/loadtests/` (uses Selenium with ThreadPoolExecutor).

## Architecture

Sudokudos is a Streamlit web application for analyzing sudoku competition results from the World Sudoku Championship (WSC) and Sudoku Grand Prix (GP).

### Structure

```
home.py                      # Entry point
pages/                       # Streamlit pages (wsc.py, gp.py, solver.py, about.py)
shared/
  data/loaders/              # Data loading (gp.py, wsc.py)
  data/manipulation.py       # Data transformation and merging
  competitions/constants.py  # Name mappings, playoff results, overrides
  competitions/utilities.py  # Competition metadata (rounds by year)
  plots/                     # Visualization (eventoriented.py, solveroriented.py)
  queryparams.py             # URL query parameter handling for state persistence
  presentation.py            # UI setup, headers, theme configuration
data/
  raw/gp/                    # Raw GP HTML/CSV files by year
  raw/wsc/                   # Raw WSC CSV files by year
  processed/gp/              # Processed GP results
```

### Key Patterns

**Name Normalization**: The most complex part of the codebase. Solvers appear with different names across competitions (encoding issues, name formats, name changes). `shared/competitions/constants.py` contains 200+ manual mappings in `WSC_NAME_TO_GP_ID_OVERRIDE`. The matching strategy tries: exact match → flipped name (Last, First → First Last) → lowercase → manual override.

**Data Caching**: Uses `@st.cache_data` decorator for expensive data loading operations.

**URL State**: Query parameters via `shared/queryparams.py` allow shareable links with filters and selections persisted in the URL.

### Technologies

- Python 3.13, Streamlit 1.40.2, Polars 1.18.0, Matplotlib 3.9.3
- Deployed to Heroku (see `Procfile` and `heroku_setup.sh`)
