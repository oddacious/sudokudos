import streamlit as st

import shared.data
import shared.data.loaders.gp
import shared.data.loaders.wsc
import shared.plots.solveroriented
import shared.presentation

import time
import psutil
import os
import sys

import polars as pl

def present_solver():
    """Create the solver page."""
    shared.presentation.global_setup_and_display()

    wsc_unmapped = shared.data.loaders.wsc.load_wsc()
    gp = shared.data.loaders.gp.load_gp()
    wsc = shared.data.attemped_mapping(wsc_unmapped, gp)

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
        on_change=shared.utils.update_query_param,
        args=("solver", "user_selector"),
        key="user_selector")

    st.divider()

    chosen_additional = shared.utils.extract_query_param_list("additional", available)

    # Show the events in upper case even though we represent them in lowercase internally.
    supported_events = [event.upper() for event in shared.utils.supported_events()]

    chosen_events = shared.utils.extract_query_param_list(
        "events", supported_events, default=("GP", "WSC"))

    included_events = st.multiselect(
        "Select events to include", 
        ["GP", "WSC"],
        chosen_events,
        on_change=shared.utils.update_query_param,
        args=("events", "event_selector", True),
        key="event_selector")
    events_lower = [event.lower() for event in included_events]

    cols = st.columns(2)

    with cols[0]:
        additional_solvers = st.multiselect(
            "Select additional solvers to compare",
            available,
            default=chosen_additional,
            on_change=shared.utils.update_query_param,
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
            on_change=shared.utils.update_query_param,
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

        with st.expander("See explanation"):
            st.write('''
                * Each point is one round in one competition, with the GP shown earlier than the WSC.
                * Playoff rounds in the GP are not included
                * Years are not uniformly spaced, but rather are weighed by number of rounds.
            ''')

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

    st.write(f"Results shown for: {selected_solver}")

    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    st.write(f"RSS: {memory_info.rss / 1024 ** 2:.2f} MB")  # Resident Set Size
    st.write(f"VMS: {memory_info.vms / 1024 ** 2:.2f} MB")  # Virtual Memory Size

    st.write(f"Filesize for wsc_unammped: {sys.getsizeof(wsc_unmapped) / 1024 / 1024:.2f} mb")
    st.write(f"Filesize for combined_with_wsc: {sys.getsizeof(combined_with_wsc) / 1024 / 1024:.2f} mb")
    st.write(f"Filesize for gp: {sys.getsizeof(gp) / 1024 / 1024:.2f} mb")
    st.write(f"Filesize for wsc: {sys.getsizeof(wsc) / 1024 / 1024:.2f} mb")

    #st.write(f"Filesize for wsc_unammped: {wsc_unmapped.estimated_size() / 1024 / 1024:.2f} mb")
    st.write(f"Filesize for combined_with_wsc: {combined_with_wsc.estimated_size() / 1024 / 1024:.2f} mb")
    #st.write(f"Filesize for gp: {gp.estimated_size() / 1024 / 1024:.2f} mb")
    #st.write(f"Filesize for wsc: {wsc.estimated_size() / 1024 / 1024:.2f} mb")

#if __name__ == "__main__":
#    present_solver()

if __name__ == "__main__":
    start_time = time.perf_counter()
    present_solver()
    end_time = time.perf_counter()
    st.write(f"Execution time: {end_time - start_time:.6f} seconds")

