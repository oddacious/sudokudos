import streamlit as st

import shared.data
import shared.data.loaders.gp
import shared.data.loaders.wsc
import shared.plots.eventoriented
import shared.presentation
import shared.utils

def present_wsc():
    """Create the WSC page."""
    shared.presentation.global_header()

    wsc_unmapped = shared.data.loaders.wsc.load_wsc()
    gp = shared.data.loaders.gp.load_gp()
    wsc = shared.data.attemped_mapping(wsc_unmapped, gp)

    years = list(reversed(shared.utils.all_available_years(wsc)))

    if "year" in st.query_params and int(st.query_params["year"]) in years:
        chosen_index = years.index(int(st.query_params["year"]))
    else:
        # 0 will be the most recent year
        chosen_index = 0

    selected_year = st.selectbox(
        "Year",
        years,
        index=chosen_index,
        on_change=shared.utils.update_query_param,
        args=("year", "year_selector"),
        key="year_selector")

    st.subheader("Summary")

    wsc_unmapped_subset = wsc_unmapped[wsc_unmapped["year"] == selected_year]

    cols = st.columns([0.1, 0.1, 0.1, 0.7])

    # Gold, silver, bronze.
    medal_symbols = ["\U0001F947", "\U0001F948", "\U0001F949"]
    for column in range(3):
        with cols[column]:
            winners = wsc_unmapped_subset[wsc_unmapped_subset["Official_rank"] == column + 1]
            for _, value in winners.iterrows():
                st.metric(value["Name"], medal_symbols[column])

    cols = st.columns(2)

    with cols[0]:
        selected_top_n = st.segmented_control("Leaderboard size", [10, 20, 50], default=10)

    cols = st.columns(2)
    with cols[0]:
        fig_leaderboard = shared.plots.eventoriented.create_wsc_leaderboard_chart(
            wsc_unmapped, year=selected_year, top_n=selected_top_n)
        st.pyplot(fig_leaderboard, use_container_width=True)
    #with cols[1]:
    #    st.metric("", "")
    #    st.metric("", "")
    #    st.metric("Tantan Dai", "\U0001F947")
    #    st.metric("Tantan Dai", "\U0001F948")
    #    st.metric("Tantan Dai", "\U0001F949")

    st.subheader("Solver tracker")
    year_subset = wsc[wsc["year"] == selected_year]

    available = list(year_subset["user_pseudo_id"].unique())
    num_default = 3

    chosen_solvers = shared.utils.extract_query_param_list(
        "solvers", available, default=available[:num_default])

    selected_solvers = st.multiselect(
        "Select solvers to compare",
        available,
        default=chosen_solvers,
        on_change=shared.utils.update_query_param,
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
    year_data_mapped = wsc[wsc["year"] == selected_year]
    kept_columns = ["user_pseudo_id", "Name", "Official", "Official_rank", "WSC_total"]
    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"WSC_t{wsc_round} points"
        if colname in year_data_mapped:
            # Some rounds don't exist in all years, but they still have columns because
            # all years are represented in one large table that contains a column for
            # every possible round.
            if sum(year_data_mapped[colname].isna()) != len(year_data_mapped):
                kept_columns.append(colname)

    year_data_mapped = year_data_mapped[kept_columns]
    matching_user_rows = year_data_mapped["user_pseudo_id"].isin(selected_solvers)
    matching_users = year_data_mapped[matching_user_rows].copy()
    matching_users.drop(columns=["user_pseudo_id"], inplace=True)
    st.dataframe(matching_users.sort_values(by="Official_rank"), hide_index=True)

    st.subheader("All competitors")

    year_data = wsc_unmapped[wsc_unmapped["year"] == selected_year].drop(
        columns=["year", "WSC_entry"])

    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"WSC_t{wsc_round} points"
        if colname in year_data:
            if sum(year_data[colname].isna()) == len(year_data):
                year_data.drop(columns=[colname], inplace=True)

    st.dataframe(year_data, hide_index=True)

if __name__ == "__main__":
    present_wsc()
