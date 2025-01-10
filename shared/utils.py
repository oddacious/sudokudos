import re
import streamlit as st
import polars as pl

import shared.constants

def supported_events():
    """Return the list of events that this code supports."""
    return ("gp", "wsc")

def validate_events(event_list):
    """Raise an exception if the events are supported."""
    supported = supported_events()
    if not all(event in supported for event in event_list):
        raise ValueError(f"Supported events are {supported}; received {event_list}")

def all_available_years(full_df):
    """Return all years that are represented in a dataframe."""
    return full_df.select(pl.col("year")).unique().sort(by="year").get_column("year").to_list()

def applicable_years(full_df, selected_solvers):
    """Return the year span that any of the solvers participated in.
    
    This uses the first and last years from any solver, and includes any years
    in between.
    """
    years = sorted(
        full_df.filter(pl.col("year").is_not_null()).get_column("year").unique().to_list())

    # Restrict to years since at least one of the users started and up until the last
    # year with any of them, and include every year in between
    filtered = full_df.filter(pl.col("user_pseudo_id").is_in(selected_solvers))
    if len(filtered) == 0:
        return []
    first_year = filtered.get_column("year").min()
    final_year = filtered.get_column("year").max()
    return [year for year in years if first_year <= year <= final_year]

def ids_to_names(df_with_names, selected_solvers, name_column="Name"):
    """Return the name for an identifier, using the first matched row."""
    names = {}
    for solver_id in selected_solvers:
        matching_rows = (
            df_with_names.filter(pl.col("user_pseudo_id") == solver_id).get_column(name_column))
        if len(matching_rows) == 0:
            raise ValueError(f"Found 0 matching rows for id {solver_id}")
        names[solver_id] = matching_rows.first()

    return names

def sum_top_k_of_n_rounds(full_df, n, k, round_columns, competition="GP"):
    """Calculate the sum of the best `k` of `n` rounds."""
    round_point_columns = []
    found_rounds = 0
    for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        col_name = f"{competition}_t{competition_round} points"
        if col_name not in full_df or col_name not in round_columns:
            continue
        found_rounds += 1
        round_point_columns.append(col_name)
        if found_rounds == n:
            break

    applicable_point_df = full_df.select(round_point_columns)

    transposed_df = applicable_point_df.transpose()

    row_top_k_sum = transposed_df.select([
        pl.col(c).top_k(k).sum().alias(c) for c in transposed_df.columns
    ])

    row_top_k_sum_transposed = row_top_k_sum.transpose()

    return row_top_k_sum_transposed

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
            df = df.with_columns(pl.col(column).cast(pl.Float32).alias(column))
            as_pct = df.get_column(column) / df.get_column(column).max()
            df = df.with_columns(
                pl.lit(as_pct).alias(column)
            )
    return df
