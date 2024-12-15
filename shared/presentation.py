import streamlit as st

def global_header():
    st.set_page_config(layout="wide")
    st.title("Sudokudos", anchor=False)
    #st.markdown("##### A sudoku community dashboard")
    #st.markdown("##### Sudoku competition results and visuals")
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
