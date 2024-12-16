import matplotlib.pyplot as plt

import streamlit as st
import streamlit_theme

def configure_matplotlib():
    theme = streamlit_theme.st_theme()
    if theme and theme['base'] == 'dark':
        plt.style.use('dark_background')
    else:
        plt.style.use('default')

def global_header():
    st.title("Sudokudos", anchor=False)
    st.markdown("#### Solvers, scores, and snazzy charts")
    cols = st.columns(6)
    with cols[0]:
        st.page_link("home.py", label="Home")
    with cols[1]:
        st.page_link("pages/wsc.py", label="WSC")
    with cols[2]:
        st.page_link("pages/gp.py", label="Grand Prix")
    with cols[3]:
        st.page_link("pages/solver.py", label="Solvers")
    #with cols[4]:
    #    st.page_link("pages/solver.py", label="Leaders")
    with cols[4]:
        st.page_link("pages/about.py", label="About")
    st.divider()

def global_setup_and_display():
    st.set_page_config(page_title="Sudokudos", layout="wide")
    configure_matplotlib()
    global_header()
