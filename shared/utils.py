import re
import streamlit as st
import pandas as pd

import shared.constants

QUERY_PARAM_SEPARATOR = "|"

def supported_events():
    """Return the list of events that this code supports."""
    return ("gp", "wsc")

def validate_events(event_list):
    """Raise an exception if the events are supported."""
    supported = supported_events()
    if not all(event in supported for event in event_list):
        raise ValueError(f"Supported events are {supported}; received {event_list}")

def update_query_param(param, selector, multiitem=False):
    """Assign the value in `selector` to the `param` query parameter.
    
    For lists, will concatenate items together.
    """
    if selector not in st.session_state:
        raise ValueError(f"Selector \"{selector}\" not found")

    if multiitem:
        new_value = QUERY_PARAM_SEPARATOR.join(st.session_state[selector])
    else:
        new_value = st.session_state[selector]

    st.query_params[param] = new_value

def extract_query_param_list(param, allowed_items, default=None):
    selected = []
    if param in st.query_params:
        for identifier in st.query_params[param].split(QUERY_PARAM_SEPARATOR):
            if identifier in allowed_items:
                selected.append(identifier)

    if default is not None and len(selected) == 0:
        return default

    return selected

def all_available_years(full_df):
    """Return all years that are represented in a dataframe."""
    return sorted(full_df["year"].unique())

def get_max_round(year, competition="GP"):
    """Return the maximum round for a given competition and year.
    
    This is maintained by hand and needs to be updated for new years.
    """
    wsc_map = {
        2010: 10,
        2011: 10,
        2012: 7,
        2014: 10,
        2015: 10,
        2016: 12,
        2017: 16,
        2018: 10,
        2019: 13,
        2022: 12,
        2023: 10,
        2024: 11,
    }
    if competition == "GP":
        if int(year) == 2014:
            return 7
        if int(year) > 2014:
            return 8
        #raise ValueError(f"Expected years from 2014 onwards, received \"{year}\"")
    elif competition == "WSC":
        if year in wsc_map:
            return wsc_map[year]
        #else:
        #    raise ValueError(f"Unsupported WSC year \"{year}\"")
    else:
        raise ValueError(f"Unsupported competition \"{competition}\" provided")

    return None

def applicable_years(full_df, selected_solvers):
    """Return the year span that any of the solvers participated in.
    
    This uses the first and last years from any solver, and includes any years
    in between.
    """
    years = sorted(full_df["year"].unique())

    # Restrict to years since at least one of the users started and up until the last
    # year with any of them, and include every year in between
    first_year = full_df.loc[full_df.index.isin(selected_solvers), "year"].min()
    final_year = full_df.loc[full_df.index.isin(selected_solvers), "year"].max()
    return [year for year in years if first_year <= year <= final_year]

def ids_to_names(df_with_names, selected_solvers, name_column="Name"):
    """Return the name for an identifier, using the first matched row."""
    names = {}
    for solver_id in selected_solvers:
        matching_rows = df_with_names[df_with_names.index == solver_id][name_column]
        #matching_rows = df_with_names[df_with_names["user_pseudo_id"] == solver_id][name_column]
        if len(matching_rows) == 0:
            raise ValueError(f"Found 0 matching rows for id {solver_id}")
        names[solver_id] = matching_rows.iloc[0]

    return names

def known_playoff_results(year):
    """Return whether we know the playoff results for the given year."""
    if year in (2024, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014):
        return True

    if year in (2023, 2022, 2021):
        return False

    raise ValueError(f"Unknown GP year \"{year}\"")

def sum_top_k_of_n_rounds(full_df, n, k, round_columns, competition="GP"):
    """Calculate the sum of the best `k` of `n` rounds."""
    subset = full_df.copy()
    round_point_columns = []
    found_rounds = 0
    for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        col_name = f"{competition}_t{competition_round} points"
        if col_name not in subset or col_name not in round_columns:
            continue
        found_rounds += 1
        round_point_columns.append(col_name)
        subset[col_name] = pd.to_numeric(subset[col_name], errors="coerce")
        if found_rounds == n:
            break

    cols = round_point_columns
    applicable_point_df = subset[cols]

    row_top_k_sum = applicable_point_df.apply(lambda row: row.nlargest(k).sum(), axis=1)

    return row_top_k_sum

def ordinal_suffix(n):
    """Format numbers as 1st, 2nd, etcetera.
    
    This was copied almost verbatim directly from ChatGPT.
    """
    if 11 <= n % 100 <= 13:  # Handle special cases for 11th, 12th, and 13th
        return f"{n}th"

    last_digit = n % 10

    if last_digit == 1:
        return f"{n}st"

    if last_digit == 2:
        return f"{n}nd"

    if last_digit == 3:
        return f"{n}rd"

    return f"{n}th"

def convert_columns_to_max_pct(df, pattern=r"^\d{4}_\d+"):
    """Convert all columns to a percentage of the column max."""
    for column in df.columns:
        if re.match(pattern, column):
            df[column] = pd.to_numeric(df[column])
            as_pct = df[column] / df[column].max()
            df[column] = as_pct
    return df
