import polars as pl

import streamlit as st

import shared.data
import shared.data.loaders.gp
import shared.data.loaders.wsc
import shared.plots.eventoriented
import shared.presentation
import shared.queryparams
import shared.utils

def present_wsc():
    """Create the WSC page."""
    shared.presentation.global_setup_and_display()

    gp = shared.data.loaders.gp.load_gp()
    wsc_unmapped = shared.data.loaders.wsc.load_wsc()
    wsc = shared.data.attemped_mapping(wsc_unmapped, gp)

    years = list(reversed(shared.utils.all_available_years(wsc)))

    # For years, 0 will be the most recent year
    chosen_index = shared.queryparams.retrieve_query_value_with_default("year", years, 0)

    with st.expander("Background", expanded=True):
        st.markdown("""
            The [World Sudoku Championship](https://en.wikipedia.org/wiki/World_Sudoku_Championship)
            is typically the culminating event of the
            [sudoku year](https://worldpuzzle.org/events/calendar), where many of the most
            dedicated solvers come together in some host city for the competion and festivities.
            Overseen by the [World Puzzle Federation](https://worldpuzzle.org/) and hosted together
            with the World Puzzle Championship, the WSC involves multiple individual and team
            rounds of excellent and challenging sudoku puzzles.
                    
            The WSC makes the distinction between *official* and *unofficial* competitors, where
            official competitors are limited to four per nation who typically form their country's
            "A" team in the team competition, or are parts of "UN" teams if their country could not
            form a full team.
        """)

    selected_year = st.selectbox(
        "Year",
        years,
        index=chosen_index,
        on_change=shared.queryparams.update_query_param,
        args=("year", "year_selector"),
        key="year_selector")

    st.subheader("Summary")

    wsc_unmapped_subset = wsc_unmapped.filter(pl.col("year") == selected_year)

    cols = st.columns([0.1, 0.1, 0.1, 0.7])

    # Gold, silver, bronze.
    medal_symbols = ["\U0001F947", "\U0001F948", "\U0001F949"]
    for column in range(3):
        with cols[column]:
            winners = wsc_unmapped_subset.filter(pl.col("Official_rank") == column + 1)
            for row in winners.iter_rows(named=True):
                st.metric(row["Name"], medal_symbols[column])

    cols = st.columns(2)

    with cols[0]:
        selected_top_n = st.segmented_control("Leaderboard size", [10, 20, 50], default=10)

    cols = st.columns(2)
    with cols[0]:
        fig_leaderboard = shared.plots.eventoriented.create_wsc_leaderboard_chart(
            wsc_unmapped, year=selected_year, top_n=selected_top_n)
        st.pyplot(fig_leaderboard, use_container_width=True)

    st.subheader("Solver tracker")
    year_subset = wsc.filter(pl.col("year") == selected_year)

    available = list(
        year_subset
            .sort(by=["Unofficial_rank"], descending=False)
            .get_column("user_pseudo_id")
            .unique(maintain_order=True))

    num_default = 3

    chosen_solvers = shared.utils.extract_query_param_list(
        "solvers", available, default=available[:num_default])

    selected_solvers = st.multiselect(
        "Select solvers to compare",
        available,
        default=chosen_solvers,
        on_change=shared.queryparams.update_query_param,
        args=("solvers", "solvers_selector", True),
        key="solvers_selector")

    cols = st.columns(2)
    with cols[0]:
        fig_violin = shared.plots.eventoriented.create_violin_chart(
            wsc, selected_solvers, year_subset=[selected_year], competition="WSC")
        st.pyplot(fig_violin, use_container_width=True)

    with cols[1]:
        if len(selected_solvers) >= 1:
            trend_chart = shared.plots.eventoriented.create_point_trend_chart(
                wsc, selected_solvers, year=selected_year, competition="WSC")
            st.pyplot(trend_chart, use_container_width=True)

    # Generate a clean dataset of the selected users
    year_data_mapped = year_subset
    kept_columns = ["Name", "Official", "Official_rank", "WSC_total", "user_pseudo_id"]
    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"WSC_t{wsc_round} points"
        if colname in year_data_mapped:
            # Some rounds don't exist in all years, but they still have columns because
            # all years are represented in one large table that contains a column for
            # every possible round.
            if year_data_mapped.get_column(colname).is_null().sum() != len(year_data_mapped):
                kept_columns.append(colname)

    year_data_mapped = year_data_mapped.select(kept_columns)
    matching_users = year_data_mapped.filter(pl.col("user_pseudo_id").is_in(selected_solvers))
    matching_users = matching_users.drop("user_pseudo_id")
    st.dataframe(matching_users.sort("Official_rank"))

    st.subheader("All competitors")

    year_data = wsc_unmapped.filter(pl.col("year") == selected_year).drop(["year", "WSC_entry"])

    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"WSC_t{wsc_round} points"
        if colname in year_data:
            if year_data.get_column(colname).is_null().sum() == len(year_data):
                year_data = year_data.drop(colname)

    st.dataframe(year_data, hide_index=True)

if __name__ == "__main__":
    present_wsc()
