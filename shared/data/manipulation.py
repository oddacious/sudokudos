"""Contains functions for manipulating and combining competition data."""

import re

import polars as pl

import shared.competitions

def create_flat_dataset(full_df, metric="points", competition="GP"):
    """Flatten a solver-year dataframe to a solver dataframe.
    
    Results by year will be represented in their own columns, so this does blow
    up the column size since not all solvers competed in all competitions.
    """
    if competition == "GP":
        kept_columns = ["user_pseudo_id", "#", "Name", "Country", "Nick", "year"]
        columns_to_drop = ["#", "year"]
    elif competition == "WSC":
        kept_columns = ["user_pseudo_id", "year", "Name", "Official", "Official_rank",
                        "Unofficial_rank", "WSC_total"]
        columns_to_drop = ["year"]
    else:
        raise ValueError(f"Observed unexpected competition \"{competition}\"")

    max_round_plus_one = shared.competitions.MAXIMUM_ROUND + 1

    for competition_round in range(1, max_round_plus_one):
        colname = f"{competition}_t{competition_round} {metric}"
        if colname in full_df.columns:
            kept_columns.append(colname)

    subset = full_df.select(kept_columns)

    flattened = None

    years = full_df.filter(pl.col("year").is_not_null()).get_column("year").unique()

    for year in years:
        single_year = subset.filter(pl.col("year") == year)
        max_round_in_year = shared.competitions.get_max_round(year, competition)

        rename = {}

        # Years that don't exist shouldn't be included for anyone
        if max_round_in_year is None:
            continue

        # Need to do this for the largest rounds available, because the columns
        # will exist for each and otherwise we'll have column name problems in
        # the join
        for competition_round in range(1, max_round_plus_one):
            colname = f"{competition}_t{competition_round} {metric}"
            if colname in single_year:
                # Some rounds don't exist in all years, but they still have columns because
                # all years are represented in one large table that contains a column for
                # every possible round.
                if sum(single_year.get_column(colname).is_null()) == len(single_year):
                    single_year = single_year.drop(colname)
                else:
                    rename[colname] = f"{year}_{competition_round}"

        single_year = single_year.rename(rename)

        if flattened is None:
            flattened = single_year
        else:
            single_year = single_year.drop(columns_to_drop)
            flattened = flattened.join(single_year, on="user_pseudo_id",
                                how="outer", suffix="_right")

            for column in ("Name", "Nick", "Country", "Official", "Official_rank",
                           "Unofficial_rank", "WSC_total", "user_pseudo_id"):
                right_col = f"{column}_right"
                if right_col in flattened.columns:
                    flattened = flattened.with_columns(
                        pl.col(column).fill_null(pl.col(right_col)).alias(column)
                    ).drop(right_col)

    flattened = flattened.drop(columns_to_drop)

    return flattened

def merge_unflat_datasets(gp_dataset, wsc_dataset):
    """Combine solver-year level datasets from the GP and WSC."""
    kept_columns = ["WSC_entry", "year", "Official", "Official_rank",
                    "Unofficial_rank", "WSC_total", "Name", "user_pseudo_id"]
    for competition_round in range(1, shared.competitions.MAXIMUM_ROUND + 1):
        round_name = f"WSC_t{competition_round} points"
        if round_name in wsc_dataset.columns:
            # Also calculate the round position at this time
            position_name = f"WSC_t{competition_round} position"
            wsc_dataset = wsc_dataset.with_columns(
                pl.col(round_name).cast(pl.Float64).alias(round_name)
            )
            wsc_dataset = wsc_dataset.with_columns(
                pl.col(round_name)
                .rank(descending=True, method="min")
                .over("year")
                .alias(position_name)
            )

            kept_columns.append(round_name)
            kept_columns.append(position_name)

    minimal = wsc_dataset.select(kept_columns)

    # Either the GP or WSC migth be missing, so take name from either.
    # Preferring GP, because it is naturally more consistent (except when
    # people change it) and we have overrides to make it consistent in such
    # cases anyways.
    merged = gp_dataset.join(minimal, how="full", on=["user_pseudo_id", "year"])

    merged = merged.with_columns(
        pl.coalesce([pl.col("Name"), pl.col("Name_right")]).alias("Name"),
        pl.coalesce([pl.col("user_pseudo_id"), pl.col("user_pseudo_id_right")])
            .alias("user_pseudo_id"),
        pl.coalesce([pl.col("year"), pl.col("year_right")]).alias("year")
    )

    merged = merged.drop(["Name_right", "user_pseudo_id_right", "year_right"])

    return merged

