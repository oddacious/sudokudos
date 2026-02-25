import streamlit as st

import shared.presentation

def present_homepage():
    """Create the homepage."""
    shared.presentation.global_setup_and_display()

    st.markdown(
        """
    \U0001F44B Welcome to Sudokudos, a website in celebration of the sudoku world.
    Here you will find results and statistics for (select) major sudoku competitions.

    Use the menu headings or the buttons below to navigate to pages for the World
    Sudoku Championship, Sudoku Grand Prix, or for statistics and comparisons of
    individual solvers.

    **NEW** — Solver rating system over on the [Ratings](ratings) page.
        """)

    st.subheader("Competitions")
    if st.button("World Sudoku Championship"):
        st.switch_page("pages/wsc.py")
    if st.button("Sudoku Grand Prix"):
        st.switch_page("pages/gp.py")

    st.subheader("Solvers")
    if st.button("Solver deep-dive"):
        st.switch_page("pages/solver.py")
    if st.button("Ratings"):
        st.switch_page("pages/ratings.py")

if __name__ == "__main__":
    present_homepage()