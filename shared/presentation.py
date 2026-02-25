"""Contains functions related to the presentation of the streamlit site."""

import matplotlib.pyplot as plt

import streamlit as st
import streamlit_theme

def configure_matplotlib():
    """Apply matplotlib general settings."""
    theme = streamlit_theme.st_theme()
    if theme and theme['base'] == 'dark':
        plt.style.use('dark_background')
    else:
        plt.style.use('default')

def global_header():
    """Create the links in the site's global header."""
    st.title("Sudokudos", anchor=False)
    st.markdown("#### Solvers, scores, and snazzy charts")
    cols = st.columns(7)
    with cols[0]:
        st.page_link("home.py", label="Home")
    with cols[1]:
        st.page_link("pages/wsc.py", label="WSC")
    with cols[2]:
        st.page_link("pages/gp.py", label="Grand Prix")
    with cols[3]:
        st.page_link("pages/solver.py", label="Solvers")
    with cols[4]:
        st.page_link("pages/ratings.py", label="Ratings")
    with cols[5]:
        st.page_link("pages/about.py", label="About")
    st.divider()

def global_setup_and_display():
    """Set the title, configure matplotlib, and create the global header."""
    st.set_page_config(
        page_title="Sudokudos", page_icon="images/sudoku-icon-pastime.png", layout="wide")
    configure_matplotlib()
    global_header()
