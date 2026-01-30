"""Utility functions for solvers."""

import polars as pl

from .. import data as shared_data, competitions, utils

def create_data_for_trend_chart(
    full_df, metric, as_percent_of_max, selected_solvers, included_events, window_size):
    """Claculate the data needed for the solver trend chart."""
    flattened_gp = shared_data.create_flat_dataset(full_df, metric=metric)
    flattened_wsc = shared_data.create_flat_dataset(full_df, metric=metric, competition="WSC")
    together = shared_data.merge_flat_datasets([flattened_gp, flattened_wsc])

    if as_percent_of_max:
        together = utils.convert_columns_to_max_pct(together)

    subset = dataframe_by_solvers(together, selected_solvers)

    year_subset = utils.applicable_years(full_df, selected_solvers)
    years_with_data = []

    rounds = []
    year_starts = []
    for year in year_subset:
        if "gp" in included_events and f"{year}_1_gp" in subset:
            year_starts.append(f"{year}_1_gp")
        elif "wsc" in included_events and f"{year}_1_wsc" in subset:
            year_starts.append(f"{year}_1_wsc")
        else:
            # Example case: Only including WSC but have non-existent years
            continue
        years_with_data.append(year)
        for competition_round in range(1, competitions.MAXIMUM_ROUND + 1):
            for competition in ["gp", "wsc"]:
                if competition in included_events:
                    column = f"{year}_{competition_round}_{competition}"
                    if column in subset:
                        rounds.append(column)
                        subset = subset.with_columns(pl.col(column).cast(pl.Float32).alias(column))

    data = { "Round": rounds }
    rolling = {}

    for solver in selected_solvers:
        solver_row = subset.filter(pl.col("user_pseudo_id") == solver)
        if len(solver_row) < 1:
            raise ValueError(f"Expected 1 row for solver \"{solver}\", found {len(solver_row)}")
        record = solver_row[0]
        outcomes = record.select(rounds).row(0)
        name = record.get_column("Name").first()
        data[name] = outcomes
        rolling[name] = pl.Series(outcomes).rolling_mean(window_size, min_periods=1)

    return data, rolling, year_starts, years_with_data

def dataframe_by_solvers(results, joint_solvers):
    """Return the subset of `results` where user_pseudo_id is one of `joint_solvers`"""
    return results.filter(pl.col("user_pseudo_id").is_in(joint_solvers))
