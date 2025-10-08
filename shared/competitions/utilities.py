"""Contains functions that encode domain knowledge about Sudoku competitions."""

def get_max_round(year, competition="GP"):
    """Return the maximum round for a given competition and year.
    
    This is maintained by hand and needs to be updated for new years.
    """
    wsc_map = {
        2010: 10,
        2011: 10,
        2012: 7,
        2014: 10,
        2015: 10,
        2016: 12,
        2017: 16,
        2018: 10,
        2019: 13,
        2022: 12,
        2023: 10,
        2024: 11,
        2025: 12,
    }
    if competition == "GP":
        if int(year) == 2014:
            return 7
        if int(year) > 2014:
            return 8
    elif competition == "WSC":
        if year in wsc_map:
            return wsc_map[year]
        else:
            raise ValueError(f"Year \"{year}\" not found: update `get_max_round`")
    else:
        raise ValueError(f"Unsupported competition \"{competition}\" provided")

    return None

def wsc_rounds_by_year():
    """Return the list of rounds (as integers) for each WSC year.

    Note that the WSC often has a gap in between rounds, with a first set of rounds from 1 to N and
    then another set from 10 or 11 onwards.
    """
    return {
        2025: [1, 2, 3, 4, 5, 6, 7, 10, 11, 12],
        2024: [1, 2, 3, 4, 5, 6, 7, 10, 11],
        2023: range(1, 11),
        2022: [1, 2, 3, 4, 5, 6, 7, 10, 11, 12],
        # No event in 2021 or 2020, although I may later on support the 2021 World Sudoku
        # "Competition"
        2019: [1, 2, 3, 4, 5, 6, 7, 11, 12, 13],
        2018: range(1, 11),
        2017: [1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16],
        2016: [1, 2, 3, 4, 5, 6, 7, 10, 11, 12],
        2015: [1, 2, 3, 4, 5, 6, 8, 9],
        2014: [1, 2, 3, 4, 5, 6, 9, 10],
        # No data currently for the 2013 WSC
        2012: range(1, 8),
        2011: range(1, 11),
        2010: range(1, 11), # These did not originally have numeric names
        # Missing data for 2006-2009 competitions.
    }

def known_playoff_results(year):
    """Return whether we know the playoff results for the given year."""
    if year in (2024, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014):
        return True

    if year in (2025, 2023, 2022, 2021):
        return False

    raise ValueError(f"Unknown GP year \"{year}\"")
