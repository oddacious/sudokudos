import re
import pandas as pd
import polars as pl

import shared.constants
import shared.utils

def create_flat_dataset(full_df, metric="points", competition="GP"):
    """Flatten a solver-year dataframe to a solver dataframe.
    
    Results by year will be represented in their own columns, so this does blow
    up the column size since not all solvers competed in all competitions.
    """
    if competition == "GP":
        kept_columns = ["#", "Name", "Country", "Nick", "year"]
        columns_to_drop = ["#", "year"]
    elif competition == "WSC":
        kept_columns = ["year", "Name", "Official", "Official_rank", "Unofficial_rank", "WSC_total"]
        columns_to_drop = ["year"]
    else:
        raise ValueError(f"Observed unexpected competition \"{competition}\"")

    for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"{competition}_t{competition_round} {metric}"
        if colname in full_df.columns:
            kept_columns.append(colname)

    subset = full_df[kept_columns].reset_index()

    flattened = None

    years = sorted(full_df["year"].unique())

    for year in years:
        single_year = subset[subset["year"] == year].copy()
        max_round_in_year = shared.utils.get_max_round(year, competition)

        rename = {}

        # Years that don't exist shouldn't be included for anyone
        if max_round_in_year is None:
            continue

        # Need to do this for the largest rounds available, because the columns
        # will exist for each and otherwise we'll have column name problems in
        # the join
        for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
            colname = f"{competition}_t{competition_round} {metric}"
            if colname in single_year:
                # Some rounds don't exist in all years, but they still have columns because
                # all years are represented in one large table that contains a column for
                # every possible round.
                if sum(single_year[colname].isna()) == len(single_year):
                    single_year.drop(columns=[colname], inplace=True)
                else:
                    rename[colname] = f"{year}_{competition_round}"

        single_year.rename(columns=rename, inplace=True)

        if flattened is None:
            flattened = single_year.copy()
        else:
            single_year.drop(columns=columns_to_drop, inplace=True)
            flattened = pd.merge(flattened, single_year, on="user_pseudo_id",
                                how="outer", suffixes=("_left", "_right"))

            for column in ("Name", "Nick", "Country", "Official", "Official_rank",
                           "Unofficial_rank", "WSC_total"):
                left_col = f"{column}_left"
                right_col = f"{column}_right"
                if left_col in flattened.columns:
                    flattened[column] = flattened[left_col].combine_first(flattened[right_col])
                    flattened.drop(columns=[left_col, right_col], inplace=True)

    flattened.drop(columns=columns_to_drop, inplace=True)
    flattened.set_index("user_pseudo_id", inplace=True)

    return flattened

def create_flat_dataset_polars(full_df, metric="points", competition="GP"):
    """Flatten a solver-year dataframe to a solver dataframe.
    
    Results by year will be represented in their own columns, so this does blow
    up the column size since not all solvers competed in all competitions.
    """
    if competition == "GP":
        kept_columns = ["user_pseudo_id", "#", "Name", "Country", "Nick", "year"]
        columns_to_drop = ["#", "year"]
    elif competition == "WSC":
        kept_columns = ["user_pseudo_id", "year", "Name", "Official", "Official_rank", "Unofficial_rank", "WSC_total"]
        columns_to_drop = ["year"]
    else:
        raise ValueError(f"Observed unexpected competition \"{competition}\"")

    for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"{competition}_t{competition_round} {metric}"
        if colname in full_df.columns:
            kept_columns.append(colname)

    #subset = full_df[kept_columns].reset_index()
    subset = full_df.select(kept_columns)

    flattened = None

    #years = sorted(full_df.get_column("year").unique().to_list())
    years = full_df.filter(pl.col("year").is_not_null()).get_column("year").unique()

    for year in years:
        #single_year = subset[subset["year"] == year].copy()
        single_year = subset.filter(pl.col("year") == year)
        max_round_in_year = shared.utils.get_max_round(year, competition)

        rename = {}

        # Years that don't exist shouldn't be included for anyone
        if max_round_in_year is None:
            continue

        # Need to do this for the largest rounds available, because the columns
        # will exist for each and otherwise we'll have column name problems in
        # the join
        for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
            colname = f"{competition}_t{competition_round} {metric}"
            if colname in single_year:
                # Some rounds don't exist in all years, but they still have columns because
                # all years are represented in one large table that contains a column for
                # every possible round.
                #if sum(single_year[colname].isna()) == len(single_year):
                if sum(single_year.get_column(colname).is_null()) == len(single_year):
                    #single_year.drop(columns=[colname], inplace=True)
                    single_year = single_year.drop(colname)
                else:
                    rename[colname] = f"{year}_{competition_round}"

        #single_year.rename(columns=rename, inplace=True)
        single_year = single_year.rename(rename)

        if flattened is None:
            flattened = single_year
        else:
            #single_year.drop(columns=columns_to_drop, inplace=True)
            single_year = single_year.drop(columns_to_drop)
            #flattened = pd.merge(flattened, single_year, on="user_pseudo_id",
            #                    how="outer", suffixes=("_left", "_right"))
            flattened = flattened.join(single_year, on="user_pseudo_id",
                                how="outer", suffix=("_right"))

            for column in ("Name", "Nick", "Country", "Official", "Official_rank",
                           "Unofficial_rank", "WSC_total", "user_pseudo_id"):
                #left_col = f"{column}_left"
                right_col = f"{column}_right"
                if right_col in flattened.columns:
                    #flattened[column] = flattened[left_col].combine_first(flattened[right_col])
                    flattened = flattened.with_columns(
                        pl.col(column).fill_null(pl.col(right_col)).alias(column)
                    )
                    #flattened.drop(columns=[left_col, right_col], inplace=True)
                    flattened = flattened.drop(right_col)

    #flattened.drop(columns=columns_to_drop, inplace=True)
    flattened = flattened.drop(columns_to_drop)
    #flattened.set_index("user_pseudo_id", inplace=True)

    return flattened