def merge_flat_datasets(datasets, suffixes=("_gp", "_wsc")):
    """Combine solver level datasets from the GP and WSC."""
    if len(datasets) != len(suffixes):
        raise ValueError("Number of datasets should match number of suffixes")

    # We use year_round as column names in each dataset, which now need
    # suffixes to be distinguished.
    for index, dataset in enumerate(datasets):
        rename = {}
        for column in dataset.columns:
            if re.fullmatch(r"\d{4}_\d+", column):
                rename[column] = column + suffixes[index]
        datasets[index] = datasets[index].rename(rename)

    merged = datasets[0].join(datasets[1], on="user_pseudo_id", how="outer").drop("Name_right")

    return merged

def attempted_mapping(wsc_df, gp_df):
    """Update a WSC dataset with identifiers from a GP dataset."""
    gp_index = gp_df.select(["Name", "Country", "Nick", "user_pseudo_id"]).unique()
    gp_index = gp_index.with_columns(pl.col("Name").str.to_lowercase().alias("name_lc"))

    wsc_mapped = wsc_df.with_columns(
        pl.col("Name").str.to_titlecase().str.replace(",", "").alias("Name"),
        pl.col("Name").str.to_lowercase().str.replace(",", "").alias("name_lc")
    )

    wsc_mapped = wsc_mapped.with_columns(
        pl.col("Name")
        .str.replace_all(",", "")
        .str.split(" ")
        .list.reverse()
        .list.join(" ")
        .alias("flipped_name")
    )

    joined = wsc_mapped.join(gp_index, on="Name", how="left").drop("name_lc_right")

    joined_flipped = (
        joined
            .join(gp_index, left_on="flipped_name", right_on="Name", how="left")
            .drop(["Country_right", "Nick_right"])
            .rename({"user_pseudo_id_right": "user_pseudo_id_flipped_name"})
    )

    wsc_and_gp = (
        joined_flipped
            .join(gp_index, on="name_lc", how="left")
            .rename(({"user_pseudo_id_right": "user_pseudo_id_name_lc"}))
    )

    # Use our attempted identifiers in a hierarchy by name, then flipped name, then lowercase name
    wsc_and_gp = wsc_and_gp.with_columns(
        pl.col("user_pseudo_id")
        .fill_null(pl.col("user_pseudo_id_flipped_name"))
        .fill_null(pl.col("user_pseudo_id_name_lc"))
        .alias("matched_id")
    )

    manual_map = shared.competitions.WSC_NAME_TO_GP_ID_OVERRIDE

    expr = None
    for key, value in manual_map.items():
        if expr is None:
            expr = pl.when(pl.col("Name") == key).then(pl.lit(value))
        else:
            expr = expr.when(pl.col("Name") == key).then(pl.lit(value))
        expr = expr.when(pl.col("flipped_name") == key).then(pl.lit(value))
    expr = expr.otherwise(pl.col("matched_id")).alias("matched_id")
    wsc_and_gp = (
        wsc_and_gp
            .with_columns(expr)
            .drop("user_pseudo_id")
            .rename({"matched_id": "user_pseudo_id"})
    )

    # TODO: Add in country
    wsc_and_gp = wsc_and_gp.with_columns(
        pl.col("user_pseudo_id").fill_null(pl.col("Name"))
    )

    return wsc_and_gp

def ids_by_total_points(combined):
    """Return identifiers ordered by total points across all competitions."""
    df = combined.filter(pl.col("user_pseudo_id").is_not_null())

    df = df.with_columns(
        (pl.col("Points").cast(pl.Float32).fill_null(0) +
        pl.col("WSC_total").cast(pl.Float32).fill_null(0)).alias("total points"),
    )

    aggregate = (
        df.group_by("user_pseudo_id")
        .agg(pl.col("total points").sum().alias("total points"))
    )

    return (aggregate.sort("total points", descending=True)
        .get_column("user_pseudo_id")
        .to_list()
    )
