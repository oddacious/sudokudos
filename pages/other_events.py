"""This generates the Other Events page."""

import polars as pl
import streamlit as st

import shared.competitions
import shared.data
import shared.data.loaders.cached
import shared.plots.eventoriented
import shared.presentation
import shared.queryparams

# Maps display name → (competition_key, year)
AVAILABLE_EVENTS = {
    "European Sudoku Championship 2026": ("ESC", 2026),
}

def present_other_events():
    """Create the Other Events page."""
    shared.presentation.global_setup_and_display("Other Events")

    esc_raw = shared.data.loaders.cached.load_eurosudoku()
    gp = shared.data.loaders.cached.load_gp()
    esc = shared.data.attempted_mapping(
        esc_raw, gp, manual_override=shared.competitions.ESC_NAME_TO_GP_ID_OVERRIDE)

    selected_event = st.selectbox("Select event", list(AVAILABLE_EVENTS.keys()))
    competition_key, year = AVAILABLE_EVENTS[selected_event]

    if competition_key == "ESC":
        _present_esc(esc, year)


def _present_esc(esc, year):
    """Render the ESC section for a given year."""
    year_df = esc.filter(pl.col("year") == year)

    st.subheader("Summary")

    cols = st.columns([0.1, 0.1, 0.1, 0.7])
    medal_symbols = ["\U0001F947", "\U0001F948", "\U0001F949"]
    for column in range(3):
        with cols[column]:
            winners = year_df.filter(pl.col("ESC_rank") == column + 1)
            for row in winners.iter_rows(named=True):
                st.metric(row["Name"], medal_symbols[column])

    cols = st.columns(2)
    with cols[0]:
        selected_top_n = st.segmented_control("Leaderboard size", [10, 20, 50], default=10)

    cols = st.columns(2)
    with cols[0]:
        fig = shared.plots.eventoriented.create_esc_leaderboard_chart(
            year_df, year=year, top_n=selected_top_n)
        st.pyplot(fig, use_container_width=True)

    st.subheader("Solver tracker")

    available = list(
        year_df
            .sort("ESC_unofficial_rank")
            .get_column("user_pseudo_id")
            .unique(maintain_order=True))

    chosen_solvers = shared.queryparams.extract_query_param_list(
        "solvers", available, default=available[:3])

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
            esc, selected_solvers, year_subset=[year], competition="ESC")
        st.pyplot(fig_violin, use_container_width=True)

    with cols[1]:
        if len(selected_solvers) >= 1:
            fig_trend = shared.plots.eventoriented.create_point_trend_chart(
                esc, selected_solvers, year=year, competition="ESC")
            st.pyplot(fig_trend, use_container_width=True)

    st.subheader("Full results")

    round_cols = sorted([c for c in year_df.columns if c.startswith("ESC_t") and c.endswith(" points")])
    display_cols = ["ESC_rank", "ESC_unofficial_rank", "Name", "Country", "ESC_total"] + round_cols

    table = (year_df
             .select([c for c in display_cols if c in year_df.columns])
             .sort("ESC_unofficial_rank"))
    st.dataframe(table, hide_index=True)


if __name__ == "__main__":
    present_other_events()
