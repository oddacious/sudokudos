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
home.py                           # Entry point
pages/
  gp.py                           # Sudoku Grand Prix page
  wsc.py                          # World Sudoku Championship page
  solver.py                       # Per-solver analysis page
  ratings.py                      # Ratings and leaderboard page
  about.py                        # About page
shared/
  data/
    loaders/
      cached.py                   # @st.cache_data wrappers for all data loading
      gp.py                       # GP data loading logic
      wsc.py                      # WSC data loading logic
      ratings.py                  # Ratings data loading logic
    manipulation.py               # Data transformation and merging
  competitions/
    constants.py                  # Name mappings, playoff results, overrides
    utilities.py                  # Competition metadata (rounds by year)
    results.py                    # Data classes for representing playoff/outcome results per solver
  plots/
    eventoriented.py              # Charts focused on events/competitions
    solveroriented.py             # Charts focused on individual solvers
    ratingoriented.py             # Charts for ratings page
  solvers/
    utils.py                      # Solver data preparation utilities
    performancecollector.py       # Solver performance aggregation
  queryparams.py                  # URL query parameter handling for state persistence
  presentation.py                 # UI setup, headers, theme configuration
  utils.py                        # Shared utilities
data/
  raw/gp/                         # Raw GP HTML/CSV files by year
  raw/wsc/                        # Raw WSC CSV files by year
  processed/gp/                   # Processed GP results
  ratings/                        # Ratings data (parquet files + metadata.json)
```

### Key Patterns

**Name Normalization**: The most complex part of the codebase. Solvers appear with different names across competitions (encoding issues, name formats, name changes). `shared/competitions/constants.py` contains 200+ manual mappings in `WSC_NAME_TO_GP_ID_OVERRIDE`. The matching strategy tries: exact match → flipped name (Last, First → First Last) → lowercase → manual override.

**Data Caching**: Uses `@st.cache_data` decorator for expensive data loading operations. Chart computation helpers (e.g. `_precompute_active_ratings` in `ratingoriented.py`) also use `@st.cache_data` with custom `hash_funcs` for Polars DataFrames.

**Ratings System**: Ratings are pre-computed by a separate external project (`sudoku-ratings`) and imported into this app as parquet files under `data/ratings/`. This app only reads and visualises ratings — it does not compute them. Data updates roughly monthly.

**URL State**: Query parameters via `shared/queryparams.py` allow shareable links with filters and selections persisted in the URL.

### Technologies

- Python 3.13, Streamlit 1.40.2, Polars 1.18.0, Matplotlib 3.9.3, st-theme 1.2.3
- Deployed to Heroku (see `Procfile` and `heroku_setup.sh`)
