"""This generates the ratings page."""

import polars as pl
import streamlit as st

import shared.data.loaders.cached
import shared.plots.ratingoriented
import shared.presentation
import shared.queryparams


def _extract_name_parts(df: pl.DataFrame) -> pl.DataFrame:
    """Add Name, Nick, Country columns by parsing user_pseudo_id."""
    uids = df["user_pseudo_id"].to_list()
    names, nicks, countries = [], [], []
    for uid in uids:
        if " - " in uid:
            name_part, country = uid.rsplit(" - ", 1)
        else:
            name_part, country = uid, ""
        if "(" in name_part and ")" in name_part:
            nick_start = name_part.index("(")
            nick_end = name_part.index(")")
            nick = name_part[nick_start + 1:nick_end]
            name = name_part[:nick_start].strip()
        else:
            nick = ""
            name = name_part.strip()
        names.append(name)
        nicks.append(nick)
        countries.append(country)
    return df.with_columns([
        pl.Series("Name", names),
        pl.Series("Nick", nicks),
        pl.Series("Country", countries),
    ])


def present_ratings():
    """Create the ratings page."""
    shared.presentation.global_setup_and_display()

    current_lb = shared.data.loaders.cached.load_current_leaderboard()
    alltime_lb = shared.data.loaders.cached.load_alltime_leaderboard()
    records = shared.data.loaders.cached.load_records()
    metadata = shared.data.loaders.cached.load_ratings_metadata()
    timeseries = shared.data.loaders.cached.load_ratings_timeseries()

    st.caption(
        f"Ratings through {metadata['data_through']}"
        f" · {len(current_lb)} active solvers"
        f" ({metadata['total_solvers']} all time)"
    )

    # Compute last-active competition per solver from timeseries
    last_comp = (
        timeseries
        .sort("comp_idx", descending=True)
        .group_by("user_pseudo_id")
        .first()
        .select([
            "user_pseudo_id",
            pl.concat_str([
                pl.col("year").cast(pl.Utf8),
                pl.lit(" "),
                pl.col("competition"),
                pl.lit(" R"),
                pl.col("round").cast(pl.Utf8),
            ]).alias("Last active"),
        ])
    )

    # --- Top 5 standings snapshot ---
    all_years = sorted(timeseries["year"].unique().to_list())
    current_year = all_years[-1]
    year_min_default = all_years[0]
    year_max_default = all_years[-1]
    top5_solvers = current_lb.head(5)["user_pseudo_id"].to_list()
    snapshot_cols = st.columns(2)
    with snapshot_cols[0]:
        fig_snapshot = shared.plots.ratingoriented.create_rank_trend_chart(
            timeseries, top5_solvers,
            year_min=current_year - 2, year_max=current_year,
        )
        st.pyplot(fig_snapshot, use_container_width=True)

    with snapshot_cols[1]:
        st.write("""
            Welcome to our ratings page! This is a **beta**, such that posted ratings are very much
                subject to change.

            This is an **unofficial** and exploratory rating system, entirely separate from efforts
                by the WPF to define an official rating system.
        """)

    st.divider()

    # --- Leaderboards side by side ---
    cur_named = _extract_name_parts(current_lb)
    at_named = _extract_name_parts(alltime_lb)

    cols = st.columns(2)

    # Build peak column for all-time leaderboard
    peak_col = pl.concat_str([
        pl.col("peak_year").cast(pl.Utf8),
        pl.lit(" "),
        pl.col("peak_competition"),
        pl.lit(" R"),
        pl.col("peak_round").cast(pl.Utf8),
    ]).alias("Peak")

    rating_fmt = {"Rating": st.column_config.NumberColumn(format="%d")}
    peak_rating_fmt = {"Peak rating": st.column_config.NumberColumn(format="%d")}

    with cols[0]:
        st.subheader("Current leaderboard")
        cur_with_last = cur_named.join(last_comp, on="user_pseudo_id", how="left")
        summary = cur_with_last.head(20).select([
            pl.col("rank").alias("#"),
            "Name",
            "Last active",
            pl.col("rating").round(0).cast(pl.Int64).alias("Rating"),
        ])
        st.dataframe(summary, hide_index=True, use_container_width=True,
                     column_config=rating_fmt)

        with st.expander("See full table"):
            full = cur_with_last.select([
                pl.col("rank").alias("#"),
                "Name", "Nick", "Country",
                pl.col("rating").round(0).cast(pl.Int64).alias("Rating"),
                pl.col("n_rounds").alias("Rounds"),
                "Last active",
                pl.col("last_place").alias("Last finish"),
            ])
            st.dataframe(full, hide_index=True, use_container_width=True,
                         column_config=rating_fmt)

    with cols[1]:
        st.subheader("All-time leaderboard")
        at_summary = at_named.head(20).select([
            pl.col("rank").alias("#"),
            "Name",
            peak_col,
            pl.col("peak_rating").round(0).cast(pl.Int64).alias("Peak rating"),
        ])
        st.dataframe(at_summary, hide_index=True, use_container_width=True,
                     column_config=peak_rating_fmt)

        with st.expander("See full table"):
            at_full = at_named.select([
                pl.col("rank").alias("#"),
                "Name", "Nick", "Country",
                pl.col("peak_rating").round(0).cast(pl.Int64).alias("Peak rating"),
                peak_col,
                pl.col("n_rounds").alias("Rounds"),
            ])
            st.dataframe(at_full, hide_index=True, use_container_width=True,
                         column_config=peak_rating_fmt)

    st.divider()

    # --- Solver Showdown ---
    st.subheader("Solver showdown")
    available = current_lb["user_pseudo_id"].to_list()
    chosen_solvers = shared.queryparams.extract_query_param_list(
        "solvers", available, default=available[:3]
    )
    try:
        if "year_min" in st.query_params:
            v = int(st.query_params["year_min"])
            if v in all_years:
                year_min_default = v
        if "year_max" in st.query_params:
            v = int(st.query_params["year_max"])
            if v in all_years:
                year_max_default = v
    except ValueError:
        pass

    selected_solvers = st.multiselect(
        "Select solvers to compare",
        available,
        default=chosen_solvers,
        on_change=shared.queryparams.update_query_param,
        args=("solvers", "solvers_selector", True),
        key="solvers_selector",
    )
    year_range = st.slider(
        "Date range",
        min_value=all_years[0],
        max_value=all_years[-1],
        value=(year_min_default, year_max_default),
        on_change=shared.queryparams.update_range_query_params,
        args=("year_min", "year_max", "year_range_selector"),
        key="year_range_selector",
    )

    if selected_solvers:
        showdown_cols = st.columns(2)
        with showdown_cols[0]:
            fig_rating = shared.plots.ratingoriented.create_rating_trend_chart(
                timeseries, selected_solvers,
                year_min=year_range[0], year_max=year_range[1],
            )
            st.pyplot(fig_rating, use_container_width=True)
        with showdown_cols[1]:
            fig_rank = shared.plots.ratingoriented.create_rank_trend_chart(
                timeseries, selected_solvers,
                year_min=year_range[0], year_max=year_range[1],
            )
            st.pyplot(fig_rank, use_container_width=True)

    st.divider()

    # --- Records ---
    st.subheader("Records")

    _record_metrics = [
        ("Events as #1",               records,    "ones_count"),
        ("Best streak",                records,    "best_streak"),
        ("Event wins",                 records,    "wins_count"),
        ("Rounds played",              records,    "total_rounds"),
        ("Lifetime event points",      records,    "total_raw_points"),
        ("Difficulty-adjusted points", records,    "total_adj_points"),
        ("Peak rating",                alltime_lb, "peak_rating"),
    ]
    _leader_lines = []
    for _label, _df, _col in _record_metrics:
        _row = _df.sort(_col, descending=True).head(1)
        _name = _extract_name_parts(_row)["Name"][0]
        _val = int(round(_row[_col][0]))
        _leader_lines.append(
            f'🥇 **{_label}**: <span style="color: #DAA520">{_name}</span> ({_val})'
        )
    st.markdown("  \n".join(_leader_lines), unsafe_allow_html=True)

    st.caption("Solvers in the top 20 by any metric, sorted by #1 count then best streak.")

    _top_adj_uids = (records.sort("total_adj_points", descending=True)
                     .head(20)["user_pseudo_id"].to_list())
    _top_wins_uids = (records.sort("wins_count", descending=True)
                      .head(20)["user_pseudo_id"].to_list())
    _top_rounds_uids = (records.sort("total_rounds", descending=True)
                        .head(20)["user_pseudo_id"].to_list())
    _top_rating_uids = alltime_lb.head(20)["user_pseudo_id"].to_list()
    _ones_uids = records.filter(pl.col("ones_count") > 0)["user_pseudo_id"].to_list()
    _included_uids = (set(_top_adj_uids) | set(_top_wins_uids)
                      | set(_top_rounds_uids) | set(_top_rating_uids) | set(_ones_uids))
    records_display = (
        _extract_name_parts(
            records
            .filter(pl.col("user_pseudo_id").is_in(_included_uids))
            .sort(["ones_count", "best_streak"], descending=True)
            .join(
                alltime_lb.select(["user_pseudo_id",
                                   pl.col("peak_rating").round(0).cast(pl.Int64)]),
                on="user_pseudo_id", how="left",
            )
        )
        .select([
            "Name", "Nick", "Country",
            pl.col("ones_count").alias("Events as #1"),
            pl.col("best_streak").alias("Best streak"),
            pl.col("wins_count").alias("Event wins"),
            pl.col("total_rounds").alias("Rounds played"),
            pl.col("total_raw_points").round(0).cast(pl.Int64).alias("Lifetime event points"),
            pl.col("total_adj_points").round(0).cast(pl.Int64).alias("Difficulty-adjusted points"),
            pl.col("peak_rating").alias("Peak rating"),
        ])
    )
    st.dataframe(records_display, hide_index=True,
                 column_config={"Peak rating": st.column_config.NumberColumn(format="%d")})

    st.divider()

    st.subheader("The rating algorithm")
    st.write("""
        #### Caveats
        * The algorithm is in **beta** and is subject to change
        * These ratings are **unofficial**, and separate from attempts by the WPF to define an official rating system
        
        #### Rating policies
        * New solvers need 3 rounds before appearing in rankings
        * Solvers drop from the leaderboard after 1 full calendar year of inactivity       
        
        #### Rating philosophy
        These ratings are about *strength*, as opposed to a point system to *reward* event
            performance or participation behavior. A good algorithm is one that has predictive
            power on upcoming performance, such that if solver A is likely to perform better at
            their next event than solver B, then solver A should have a better rating. This gives
            us an empirical and testable criteria for ratings.
        
        However, I do impose a few constraints on purely empirical ratings:
        * Ratings never use forward-looking information
        * Ratings only depend on individual event performance and not on other predictive measures
        * Rating changes should have some smoothness
        * Newly rated players should take multiple events before gaining a high rating
        * Missed a round should not affect ratings (unless missing enough rounds to disqualify from
            the rankings)

        #### Overview of the algorithm
        1. Each individual round in the WSC or GP is treated equally.
        1. Each round has a difficulty level, calculated from the point distribution of
            participating solvers compared to their performance in prior rounds.
        2. Solvers have a historical vector of difficulty-adjusted points from those rounds,
            including a *prior* of three rounds of average performance (from all solvers before
            that solver entered the pool). As such, when solvers first get rated their rating is
            pulled towards average performance.
        3. A solver's rating is the exponentially weighted mean of that difficulty-adjusted points
            vector, with a decay rate 0.9 (most recent rounds weighted highest).

        I evaluated a handful of simple and complex algorithms. This one had strong predictive
            performance while being relatively simple and returning a rating in units of
            difficulty-adjusted points.
    """)


if __name__ == "__main__":
    present_ratings()
