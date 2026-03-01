"""This generates the solver page."""

import streamlit as st

import shared.data
import shared.data.loaders.cached
import shared.plots.ratingoriented
import shared.plots.solveroriented
import shared.presentation
import shared.queryparams
import shared.utils

def present_solver():
    """Create the solver page."""
    shared.presentation.global_setup_and_display("Solver Analysis")

    wsc_unmapped = shared.data.loaders.cached.load_wsc()
    gp = shared.data.loaders.cached.load_gp()
    wsc = shared.data.attempted_mapping(wsc_unmapped, gp)
    timeseries = shared.data.loaders.cached.load_ratings_timeseries()

    combined_with_wsc = shared.data.merge_unflat_datasets(gp, wsc)

    # List solvers by total points in all competitions
    available = shared.data.ids_by_total_points(combined_with_wsc)

    chosen_index = None
    if "solver" in st.query_params and st.query_params["solver"] in available:
        chosen_index = available.index(st.query_params["solver"])
    else:
        chosen_index = 0

    selected_solver = st.selectbox(
        "Select solver",
        available,
        index=chosen_index,
        on_change=shared.queryparams.update_query_param,
        args=("solver", "user_selector"),
        key="user_selector")

    st.divider()

    chosen_additional = shared.queryparams.extract_query_param_list("additional", available)

    # Show the events in upper case even though we represent them in lowercase internally.
    supported_events = [event.upper() for event in shared.utils.supported_competitions()]

    chosen_events = shared.queryparams.extract_query_param_list(
        "events", supported_events, default=("GP", "WSC"))

    included_events = st.multiselect(
        "Select events to include", 
        ["GP", "WSC"],
        chosen_events,
        on_change=shared.queryparams.update_query_param,
        args=("events", "event_selector", True),
        key="event_selector")
    events_lower = [event.lower() for event in included_events]

    cols = st.columns(2)

    with cols[0]:
        additional_solvers = st.multiselect(
            "Select additional solvers to compare",
            available,
            default=chosen_additional,
            on_change=shared.queryparams.update_query_param,
            args=("additional", "additional_selector", True),
            key="additional_selector")

        joint_solvers = [selected_solver] + additional_solvers

        smoothing_level = 8
        if "smoothing" in st.query_params:
            value = int(st.query_params["smoothing"])
            if 1 <= value <= 20:
                smoothing_level = value

        smoothing = st.select_slider(
            "Periods for smoothing",
            options=(range(1, 21)),
            value=smoothing_level,
            on_change=shared.queryparams.update_query_param,
            args=("smoothing", "smoothing_selector"),
            key="smoothing_selector")

        fig_points = shared.plots.solveroriented.create_trend_chart(
            combined_with_wsc,
            joint_solvers,
            metric="points",
            as_percent_of_max=True,
            window_size=smoothing,
            included_events=events_lower)
        if fig_points is not None:
            st.pyplot(fig_points, use_container_width=True)

        fig_position = shared.plots.solveroriented.create_trend_chart(
            combined_with_wsc,
            joint_solvers,
            metric="position",
            window_size=smoothing,
            included_events=events_lower)
        if fig_position is not None:
            st.pyplot(fig_position, use_container_width=True)

    with cols[1]:
        fig_rank = shared.plots.solveroriented.create_rank_chart(
            combined_with_wsc, selected_solver, included_events=events_lower)
        if fig_rank is not None:
            st.pyplot(fig_rank, use_container_width=True)

        with st.expander("See explanation"):
            st.write('''
                * Positions for WSC are final positions
                * Positions for GP use playoff positions when known (mising: 2023, 2022, 2021)
                * An asterisk means the user was an unofficial participant
                * For official WSC participants, rank, percentile, and denominator are of official participants only.
                * For unofficial WSC participants, rank, percentile, and denominator are of all participants.
            ''')

    rating_cols = st.columns(2)
    with rating_cols[0]:
        fig_rating = shared.plots.ratingoriented.create_rating_trend_chart(
            timeseries, joint_solvers)
        st.pyplot(fig_rating, use_container_width=True)

        with st.expander("See explanation"):
            st.write('''
                * Each point is one round in one competition, with the GP shown earlier than the WSC.
                * Playoff rounds in the GP are not included
                * Years are not uniformly spaced, but rather are weighed by number of rounds.
                * See the [Ratings](ratings) page for information on rating calculations.
            ''')
    with rating_cols[1]:
        fig_rating_rank = shared.plots.ratingoriented.create_rank_trend_chart(
            timeseries, joint_solvers)
        st.pyplot(fig_rating_rank, use_container_width=True)

    st.write(f"Results shown for: {selected_solver}")

    st.divider()

    if "GP" in included_events:
        st.subheader("GP")
        subset = shared.plots.solveroriented.gp_table_for_display(gp, joint_solvers)
        st.dataframe(subset)

    if "WSC" in included_events:
        st.subheader("WSC")
        subset = shared.plots.solveroriented.wsc_table_for_display(wsc, joint_solvers)
        st.dataframe(subset)


if __name__ == "__main__":
    present_solver()
