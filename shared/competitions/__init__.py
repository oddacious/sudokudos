"""Provides functionality related to competitions."""

from .results import (
    CompetitionResults,
    CompetitionResultsCollector
)

from .constants import (
    MAXIMUM_ROUND,
    WSC_NAME_TO_GP_ID_OVERRIDE,
    GP_PLAYOFF_RESULTS
)

from .utilities import (
    get_max_round,
    wsc_rounds_by_year,
    known_playoff_results
)
