"""Contains functions to generate plots about solver ratings."""

import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
import matplotlib.ticker
import polars as pl
import streamlit as st


def _build_solver_series(timeseries_df, selected_solvers):
    """Return per-solver DataFrames filtered and sorted by comp_idx, keyed by solver id."""
    result = {}
    for solver in selected_solvers:
        df = (
            timeseries_df
            .filter(pl.col("user_pseudo_id") == solver)
            .sort("comp_idx")
        )
        if not df.is_empty():
            result[solver] = df
    return result


@st.cache_data(hash_funcs={pl.DataFrame: lambda df: df.hash_rows().sum()})
def _precompute_active_ratings(full_timeseries_df):
    """For each comp_idx in the dataset, return the list of active solver ratings.

    A solver is active at a given point if their most recent entry has a year
    within 1 of the target year (i.e. no full calendar year of inactivity).

    Result is cached since full_timeseries_df only changes ~monthly.
    """
    comp_year = dict(
        full_timeseries_df
        .select(["comp_idx", "year"])
        .unique()
        .rows()
    )

    all_rows = (
        full_timeseries_df
        .select(["user_pseudo_id", "comp_idx", "rating", "year"])
        .sort("comp_idx")
        .rows()
    )

    current_state = {}  # {uid: (rating, year)}
    active_ratings_by_comp_idx = {}

    i = 0
    while i < len(all_rows):
        comp_idx = all_rows[i][1]
        # Process all rows sharing this comp_idx before computing active ratings
        while i < len(all_rows) and all_rows[i][1] == comp_idx:
            uid, _, rating, year = all_rows[i]
            current_state[uid] = (rating, year)
            i += 1
        target_year = comp_year[comp_idx]
        active_ratings_by_comp_idx[comp_idx] = [
            r for r, y in current_state.values()
            if y >= target_year - 1
        ]

    return active_ratings_by_comp_idx


def _compute_rating_ranks(full_timeseries_df, selected_solvers, target_comp_idxs):
    """Compute rating rank for selected solvers at specified comp_idx values.

    Rank is computed among solvers who were active at each target point, matching
    the leaderboard definition: a solver is active if their most recent entry
    has a year within 1 of the target year (i.e. no full calendar year of inactivity).
    """
    active_ratings_by_comp_idx = _precompute_active_ratings(full_timeseries_df)

    # Pre-index selected solvers' ratings by comp_idx
    solver_ratings = {}  # {(solver, comp_idx): rating}
    for solver in selected_solvers:
        for comp_idx, rating in (
            full_timeseries_df
            .filter(pl.col("user_pseudo_id") == solver)
            .select(["comp_idx", "rating"])
            .rows()
        ):
            solver_ratings[(solver, comp_idx)] = rating

    results = {}
    for target in target_comp_idxs:
        active_ratings = active_ratings_by_comp_idx.get(target, [])
        for solver in selected_solvers:
            if (solver, target) not in solver_ratings:
                continue
            s_rating = solver_ratings[(solver, target)]
            results[(solver, target)] = (
                sum(1 for r in active_ratings if r > s_rating) + 1
            )

    return results


def _year_ticks(timeseries_df):
    df = (
        timeseries_df
        .group_by("year")
        .agg(pl.col("comp_idx").min().alias("comp_idx"))
        .sort("year")
    )
    return df["comp_idx"].to_list(), df["year"].to_list()


def _label_endpoints(ax, x_vals, y_vals, color):
    """Annotate the first and last point of a series with their y-value."""
    kwargs = dict(textcoords="offset points", va="center", color=color)
    ax.annotate(f"{int(y_vals[0])}", xy=(x_vals[0], y_vals[0]),
                xytext=(-5, 0), ha="right", **kwargs)
    if x_vals[-1] != x_vals[0]:
        ax.annotate(f"{int(y_vals[-1])}", xy=(x_vals[-1], y_vals[-1]),
                    xytext=(5, 0), ha="left", **kwargs)


def _apply_common_style(ax, xticks, xlabels):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks(ticks=xticks, labels=xlabels, rotation=-45)
    ax.legend(frameon=False)


def create_rating_trend_chart(timeseries_df, selected_solvers, year_min=None, year_max=None):
    """Line chart of rating over time for selected solvers."""
    if year_min is not None:
        timeseries_df = timeseries_df.filter(pl.col("year") >= year_min)
    if year_max is not None:
        timeseries_df = timeseries_df.filter(pl.col("year") <= year_max)

    colors = [matplotlib.cm.Set2(i) for i in range(8)]
    xticks, xlabels = _year_ticks(timeseries_df)
    solver_data = _build_solver_series(timeseries_df, selected_solvers)

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, (solver, df) in enumerate(solver_data.items()):
        color = matplotlib.colors.to_hex(colors[i % len(colors)])
        xs = df["comp_idx"].to_list()
        ys = df["rating"].to_list()
        ax.plot(xs, ys, marker="o", markerfacecolor="white", markersize=4,
                color=color, linewidth=1, label=solver.split(" - ")[0])
        _label_endpoints(ax, xs, ys, color)

    ax.set_title("Rating progression")
    _apply_common_style(ax, xticks, xlabels)
    return fig


def create_rank_trend_chart(timeseries_df, selected_solvers, year_min=None, year_max=None):
    """Log-scale ratings-rank-over-time chart; rank 1 at top, y-axis inverted.

    Rating rank is computed globally across all solvers at each point in time,
    not the per-round placement stored in the timeseries 'rank' column.
    """
    # Filter display range but keep full timeseries for rank computation
    display_df = timeseries_df
    if year_min is not None:
        display_df = display_df.filter(pl.col("year") >= year_min)
    if year_max is not None:
        display_df = display_df.filter(pl.col("year") <= year_max)

    colors = [matplotlib.cm.Set2(i) for i in range(8)]
    xticks, xlabels = _year_ticks(display_df)
    solver_display = _build_solver_series(display_df, selected_solvers)

    # Compute rating ranks from the full (unfiltered) timeseries
    all_target_idxs = {
        idx for df in solver_display.values() for idx in df["comp_idx"].to_list()
    }
    rank_map = _compute_rating_ranks(timeseries_df, selected_solvers, all_target_idxs)

    all_ranks = list(rank_map.values())
    max_rank = max(all_ranks) if all_ranks else 1000

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, (solver, df) in enumerate(solver_display.items()):
        color = matplotlib.colors.to_hex(colors[i % len(colors)])
        xs = df["comp_idx"].to_list()
        ys = [rank_map[(solver, x)] for x in xs if (solver, x) in rank_map]
        xs = [x for x in xs if (solver, x) in rank_map]
        if not xs:
            continue
        ax.plot(xs, ys, marker="o", markerfacecolor="white", markersize=4,
                color=color, linewidth=1, label=solver.split(" - ")[0])
        _label_endpoints(ax, xs, ys, color)

    ax.set_yscale("log")
    ax.invert_yaxis()
    ax.set_ylim([max(max_rank * 1.5, 100), 0.8])
    tick_vals = [1, 2, 3, 5, 10, 30, 100, 300, 1000]
    ax.set_yticks(tick_vals)
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    ax.set_title("Race for the throne")
    _apply_common_style(ax, xticks, xlabels)
    return fig
