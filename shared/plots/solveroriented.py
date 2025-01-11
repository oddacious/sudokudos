"""Contains functions to generate plots about sudoku solvers."""

import itertools
import polars as pl
import matplotlib
import matplotlib.lines
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.ticker

import shared.competitions
import shared.data
import shared.solvers
import shared.utils

def create_trend_chart(full_df, selected_solvers, metric="points", window_size=8,
                       as_percent_of_max=False, included_events=("gp", "wsc"),
                       colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This shows performance across all competitions and rounds.
    
    Each dot is a round.
    Lines are averages over `window_size` rounds.
    """
    shared.utils.validate_competitions(included_events)
    if len(included_events) == 0:
        return None

    data, rolling, year_starts, years_with_data = shared.solvers.create_data_for_trend_chart(
        full_df, metric, as_percent_of_max, selected_solvers, included_events, window_size)

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

def rank_chart_figure(competition_labels, event_results, outcome_labels, years, colors, name):
    """Generate the bar chart with ranks."""
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

    ax.set_title(f"Ranks for {name}")

    ax.set_xlim([0, 1])
    ax.set_yticks(competition_labels)

    return fig

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
    shared.utils.validate_competitions(included_events)
    if len(included_events) == 0:
        return None

    years = shared.utils.applicable_years(full_df, [solver])

    df = full_df.with_columns(pl.col("Points").cast(pl.Float32).alias("Points"))

    wsc_years = (sorted(full_df.filter((pl.col("WSC_entry") == 1) & pl.col("year").is_not_null())
                        .get_column("year").unique().to_list()))
    performances = shared.solvers.PerformanceCollector(solver, included_events, wsc_years)

    for year in years:
        subset = df.filter(pl.col("year") == year)

        performances.gp_performance_by_solver_year(subset, year, use_playoffs=use_gp_playoffs)
        performances.wsc_performance_by_solver_year(subset, year)

    competition_labels = performances.solver_results.all_competition_names()
    competition_results = performances.solver_results.all_competition_results()
    outcome_labels = performances.solver_results.all_competition_outcome_descriptions()

    fig = rank_chart_figure(
        competition_labels, competition_results, outcome_labels, years, colors,
        shared.utils.ids_to_names(full_df, [solver])[solver])

    return fig
