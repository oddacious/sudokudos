"""Collect outcomes for a solver and generate statistics."""

import math

import polars as pl

from .. import competitions, utils

class PerformanceCollector():
    """
    A class to calculate a solver's relative performance in different events.
    """
    LABEL_NO_RECORD = "    N/A (No record found)"

    def __init__(self, solver, included_events, wsc_years):
        """Initiative the object and its internal results list."""
        self.solver = solver
        self.included_events = included_events
        self.wsc_years = wsc_years
        self._solver_results = competitions.CompetitionResultsCollector()

    def gp_performance_by_solver_year(self, subset, year, use_playoffs=True):
        """Calculate the outcomes in the GP for the solver in `year`."""
        if "gp" in self.included_events and year >= 2014:
            if use_playoffs:
                subset = subset.with_columns(
                    (pl.col("Rank")
                     .rank(descending=True) / pl.col("Rank").is_not_null().sum())
                     .alias("percentile")
                )
                subset = subset.with_columns(pl.col("Rank").rank().alias("rank"))
            else:
                subset = subset.with_columns(
                    (pl.col("Points").rank() / pl.count()).alias("percentile")
                )
                subset = subset.with_columns(pl.col("Points").rank(ascending=False).alias("rank"))
            total = sum(subset.get_column("Total GPs").is_not_null())

            solver_rows = subset.filter(pl.col("user_pseudo_id") == self.solver)

            played_gp = solver_rows.get_column("Total GPs").is_null().sum() == 0

            if len(solver_rows) < 1 or not played_gp:
                pctile = 0
                outcome_label = self.LABEL_NO_RECORD
            else:
                pctile = solver_rows.get_column("percentile").first()
                rank = int(solver_rows.get_column("rank").first())
                ordinal_pctile = utils.ordinal_suffix(math.floor(pctile * 100))
                ordinal_rank = utils.ordinal_suffix(rank)
                label_prefix = "\U00002606" if rank <= 3 else "   "
                outcome_label = (f"{label_prefix} {ordinal_pctile} "
                                 f"pctile ({ordinal_rank} of {total})")

            self.solver_results.add_event(f"{year} GP", pctile, outcome_label)

        return self.solver_results

    def wsc_performance_by_solver_year(self, subset, year):
        """Calculate the outcomes in the WSC for the solver in `year`."""
        if year not in self.wsc_years or "wsc" not in self.included_events:
            return None

        solver_record = subset.filter(pl.col("user_pseudo_id") == self.solver)

        # The row won't exist if they didn't do any event. But if they did any
        # event, the row would exist even if the solver did not participate in the WSC.
        wsc_entry = solver_record.get_column("WSC_entry").first()
        participated = len(solver_record) > 0 and wsc_entry is True

        if len(solver_record) > 0:
            is_official = solver_record.get_column("Official").first() is True
        else:
            is_official = True

        if is_official is True:
            rank_column = "Official_rank"
            applicable_subset = subset.filter(pl.col('Official') == 1)
        else:
            rank_column = "Unofficial_rank"
            applicable_subset = subset.filter(pl.col("WSC_entry") == 1)

        applicable_subset = applicable_subset.with_columns(
            (pl.col(rank_column).rank(descending=True) / pl.count()).alias("percentile")
        )

        total = len(applicable_subset)

        if not participated or (len(applicable_subset) == 0 and len(subset) == 0):
            pctile = 0
            outcome_label = self.LABEL_NO_RECORD
        else:
            row_in_applicable_subset = applicable_subset.filter(
                pl.col("user_pseudo_id") == self.solver)
            total = subset.get_column("WSC_entry").is_not_null().sum()
            pctile = row_in_applicable_subset.get_column("percentile").first()
            rank = row_in_applicable_subset.get_column(rank_column).first()
            ordinal_pctile = utils.ordinal_suffix(math.floor(pctile * 100))
            ordinal_rank = utils.ordinal_suffix(int(rank))
            label_prefix = "\U00002606" if rank <= 3 else "   "
            outcome_label = (f"{label_prefix} {ordinal_pctile} "
                             f"pctile ({ordinal_rank} of {total})")
            if not is_official:
                outcome_label += "*"

        self.solver_results.add_event(f"{year} WSC", pctile, outcome_label)

        return self.solver_results

    @property
    def solver_results(self):
        """Access the list of results for the solver."""
        return self._solver_results
