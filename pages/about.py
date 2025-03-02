"""This generates the about page."""

import streamlit as st

import shared.presentation

def present_about():
    """Create the About page."""
    shared.presentation.global_setup_and_display()

    st.subheader("Contact")
    st.write("""
             Please send any questions, suggestions, data (:crossed_fingers:), fixes, hate mail,
             etc., to fumble.to.victory@gmail.com""")
    st.divider()

    st.subheader("Issues")
    st.markdown("*Of which there are many.*")
    st.markdown("""
        #### Data completeness
        * WSC:
            * Missing years: 2013, 2009, 2008, 2007, and 2006.
            * Incomplete "Official" labelling: 2022.
        * GP:
            * Missing playoff outcomes: 2023, 2022, and 2021.
        #### Data accuracy  
        * Inexact matching between GP and WSC. And, for that matter, within GP and within WSC.
            * Each WSC was an independent event where competitors entered their names given the
            constraints at the time (e.g. varying support for non-ASCII characters) and where
            the names were output in different formats (e.g. name ordering and capitalization).
            * The GP at least is controlled in one website, but it does not publicly provide an
            identifier. Names and countries are editable, but without updating prior years.
            Nicks are optionally displayed, and either were changeable or some people created
            duplicate accounts.
            * I created some utilities to map names together algorithmically and to find and
            define hardcoded lists. I expect I have both false positives (results that I
            connected together but which represent different people with similar names) and
            many false negatives (results where I either didn't notice the name equivalence or
            I was not confident in connecting them together).
        * Imprecise transcription. Data has come through spreadsheets, websites, and PDF files,
            requiring various parsing methods. In particular, OCR on PDF files was imprecise at
            reading in characters in names.
        #### Data representation
        * Inconsistent labelling of names across the site: Sometimes using the names as written
            in the particular WSC or GP year, and other times using another version of the
            person's name from another source.
        * Forcing a consistent representation of event outcomes. For example, renaming the
            rounds from each WSC into one convention. That is a fairly innocuous example, but
            there may be ways that individual WSC's chose to represent outcomes that my
            normalization discards.
        #### Scope 
        * Only includes WSC and GP for now.
        * No coverage of team results.
        * No coverage of country results.
            * I postponed including countries because of their varying representations. One
            WSC may write "China", another "CHN', another the Chinese flag, another no explicit
            country identification aside from team membership.
            * For a number of solvers their country identification changed over time, such that
            any statistics on countries may have to choose whether to reflect most recent
            national identification, or country at the time, or to reflect multiple countries
            in aggregations.
                """)

    st.divider()
    st.subheader("Acknowledgements")
    st.markdown("""
        First and foremost, to all the people who organize sudoku events, design puzzles, contribute to the
        events in any way, and participate as solvers. The sudoku community is wonderful.

        Special kudos to:

        * *yyao* for sharing full WSC 2022 results.
        * *limt* for noticing missing data for the current GP year for solvers without nicks.

        Data for the Sudoku Grand Prix comes from the GP website at
        [https://gp.worldpuzzle.org](https://gp.worldpuzzle.org/). World Sudoku Championship data comes
        from the various WSC host pages when available (see
        [https://wpc.puzzles.com/history](https://wpc.puzzles.com/history)), from the
        [Internet Archive](https://archive.org) of those pages, or from files that others have
        helpfully shared.

        Authoritative results, and the official presentation of those results, belongs to those
        organizations. I apologize for any errors in my calculations or representations.
                
        The favicon was created by [smalllikeart](https://www.flaticon.com/authors/smalllikeart).
    """)

if __name__ == "__main__":
    present_about()
