import streamlit as st

import shared.data
import shared.data.loaders.gp
import shared.plots.eventoriented
import shared.utils
import shared.presentation

def present_gp():
    """Create the GP page."""
    shared.presentation.global_setup_and_display()

    combined_df = shared.data.loaders.gp.load_gp()

    years = list(reversed(shared.utils.all_available_years(combined_df)))

    if "year" in st.query_params and int(st.query_params["year"]) in years:
        chosen_index = years.index(int(st.query_params["year"]))
    else:
        # 0 will be the most recent year
        chosen_index = 0

    st.markdown("""
        The [Sudoku Grand Prix (GP)](https://gp.worldpuzzle.org/) is the largest annual sudoku
        competition by number of participants. The eight rounds are held online, each four weeks
        apart covering more than half of the year. Each round is crafted by a different nation.
        Solvers are ranked by the sum of their top 6 rounds, and typically the top finishers are
        invited to compete in an in-person playoff for final ranking held during the World Sudoku
        Championship (WSC).
    """)

    selected_year = st.selectbox(
        "Year",
        years,
        index=chosen_index,
        on_change=shared.utils.update_query_param,
        args=("year", "year_selector"),
        key="year_selector")

    year_subset = combined_df[combined_df["year"] == selected_year]

    st.subheader("Summary")

    if shared.utils.known_playoff_results(selected_year):
        cols = st.columns([0.1, 0.1, 0.1, 0.7])

        # Gold, silver, bronze.
        medal_symbols = ["\U0001F947", "\U0001F948", "\U0001F949"]
        for column in range(3):
            with cols[column]:
                winners = year_subset[year_subset["Rank"] == column + 1]
                for _, value in winners.iterrows():
                    st.metric(value["Name"], medal_symbols[column])

    cols = st.columns(2)

    with cols[0]:
        #selected_top_n = st.selectbox("Leaderboard size", [10, 20, 50])
        selected_top_n = st.segmented_control("Leaderboard size", [10, 20, 50], default=10)

    cols = st.columns(2)
    with cols[0]:
        fig_leaderboard = shared.plots.eventoriented.create_leaderboard_chart(
            combined_df, year=selected_year, top_n=selected_top_n)
        st.pyplot(fig_leaderboard, use_container_width=True)

    with cols[1]:
        fig_participants = shared.plots.eventoriented.create_participant_volume_chart(
            combined_df, year=selected_year)
        st.pyplot(fig_participants, use_container_width=True)

    st.subheader("Solver tracker")

    available = list(year_subset.sort_values(by="Rank")["user_pseudo_id"].unique())
    num_default = 3

    chosen_solvers = shared.utils.extract_query_param_list(
        "solvers", available, default=available[:num_default])

    selected_solvers = st.multiselect("Select solvers to compare",
                                    available,
                                    default=chosen_solvers,
                                    on_change=shared.utils.update_query_param,
                                    args=("solvers", "solvers_selector", True),
                                    key="solvers_selector")

    cols = st.columns(2)
    with cols[0]:
        fig_violin = shared.plots.eventoriented.create_violin_chart(
            combined_df, selected_solvers, year_subset=[selected_year])
        st.pyplot(fig_violin, use_container_width=True)

    with cols[1]:
        if len(selected_solvers) >= 1:
            trend_chart = shared.plots.eventoriented.create_point_trend_chart(
                combined_df, selected_solvers, year=selected_year)
            st.pyplot(trend_chart, use_container_width=True)

    subset = combined_df[combined_df["year"] == selected_year].drop(
        columns=["year", "source_file"])

    subset_selected = subset[subset["user_pseudo_id"].isin(selected_solvers)]

    unshown_columns = ["user_pseudo_id", "#"]

    if len(subset_selected) > 0:
        st.dataframe(subset_selected.drop(columns=unshown_columns), hide_index=True)

    st.subheader("All competitors")

    st.write("""Results shown by `Rank`, which orders by playoff position and then by top-6 points.
             For playoff competitors (when known) I create a total ordering by completed round and
             then completion time of last solved puzzle.""")

    st.dataframe(subset.drop(columns=unshown_columns), hide_index=True)

    st.divider()

    cols = st.columns([2,2,10])
    with cols[0]:
        st.link_button("GP homepage", "https://gp.worldpuzzle.org/")
    with cols[1]:
        st.link_button("World Puzzle Federation homepage", "https://worldpuzzle.org/")

if __name__ == "__main__":
    present_gp()
