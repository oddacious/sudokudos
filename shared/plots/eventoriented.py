"""Contains functions to generate plots for sudoku competitions."""

import itertools
import numpy as np
import polars as pl
import matplotlib
import matplotlib.lines
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.path
import matplotlib.ticker

import shared.competitions
import shared.data
import shared.utils

def create_participant_volume_chart(
        full_df, year=2024, colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This chart shows the number of participants for each round.
    
    This shows the number who played in prior years, or are in their first
    year, or in their first round of the year.

    Currently only supports the GP.
    """
    ids_prior_years = full_df.filter(pl.col("year") < year).get_column("user_pseudo_id").unique()

    this_year = full_df.filter(pl.col("year") == year)

    labels = []
    veteran_counts = []
    first_round_counts = []
    earlier_this_year_counts = []

    num_rounds = shared.competitions.get_max_round(year)

    previously_seen_this_year = None
    for gp_round in range(1, num_rounds + 1):
        played = this_year.filter(pl.col(f"GP_t{gp_round} position").is_not_null())
        played_ids = played.get_column("user_pseudo_id")

        veterans = played_ids.is_in(ids_prior_years)
        non_veterans = ~veterans

        num_first_year = len(played_ids) - sum(veterans)
        if previously_seen_this_year is None:
            sum_seen_earlier_this_year = 0
        else:
            non_veteran_ids = played_ids.filter(non_veterans)
            seen_this_year = non_veteran_ids.is_in(previously_seen_this_year)
            sum_seen_earlier_this_year = sum(seen_this_year)

        if previously_seen_this_year is None:
            previously_seen_this_year = list(played_ids)
        else:
            previously_seen_this_year.extend(list(played_ids))

        num_veterans = sum(veterans)
        num_first_round = num_first_year - sum_seen_earlier_this_year

        labels.append(f"{year}_{gp_round}")
        veteran_counts.append(num_veterans)
        first_round_counts.append(num_first_round)
        earlier_this_year_counts.append(sum_seen_earlier_this_year)

    fig, ax = plt.subplots()

    ax.bar(labels, veteran_counts, label='Played prior years', color=colors[0])
    ax.bar(
        labels,
        earlier_this_year_counts,
        bottom=veteran_counts,
        label='New earlier this year',
        color=colors[1])
    ax.bar(labels,
           first_round_counts,
           bottom=np.array(veteran_counts) + np.array(earlier_this_year_counts),
           label='New this round',
           color=colors[2])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title(f'Sudoku Grand Prix participant volume ({year})')
    ax.legend(frameon=False)

    return fig

def create_leaderboard_chart(full_df, year=2024, top_n=10,
                             colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This creates a horizontal bar chart of the top scores for a GP year."""
    year_df = full_df.filter(pl.col("year") == year)
    year_df = year_df.with_columns(
        pl.col("Points").cast(pl.Float32).alias("Points"),
        pl.col("PointsTop6").cast(pl.Float32).alias("PointsTop6"),
    )

    subset = year_df.sort("PointsTop6", descending=True).head(top_n)

    labels = subset.get_column("Name")
    points = subset.get_column("PointsTop6")
    extra_points = subset.get_column("Points") - subset.get_column("PointsTop6")

    fig, ax = plt.subplots(figsize=(6.4, 10))
    ax.barh(labels, points, label='Top 6 rounds', color=colors[0])
    ax.barh(labels, extra_points, left=points, label='Extra rounds', color=colors[1])
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()
    ax.legend(frameon=False, bbox_to_anchor=(1.05, 1.05), loc='lower center')
    #ax.legend(frameon=False, loc='lower right')
    ax.set_title(f"Sudoku Grand Prix point leaders ({year})", pad=50)

    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    return fig

def create_playoff_bump_chart(full_df, year=2024,
                              colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This creates a bump chart comparing GP qualifying rank to final playoff rank."""
    green = "#4caf50"
    amber = "#f0ad4e"
    grey = "#bdbdbd"

    year_df = full_df.filter(pl.col("year") == year)

    # Include the full qualifying field on the left side -- even solvers whose playoff
    # result we don't know -- so the known results are spaced according to their real
    # Rank_before_playoffs rather than being compressed into a tiny subset. Only rows with
    # a known Playoff_rank get a connecting line to the right; the rest are shown dimmed
    # as a placeholder, without claiming they skipped the playoff (see
    # known_full_playoff_order for the distinction).
    qualified = year_df.filter(
        pl.col("Playoff_rank").is_not_null()
        | ((pl.col("Rank_before_playoffs") <= 10) & pl.col("Playoff_rank").is_null())
    ).sort("Rank_before_playoffs")

    # Figure height scales with row count (so fewer rows stay compact) but is capped to
    # match the height of the other charts on the page.
    fig_height = min(10, 1.0 + 0.3 * max(len(qualified), 1))
    fig, ax = plt.subplots(figsize=(6.4, fig_height))

    if len(qualified) == 0:
        ax.text(0.5, 0.5, "No playoff data available", ha='center', va='center')
        ax.axis('off')
        return fig

    played = qualified.filter(pl.col("Playoff_rank").is_not_null()).sort("Playoff_rank")

    def truncate(name):
        return name if len(name) <= 25 else name[:24] + "…"

    x_left, x_right = 0, 1
    row_spacing = 1.0

    left_y = {row["user_pseudo_id"]: index * row_spacing
              for index, row in enumerate(qualified.iter_rows(named=True))}
    right_y = {row["user_pseudo_id"]: index * row_spacing
               for index, row in enumerate(played.iter_rows(named=True))}

    for row in qualified.iter_rows(named=True):
        solver = row["user_pseudo_id"]
        y = left_y[solver]
        did_not_play = row["Playoff_rank"] is None
        label_color = grey if did_not_play else "black"
        alpha = 0.5 if did_not_play else 1.0
        ax.scatter(x_left, y, color=grey if did_not_play else "black", zorder=3, s=30,
                   alpha=alpha)
        ax.text(x_left - 0.05, y, f"{row['Rank_before_playoffs']}. {truncate(row['Name'])}",
               ha='right', va='center', color=label_color, alpha=alpha, fontsize=9)

    for row in played.iter_rows(named=True):
        solver = row["user_pseudo_id"]
        y = right_y[solver]
        ax.scatter(x_right, y, color="black", zorder=3, s=30)
        ax.text(x_right + 0.05, y, f"{int(row['Playoff_rank'])}. {truncate(row['Name'])}",
               ha='left', va='center', fontsize=9)

        x0, y0 = x_left, left_y[solver]
        x1, y1 = x_right, y
        xmid = (x0 + x1) / 2
        verts = [(x0, y0), (xmid, y0), (xmid, y1), (x1, y1)]
        codes = [matplotlib.path.Path.MOVETO] + [matplotlib.path.Path.CURVE4] * 3
        color = green if row["Playoff_rank"] <= row["Rank_before_playoffs"] else amber
        patch = matplotlib.patches.PathPatch(
            matplotlib.path.Path(verts, codes), facecolor='none', edgecolor=color,
            lw=1.8, alpha=0.85, zorder=1)
        ax.add_patch(patch)

    header_y = -row_spacing
    ax.text(x_left, header_y, "Qualifying rank", ha='right', va='center', fontsize=10,
           fontweight='bold')
    ax.text(x_right, header_y, "Playoff rank", ha='left', va='center', fontsize=10,
           fontweight='bold')

    ax.set_xlim(-0.9, 1.9)
    ax.set_ylim((len(qualified) - 1) * row_spacing + row_spacing / 2, header_y - row_spacing / 2)
    ax.axis('off')
    ax.set_title(f"Sudoku Grand Prix: qualifying vs. playoff rank ({year})", pad=8)

    return fig

def create_wsc_leaderboard_chart(full_df, year=2024, top_n=10,
                                 colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This creates a horizontal bar chart of the top scores for a WSC year."""
    year_df = full_df.filter(pl.col("year") == year)
    year_df = year_df.with_columns(
        pl.col("WSC_total").cast(pl.Float32).alias("WSC_total")
    )

    subset = year_df.sort("WSC_total", descending=True).head(top_n)

    labels = subset.get_column("Name")
    points = subset.get_column("WSC_total")

    fig, ax = plt.subplots(figsize=(6.4, 10))

    bar_colors = [colors[0] for _ in range(len(labels))]
    for index, row in enumerate(subset.iter_rows(named=True)):
        if not row['Official']:
            bar_colors[index] = colors[1]

    ax.barh(labels, points, color=bar_colors)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()

    # Use the legend to show what the colors mean
    official_line = matplotlib.lines.Line2D(
        [], [], linewidth=10, color=colors[0], label='Official')
    unofficial_line = matplotlib.lines.Line2D(
        [], [], linewidth=10, color=colors[1], label='Unofficial')
    ax.legend(handles=[official_line, unofficial_line], loc="lower right", frameon=False)

    ax.set_title(f"World Sudoku Championship point leaders ({year})", pad=50)

    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    return fig

def create_esc_leaderboard_chart(full_df, year=2026, top_n=10,
                                 colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This creates a horizontal bar chart of the top scores for an ESC year."""
    year_df = full_df.filter(pl.col("year") == year)
    year_df = year_df.with_columns(pl.col("ESC_total").cast(pl.Float32).alias("ESC_total"))

    subset = year_df.sort("ESC_total", descending=True).head(top_n)

    labels = subset.get_column("Name")
    points = subset.get_column("ESC_total")

    fig, ax = plt.subplots(figsize=(6.4, 10))

    bar_colors = [
        colors[0] if row["ESC_rank"] is not None else colors[1]
        for row in subset.iter_rows(named=True)
    ]
    ax.barh(labels, points, color=bar_colors)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()

    official_line = matplotlib.lines.Line2D([], [], linewidth=10, color=colors[0], label="Official")
    unofficial_line = matplotlib.lines.Line2D([], [], linewidth=10, color=colors[1], label="Unofficial")
    ax.legend(handles=[official_line, unofficial_line], loc="lower right", frameon=False)

    ax.set_title(f"European Sudoku Championship point leaders ({year})", pad=50)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    return fig


def create_violin_chart(full_df, selected_solvers, year_subset=(2024,),
                        competition="GP",
                        colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This shows point distributions and select solver positions by round."""
    flattened = shared.data.create_flat_dataset(
        full_df, metric="points", competition=competition)

    names = shared.utils.ids_to_names(flattened, selected_solvers)

    rounds = []
    year_starts = []
    for year in year_subset:
        year_starts.append(f"{year}_1")
        num_rounds = shared.competitions.get_max_round(year, competition=competition)
        if num_rounds is None:
            raise ValueError(f"Year \"{year}\" not found: update `get_max_round`")
        for competition_round in range(1, num_rounds + 1):
            column = f"{year}_{competition_round}"
            if column in flattened:
                rounds.append(column)

    fig, ax = plt.subplots(nrows=1, ncols=len(rounds), sharey=True)

    # Handle the special case after the first round of a year, where subplots will
    # return a single axis instead of an array of them.
    if len(rounds) == 1:
        ax = [ax]

    for idx, column in enumerate(rounds):
        data = flattened.select(pl.col(column).cast(pl.Float32).drop_nulls())

        if len(data) == 0:
            continue

        ax[idx].violinplot(data, showmeans=True, showmedians=True)
        ax[idx].spines['top'].set_visible(False)
        ax[idx].spines['right'].set_visible(False)
        if idx != 0:
            ax[idx].spines['left'].set_visible(False)
            ax[idx].tick_params(axis='y', labelleft=False, length=0)
        ax[idx].set_xticks([1], [column], rotation=-45)

        color_cycle = itertools.cycle(plt.cycler('color', colors).by_key()['color'])
        for solver in selected_solvers:
            solver_row = flattened.filter(pl.col("user_pseudo_id") == solver)
            if solver_row.height < 1:
                raise ValueError(
                    f"Expected 1 row for solver \"{solver}\", found {solver_row.height}")
            score = solver_row.get_column(column).cast(pl.Float64).fill_null(0).item()
            if idx == 0:
                label = names[solver]
            else:
                label=None
            ax[idx].plot(1, score, color=next(color_cycle), marker='o', markersize=10,
                         markerfacecolor='white', label=label)

    if competition == "GP":
        title_competition = "Sudoku Grand Prix"
    elif competition == "WSC":
        title_competition = "World Sudoku Championship"
    else:
        # Will let the "else" case fall through to an empty string, albeit awkwardly.
        title_competition = ""

    fig.suptitle(f"{title_competition} points by round ({year})")
    fig.legend(frameon=False, bbox_to_anchor=(1.2, 0.9), loc="upper right")

    return fig

def create_point_trend_chart(full_df, selected_solvers, year=2024, competition="GP",
                             colors=[matplotlib.cm.Set2(i) for i in range(8)]):
    """This creates a step chart with cumulative points for solvers."""
    year_df = full_df.filter(pl.col("year") == year)
    subset = year_df.filter(pl.col("user_pseudo_id").is_in(selected_solvers))
    num_rounds = shared.competitions.get_max_round(year, competition=competition)
    if num_rounds is None:
        raise ValueError(f"Year \"{year}\" not found: update `get_max_round`")

    wsc_rounds = shared.competitions.wsc_rounds_by_year()

    labels = subset.get_column("Name")
    cumulative = [[] for _ in labels]
    round_columns = []
    round_labels = []

    counter = 0
    for competition_round in range(1, num_rounds + 1):
        # WSC skips over some rounds in their numbering
        if competition == "WSC" and competition_round not in wsc_rounds[year]:
            continue
        # Maintaining a round counter instead of relying on the round number,
        # because of non-existent round numbers in many WSC years.
        counter += 1
        round_labels.append(f"{year}_{competition_round}")
        round_columns.append(f"{competition}_t{competition_round} points")
        if competition == "GP":
            round_limit = 6
        else:
            round_limit = counter
        top_k_sums = shared.utils.sum_top_k_of_n_rounds(
            subset, counter, round_limit, round_columns, competition)
        for index, row in enumerate(top_k_sums.iter_rows()):
            cumulative[index].append(row[0])

    fig, ax = plt.subplots()
    for index, items in enumerate(labels):
        ax.step(round_labels, cumulative[index], where='post', label=items, color=colors[index])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax. set_ylim(bottom=0)
    #ax.set_xticklabels(ax.get_xticklabels(), rotation=-45)
    for tick in ax.get_xticklabels():
        tick.set_rotation(-45)
    ax.legend(frameon=False)

    if competition == "GP":
        ax.set_title(f"Accumulated points (top 6) in the Sudoku Grand Prix ({year})")
    elif competition == "WSC":
        ax.set_title(f"Accumulated points in the World Sudoku Championship ({year})")
    elif competition == "ESC":
        ax.set_title(f"Accumulated points in the European Sudoku Championship ({year})")

    return fig