def merge_unflat_datasets(gp_dataset, wsc_dataset):
    """Combine solver-year level datasets from the GP and WSC."""
    kept_columns = ["WSC_entry", "year", "Official", "Official_rank",
                    "Unofficial_rank", "WSC_total", "Name"]
    for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        round_name = f"WSC_t{competition_round} points"
        if round_name in wsc_dataset.columns:
            # Also calculate the round position at this time
            position_name = f"WSC_t{competition_round} position"
            wsc_dataset[round_name] = pd.to_numeric(
                wsc_dataset[round_name], errors="coerce").fillna(0)
            wsc_dataset[position_name] = wsc_dataset.groupby("year")[round_name].rank(
                ascending=False, method="min")

            kept_columns.append(round_name)
            kept_columns.append(position_name)

    minimal = wsc_dataset[kept_columns]

    # Either the GP or WSC migth be missing, so take name from either.
    # Preferring GP, because it is naturally more consistent (except when
    # people change it) and we have overrides to make it consistent in such
    # cases anyways.
    merged = pd.merge(gp_dataset, minimal, on=["user_pseudo_id", "year"], how="outer")
    merged["Name"] = merged["Name_x"].combine_first(merged["Name_y"])
    merged.drop(columns=["Name_x", "Name_y"], inplace=True)

    return merged

def merge_unflat_datasets_polars(gp_dataset, wsc_dataset):
    """Combine solver-year level datasets from the GP and WSC."""
    kept_columns = ["WSC_entry", "year", "Official", "Official_rank",
                    "Unofficial_rank", "WSC_total", "Name", "user_pseudo_id"]
    for competition_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        round_name = f"WSC_t{competition_round} points"
        if round_name in wsc_dataset.columns:
            # Also calculate the round position at this time
            position_name = f"WSC_t{competition_round} position"
            #wsc_dataset[round_name] = pd.to_numeric(
            #    wsc_dataset[round_name], errors="coerce").fillna(0)
            wsc_dataset = wsc_dataset.with_columns(
                        pl.col(round_name).cast(pl.Float32).fill_null(0).alias(round_name)
                    )
            # wsc_dataset[position_name] = wsc_dataset.groupby("year")[round_name].rank(
            #     ascending=False, method="min")
            # wsc_dataset = wsc_dataset.with_columns(
            #     pl.col(pl.struct("round_name", "year"))
            #     .rank(descending=True, method="min")
            #     .over("year")
            #     .alias(position_name)
            # )
            #print(wsc_dataset.columns)
            #print(round_name)
            #print(round_name in wsc_dataset.columns)
            wsc_dataset = wsc_dataset.with_columns(
                pl.col(round_name)
                .rank(descending=True, method="min")
                .over("year")
                .alias(position_name)
            )

            kept_columns.append(round_name)
            kept_columns.append(position_name)

    #minimal = wsc_dataset[kept_columns]
    minimal = wsc_dataset.select(kept_columns)

    # Either the GP or WSC migth be missing, so take name from either.
    # Preferring GP, because it is naturally more consistent (except when
    # people change it) and we have overrides to make it consistent in such
    # cases anyways.
    #merged = pd.merge(gp_dataset, minimal, on=["user_pseudo_id", "year"], how="outer")
    merged = gp_dataset.join(minimal, how="full", on=["user_pseudo_id", "year"])
    merged = merged.with_columns(
        pl.coalesce([pl.col("user_pseudo_id"), pl.col("user_pseudo_id_right")]).alias("user_pseudo_id")
    )
    #merged["Name"] = merged["Name_x"].combine_first(merged["Name_y"])
    merged = merged.with_columns(
        pl.coalesce([pl.col("Name"), pl.col("Name_right")]).alias("Name"),
        pl.coalesce([pl.col("user_pseudo_id"), pl.col("user_pseudo_id_right")]).alias("user_pseudo_id"),
        pl.coalesce([pl.col("year"), pl.col("year_right")]).alias("year")
    )

    #merged.drop(columns=["Name_x", "Name_y"], inplace=True)
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
        #dataset.rename(columns=rename, inplace=True)
        datasets[index] = datasets[index].rename(rename)

    #merged = pd.merge(datasets[0], datasets[1], on="user_pseudo_id", how="outer")
    merged = datasets[0].join(datasets[1], on="user_pseudo_id", how="outer")
    #merged.rename(columns={"Name_x": "Name"}, inplace=True)
    #merged.drop(columns=["Name_y"], inplace=True)
    merged = merged.drop("Name_right")
    #merged.set_index("user_pseudo_id", inplace=True)

    return merged

