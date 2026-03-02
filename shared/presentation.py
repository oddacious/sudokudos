"""Contains functions related to the presentation of the streamlit site."""

import matplotlib.pyplot as plt
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components
import streamlit_theme

GA_MEASUREMENT_ID = "G-QQC8GHVLBD"

def inject_analytics():
    """Inject Google Analytics and meta description via an invisible iframe (the only
    way to execute scripts in Streamlit). Pageviews fire at most once per page per session."""
    components.html(f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_MEASUREMENT_ID}', {{'send_page_view': false}});
(function() {{
    var key = 'ga_pv_' + window.parent.location.pathname;
    if (!sessionStorage.getItem(key)) {{
        sessionStorage.setItem(key, '1');
        gtag('event', 'page_view', {{'page_path': window.parent.location.pathname}});
    }}
    var desc = window.parent.document.querySelector('meta[name="description"]');
    if (!desc) {{
        desc = window.parent.document.createElement('meta');
        desc.name = 'description';
        window.parent.document.head.appendChild(desc);
    }}
    desc.content = "Explore results, rankings, and solver performance from the World Sudoku Championship and Sudoku Grand Prix.";
}})();
</script>
""", height=0)

def inject_css():
    """Inject CSS tweaks: hide the Streamlit header and reduce top padding."""
    st.markdown("""
<style>
[data-testid="stHeader"] { display: none; }
[data-testid="stCustomComponentV1"] { display: none; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

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

def global_setup_and_display(page_name: Optional[str] = None):
    """Set the title, configure matplotlib, and create the global header."""
    title = f"Sudokudos - {page_name}" if page_name else "Sudokudos - Solvers, scores, and snazzy charts"
    st.set_page_config(
        page_title=title, page_icon="images/sudoku-icon-pastime.png", layout="wide")
    inject_analytics()
    inject_css()
    configure_matplotlib()
    global_header()
