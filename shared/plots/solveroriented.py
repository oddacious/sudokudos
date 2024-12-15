import math
import itertools
import pandas as pd
import matplotlib
import matplotlib.lines
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.ticker

import shared.data
import shared.utils

def create_trend_chart(full_df, selected_solvers, metric="points", window_size=8,
                       as_percent_of_max=False, included_events=("gp", "wsc"),
                       colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This shows performance across all competitions and rounds.
    
    Each dot is a round.
    Lines are averages over `window_size` rounds.
    """
    shared.utils.validate_events(included_events)
    if len(included_events) == 0:
        return None

    flattened_gp = shared.data.create_flat_dataset(full_df, metric=metric)
    flattened_wsc = shared.data.create_flat_dataset(full_df, metric=metric, competition="WSC")
    together = shared.data.merge_flat_datasets([flattened_gp, flattened_wsc])

    if as_percent_of_max:
        together = shared.utils.convert_columns_to_max_pct(together)

    subset = together[together["user_pseudo_id"].isin(selected_solvers)].copy()

    year_subset = shared.utils.applicable_years(full_df, selected_solvers)
    years_with_data = []

    rounds = []
    year_starts = []
    for year in year_subset:
        if "gp" in included_events and f"{year}_1_gp" in subset:
            year_starts.append(f"{year}_1_gp")
        elif "wsc" in included_events and f"{year}_1_wsc" in subset:
            year_starts.append(f"{year}_1_wsc")
        else:
            # Example case: Only including WSC but have non-existent years
            continue
        years_with_data.append(year)
        for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
            for competition in ["gp", "wsc"]:
                if competition in included_events:
                    column = f"{year}_{competition_round}_{competition}"
                    if column in subset:
                        rounds.append(column)
                        subset[column] = pd.to_numeric(subset[column], errors='coerce')

    data = { "Round": rounds }
    rolling = {}

    for solver in selected_solvers:
        solver_row = subset[subset["user_pseudo_id"] == solver]
        if len(solver_row) < 1:
            raise ValueError(f"Expected 1 row for solver \"{solver}\", found {len(solver_row)}")
        record = solver_row.iloc[0]
        outcomes = record[rounds]
        data[record["Name"]] = outcomes
        rolling[record["Name"]] = outcomes.rolling(window=window_size, min_periods=1).mean()

    xticks = year_starts
    xlabels = years_with_data

    fig, ax = plt.subplots(figsize=(8, 5))

    color_cycle = itertools.cycle(plt.cycler('color', colors).by_key()['color'])

    for column, record in data.items():
        if column == "Round":
            continue
        same_color = matplotlib.colors.to_hex(next(color_cycle))
        ax.plot(data['Round'], record, linestyle='', marker='o', markerfacecolor='white',
                markersize=4, color=same_color)
        ax.plot(data['Round'], rolling[column], label=column, color=same_color, linewidth=1)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xticks(ticks=xticks, labels=xlabels, rotation=-45)

    title = f"{metric.title()} over time"
    if as_percent_of_max:
        title = title + " (as % of top score)"
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
        ax.set_ylim([0, 1.1])
    ax.set_title(title)
    ax.text(0.5, 0.97, f'Lines are moving averages over {window_size} rounds', ha='center',
            va='center', transform=ax.transAxes, fontsize=10, color='gray')

    ax.legend(frameon=False)

    return fig

class EventResults():
    """
    A class to represent the result for a specific event and solver.
    """
    def __init__(self, event_name=None, event_result=None, outcome_description=None):
        """Create the object and optionally initalize its members."""
        self.event_name = event_name
        self.event_result = event_result
        self.outcome_description = outcome_description

class EventResultsBySolver():
    """
    A class to represent all event results for a solver.
    """
    def __init__(self):
        """Initiative the object."""
        self.event_results = []

    def add_event(self, event_name, event_result, outcome_description):
        """Add a single event to the event list."""
        self.event_results.append(EventResults(event_name, event_result, outcome_description))

    def retrieve_events(self):
        """Retrieve all events."""
        return self.event_results

    def all_event_names(self):
        """Retrieve a generator of all event names."""
        return [item.event_name for item in self.event_results]

    def all_event_results(self):
        """Retrieve a generator of all event results."""
        return [item.event_result for item in self.event_results]

    def all_event_outcome_descriptions(self):
        """Retrieve a generator of all event outcome descriptions."""
        return [item.outcome_description for item in self.event_results]

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
        self._solver_results = EventResultsBySolver()

    def gp_performance_by_solver_year(self, subset, year, use_playoffs=True):
        """Calculate the outcomes in the GP for the solver in `year`."""
        if "gp" in self.included_events and year >= 2014:
            if use_playoffs:
                percentiles = subset["Rank"].rank(pct=True, ascending=False)
                ranks = subset["Rank"].rank()
            else:
                percentiles = subset["Points"].rank(pct=True)
                ranks = subset["Points"].rank(ascending=False)
            total = sum(subset["Total GPs"].notna())

            solver_rows = subset[subset['user_pseudo_id'] == self.solver]
            row_index = solver_rows.index

            played_gp = sum(solver_rows["Total GPs"].isna()) == 0

            if len(row_index) < 1 or not played_gp:
                pctile = 0
                outcome_label = self.LABEL_NO_RECORD
            else:
                pctile = percentiles[row_index].iloc[0]
                rank = int(ranks[row_index].iloc[0])
                ordinal_pctile = shared.utils.ordinal_suffix(math.floor(pctile * 100))
                ordinal_rank = shared.utils.ordinal_suffix(rank)
                label_prefix = "\U00002606" if rank <= 3 else "   "
                outcome_label = (f"{label_prefix} {ordinal_pctile} "
                                 f"pctile ({ordinal_rank} of {total})")

            self.solver_results.add_event(f"{year} GP", pctile, outcome_label)

        return self.solver_results

    def wsc_performance_by_solver_year(self, subset, year):
        """Calculate the outcomes in the WSC for the solver in `year`."""
        if year not in self.wsc_years or "wsc" not in self.included_events:
            return

        solver_record = subset[subset['user_pseudo_id'] == self.solver]

        # The row won't exist if they didn't do any event. But if they did any
        # event, the row would exist even if the solver did not participate in the WSC.
        participated = len(solver_record) > 0 and solver_record["WSC_entry"].iloc[0] is True

        if len(solver_record) > 0:
            is_official = solver_record["Official"].iloc[0] is True
        else:
            is_official = True

        if is_official is True:
            rank_column = "Official_rank"
            applicable_subset = subset[subset['Official'] == 1]
        else:
            rank_column = "Unofficial_rank"
            applicable_subset = subset

        percentiles = pd.to_numeric(applicable_subset[rank_column]).rank(pct=True, ascending=False)
        total = len(applicable_subset)

        criteria = (subset['user_pseudo_id'] == self.solver) & (subset['Official'] == 0)
        row_index_unofficial = subset[criteria].index
        row_index = applicable_subset[applicable_subset['user_pseudo_id'] == self.solver].index

        if not participated or (row_index_unofficial == -1 and row_index == -1):
            pctile = 0
            outcome_label = self.LABEL_NO_RECORD
        else:
            total = sum(subset["WSC_entry"].notna())
            pctile = percentiles[row_index].iloc[0]
            solver_rows = applicable_subset['user_pseudo_id'] == self.solver
            rank = applicable_subset[solver_rows][rank_column].iloc[0]
            ordinal_pctile = shared.utils.ordinal_suffix(math.floor(pctile * 100))
            ordinal_rank = shared.utils.ordinal_suffix(int(rank))
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

def create_rank_chart(
        full_df,
        solver,
        included_events=("GP", "WSC"),
        use_gp_playoffs=True,
        colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This shows a solver's rank for each competition.
    
    This shows the years they participated in, and every year in between.
    This adds stars for top-3 performance.
        - Position for the WSC includes playoff results
        - Position for the GP does not include playoffs, which I could not find
    """
    shared.utils.validate_events(included_events)
    if len(included_events) == 0:
        return None

    years = shared.utils.applicable_years(full_df, [solver])

    df = full_df.copy()
    df["Points"] = pd.to_numeric(df["Points"], errors="coerce")

    wsc_years = sorted(full_df[full_df["WSC_entry"] == 1]["year"].unique())
    performances = PerformanceCollector(solver, included_events, wsc_years)

    for year in years:
        subset = df[df["year"] == year]

        performances.gp_performance_by_solver_year(subset, year, use_playoffs=use_gp_playoffs)
        performances.wsc_performance_by_solver_year(subset, year)

    competition_labels = performances.solver_results.all_event_names()
    event_results = performances.solver_results.all_event_results()
    outcome_labels = performances.solver_results.all_event_outcome_descriptions()

    fig, ax = plt.subplots(figsize=(5, len(years) * 0.75))
    height = 0.75
    width = height / 10
    bars = ax.barh(
        competition_labels,
        [result-width/2 for result in event_results],
        color=colors[0],
        height=height)

    # I'm unsure why I need this, but otherwise sometimes it visually looks
    # like the ellipse is a bit taller than the bar.
    ellipse_height_scaler = 0.96

    for event_bar, label, result in zip(bars, outcome_labels, event_results):
        if "(1st" in label:
            event_bar.set_color("gold")
        elif "(2nd" in label:
            event_bar.set_color("silver")
        elif "(3rd" in label:
            event_bar.set_color('#DAA520')
        ax.text(1.01, event_bar.get_y() + event_bar.get_height() / 2,
                label,
                va='center',
                ha='left')
        color = event_bar.get_facecolor()
        ax.add_patch(
            matplotlib.patches.Ellipse(
                (result-width/2, event_bar.get_y() + event_bar.get_height() / 2),
                width=width,
                height=height * ellipse_height_scaler,
                color=color,
                zorder=10))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    name = shared.utils.ids_to_names(full_df, [solver])[solver]
    ax.set_title(f"Ranks for {name}")

    ax.set_xlim([0, 1])
    ax.set_yticks(competition_labels)

    return fig