def attemped_mapping(wsc_df, gp_df):
    """Update a WSC dataset with identifiers from a GP dataset."""
    wsc_mapped = wsc_df.copy()
    gp_df2 = gp_df.copy().reset_index()
    gp_index = gp_df2[["Name", "Country", "Nick", "user_pseudo_id"]].drop_duplicates()
    gp_index["name_lc"] = gp_index["Name"].str.lower()

    wsc_mapped["Name"] = wsc_mapped["Name"].str.replace(",", "")
    wsc_mapped["Name"] = wsc_mapped["Name"].str.title()
    wsc_mapped["name_lc"] = wsc_mapped["Name"].str.lower()

    parts = wsc_mapped["Name"].str.split()
    wsc_mapped["flipped_name"] = parts.apply(
        lambda x: " ".join(reversed(x)) if isinstance(x, list) else "")

    joined = pd.merge(wsc_mapped, gp_index, on="Name", how="left")
    joined_flipped = pd.merge(joined, gp_index, left_on="flipped_name", right_on="Name", how="left")
    wsc_and_gp = pd.merge(joined_flipped, gp_index, on="name_lc", how="left")

    # Otherwise the "Name" column comes from `gp_index` in the last join
    wsc_and_gp.drop(columns=["Name"], inplace=True)
    wsc_and_gp.rename(columns={"Name_x": "Name"}, inplace=True)

    # Use our attempted identifiers in a hierarchy by name, then flipped name, then lowercase name
    wsc_and_gp["matched_id"] = wsc_and_gp["user_pseudo_id_x"].combine_first(
        wsc_and_gp["user_pseudo_id_y"]).combine_first(wsc_and_gp["user_pseudo_id"])

    manual_map = shared.constants.WSC_NAME_TO_GP_ID_OVERRIDE
    wsc_and_gp["matched_id"] = wsc_and_gp.apply(
        lambda row: (manual_map[row['flipped_name']] if row['flipped_name'] in manual_map
                     else row['matched_id']), axis=1)
    wsc_and_gp["matched_id"] = wsc_and_gp.apply(
        lambda row: (manual_map[row['Name']] if row['Name'] in manual_map
                     else row['matched_id']), axis=1)

    wsc_and_gp["user_pseudo_id"] = wsc_and_gp["matched_id"]

    # TODO: Add in country
    wsc_and_gp["user_pseudo_id"] = wsc_and_gp["user_pseudo_id"].fillna(wsc_and_gp["Name"])
    wsc_and_gp.set_index("user_pseudo_id", inplace=True)

    return wsc_and_gp

def ids_by_total_points(combined):
    """Return identifiers ordered by total points across all competitions."""
    #df = combined.copy()
    df = combined.filter(pl.col("user_pseudo_id").is_not_null())
    #df["total points"] = (pd.to_numeric(df["Points"]).fillna(0) +
    #                      pd.to_numeric(df["WSC_total"]).fillna(0))
    df = df.with_columns(
        (pl.col("Points").cast(pl.Float32).fill_null(0) +
        pl.col("WSC_total").cast(pl.Float32).fill_null(0)).alias("total points"),
    )

    #aggregate = df.groupby("user_pseudo_id")["total points"].sum()
    aggregate = (
        df.group_by("user_pseudo_id")
        .agg(pl.col("total points").sum().alias("total points"))
    )

    #return aggregate.sort_values(ascending=False).index.to_list()
    return (aggregate.sort("total points", descending=True)
        .get_column("user_pseudo_id")
        .to_list()
    )

def wsc_rounds_by_year():
    """Return the list of rounds (as integers) for each WSC year.

    Note that the WSC often has a gap in between rounds, with a first set of rounds from 1 to N and
    then another set from 10 or 11 onwards.
    """
    return {
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
