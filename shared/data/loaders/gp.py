"""Provides a function to load GP data from CSV files."""

import os
import polars as pl

import streamlit as st

import shared.competitions

def manual_adjustements(df):
    """Update names, nicks, and countries in GP files.
    
    Those three fields are used together to create an identifier, due to the
    lack of an actual unique identifier. As such, they need to be the same for
    every row (year) for each person. Unfortunately, all three fields can
    change over time. Name and country are editable at any time (and prior year
    pages will not update accordingly), nick can be shown or hidden at any time,
    and it looks like some people have either changed their nicks or created
    new accounts.
    """
    name_to_name = {
        "TanTan Dai": "Tantan Dai",
        "Dai Tantan": "Tantan Dai",
        "Seongwon Jin": "Sung-Won Jin",
        "Timothy DOYLE": "Timothy Doyle",
    }

    nick_to_nick = {
        "Qyz_": "qyz",
        "The Scrasse": "TheScrasse",
        "x18349276": "TheScrasse",
        "ChessCombinatorics": "BeautyOfConfigurations",
        "CosmicCombination": "BeautyOfConfigurations",
        "CosmicQuietude": "BeautyOfConfigurations",
        "TheHolyGame": "BeautyOfConfigurations",
        "TheWhisperingBullet": "BeautyOfConfigurations",
        "TheXTrain": "BeautyOfConfigurations",
    }

    name_to_nick = {
        "Darina Maratova": "DarinaM",
        "Bobo Lo": "Seyeonnie",
        "Izabella Tilkin": "creta",
        "Ytep Flores": "AlexCross",
        "Zalak Ghetia": "puzzlegirl",
        "Bruno Rivara": "Bruno61",
        "H. L. Vu": "gimmick",
        "Karthika Balusamy": "Light",
        "Minfang Lin": "leafcard",
        "Paul Hlebowitsh": "FLEB",
        "Ryotaro Chiba": "EctoPlasma",
        "Félix Meyer": "NewStar",
        "Cheryl Gaul": "cgaul",
        "Howard Wilkinson": "HWHW",
        "Riley Guerin": "Bluey",
        "Sirawit Pulketkij": "Potter",
        "Sultan GÜLTAŞ": "Sultan09",
        "Taavi Piller": "Taavi",
        "Virgi Puusepp": "Virgip",
        "Wesley Barton": "sparrowhawk73",
        "Sitanshu Sah": "sitaswag",
        "Valeria Losasso": "Bely",
        "daniele cassani": "dany_thor",
        "akash doulani": "akashdoulani78",
        "Esmeralda Kleinreesink": "Esmeralda Kleinreesink",
        "James Anderson": "Holboo",
        "Mohammad Amini Rad": "Kobresia",
        "Sohaima Jabeen": "sohaima",
        "Avinash Kumar": "ak_iit",
        "Janelle Aleisonne Navarro": "Alison",
        "Jimin HWANG": "GGFJH",
        "Sebastian Matschke": "Semax",
        "Sérgio Schwarz de Assis Farias": "Schwarz",
        "Zhen Fan": "FierceHAuCl4",
        "betty bei": "beibeiball",
        "Ömer DURMAZ": "mrdrmz",
        "Katerina Sabevska": "k_2005",
        "Pat Stanford": "Kaysman",
        "Pitchpreeya Jullathochai": "MaiPrae",
        "Sae Joon Jang": "jonahjang",
        "michael stitzel": "mikeylyk",
        "Alan Filipin": "alanfilipin",
        "Deepankar Sharma": "Deep",
        "Jeannette Fries": "swissjane",
        "Kentaro Shibata": "esqn",
        "MinHyeok Choi": "applejackcmh",
        "Sravani Sripada": "scampy",
        "Supachai Thongsawang": "AgentK",
        "Bhuvaneshwari S": "Bhuvi",
        "Bret Kugler": "SOTC",
        "Rohan Rao": "Rohan Rao",
    }

    name_to_country = {
        "Jimin HWANG": "Korea, South",
        "James Anderson": "American Samoa",
        "Howard Wilkinson": "UK",
        "Jay Mark": "USA",
        "Wesley Barton": "Canada",
        "Josh Bao": "Singapore",
        "Sérgio Schwarz de Assis Farias": "Brazil",
        "Zhen Fan": "China",
        "betty bei": "China",
        "Kevin Lee": "Hong Kong",
        "Timothy O'Shea": "USA",
        "Bruno Rivara": "Switzerland",
        "H. L. Vu": "Vietnam",
        "Karthika Balusamy": "Ireland",
        "P S": "Israel",
        "Diana Huang": "USA",
        "Zalak Ghetia": "USA",
        "Sravani Sripada": "Canada",
        "CJ Tan": "Philippines",
    }

    expr_nick = None
    for key, value in name_to_nick.items():
        if expr_nick is None:
            expr_nick = pl.when(pl.col("Name") == key).then(pl.lit(value))
        else:
            expr_nick = expr_nick.when(pl.col("Name") == key).then(pl.lit(value))
    expr_nick = expr_nick.otherwise(pl.col("Nick")).alias("Nick")

    expr_country = None
    for key, value in name_to_country.items():
        if expr_country is None:
            expr_country = pl.when(pl.col("Name") == key).then(pl.lit(value))
        else:
            expr_country = expr_country.when(pl.col("Name") == key).then(pl.lit(value))
    expr_country = expr_country.otherwise(pl.col("Country")).alias("Country")

    df = df.with_columns(
        pl.col("Name").replace(name_to_name).alias("Name"),
        pl.col("Nick").replace(nick_to_nick).alias("Nick")
    )
    df = df.with_columns(expr_nick, expr_country)

    return df

def apply_types(gp):
    """Change the types for many columns."""
    column_types = {
        # Integer columns
        'GP_t1 position': pl.Float64,
        'GP_t2 position': pl.Float64,
        'GP_t3 position': pl.Float64,
        'GP_t4 position': pl.Float64,
        'GP_t5 position': pl.Float64,
        'GP_t6 position': pl.Float64,
        'GP_t7 position': pl.Float64,
        'GP_t8 position': pl.Float64,
        'Played GPs': pl.Int32,
        'Total GPs': pl.Int32,
        'Rank_before_playoffs': pl.Int32,
        'Playoff_rank': pl.Float64,
        'Rank': pl.Int32,

        # Float columns
        'GP_t1 points': pl.Float64,
        'GP_t1 rank. points': pl.Float64,
        'GP_t2 points': pl.Float64,
        'GP_t2 rank. points': pl.Float64,
        'GP_t3 points': pl.Float64,
        'GP_t3 rank. points': pl.Float64,
        'GP_t4 points': pl.Float64,
        'GP_t4 rank. points': pl.Float64,
        'GP_t5 points': pl.Float64,
        'GP_t5 rank. points': pl.Float64,
        'GP_t6 points': pl.Float64,
        'GP_t6 rank. points': pl.Float64,
        'GP_t7 points': pl.Float64,
        'GP_t7 rank. points': pl.Float64,
        'GP_t8 points': pl.Float64,
        'GP_t8 rank. points': pl.Float64,
        'Points': pl.Float64,

        # Other types (default as-is or left unspecified)
        '#': pl.String,  # Identifier, keep as object
        'Name': pl.String,
        'Country': pl.String,
        'Nick': pl.String,
        'year': pl.Int32,  # If `year` is numeric
        'source_file': pl.String
    }

    for key, value in column_types.items():
        gp = gp.with_columns(
            pl.col(key).cast(value).alias(key)
        )

    return gp

def remove_false_headers(df):
    """Filter out header rows, which may be interlaced throughout a file."""
    condition = ~((df["Name"] == "Name") &
                (df["Country"] == "Country") &
                (df["Nick"] == "Nick"))

    return df.filter(condition)

def merge_dfs_by_year(all_dataframes):
    """Construct an array of per-year dataframes.

    Inputs may have multiple rounds per year, typically in the case of in-progress years.
    """
    # One dataframe per year, ordered by year.
    dataframes = []

    # "year" isn't needed for joining, but it should be unique here and we need it in
    # the resulting dataframe.
    join_cols = ["Name", "Country", "Nick", "year"]
    for mapping in all_dataframes.values():
        if len(mapping) == 1:
            value = next(iter(mapping.values()))
            dataframes.append(value)
        else:
            # Sort by year
            dfs = [value for _, value in sorted(mapping.items())]
            merged_df = dfs[0]
            merged_df = remove_false_headers(merged_df)
            for df in dfs[1:]:
                df = remove_false_headers(df)
                relevant_columns = [
                    col for col in df.columns if col not in merged_df.columns or col in join_cols]
                merged_df = merged_df.join(
                    df.select(relevant_columns), on=join_cols, how="outer", join_nulls=True)
                # The merge creates columns with the suffix "_right".
                merged_df = merged_df.with_columns(
                    [pl.coalesce([col, f"{col}_right"]).alias(col) for col in join_cols]
                ).drop([f"{col}_right" for col in join_cols])

            merged_df = merged_df.drop(["source_file", "round"])

            # Need to calculate point totals. Here using the "rank. " columns to not overcount.
            points_cols = [col for col in merged_df.columns if "rank. points" in col]

            point_inputs = [pl.col(col).cast(pl.Float64).fill_null(0) for col in points_cols]
            merged_df = merged_df.with_columns(
                # Casting back to string because the single-year dataframes will have strings.
                pl.sum_horizontal(point_inputs).cast(pl.String).alias("Points")
            )

            dataframes.append(merged_df)

    return dataframes

def collect_dataframes(csv_directory, verbose=False):
    """From a directory with CSVs, gather all the input dataframes.

    The directory may have single aggregate CSVs per year, but may also have disaggregated
    round-by-round CSVs.
    """
    # Dict of columns to their types
    all_columns = {}

    all_dataframes = {}

    for filename in os.listdir(csv_directory):
        if not filename.endswith(".csv"):
            continue

        if verbose:
            print(f"Parsing file {filename}")
        file_path = os.path.join(csv_directory, filename)

        df = pl.read_csv(file_path)
        df = df.with_columns(
            pl.lit(filename).alias("source_file")
        )

        if "year" not in df.columns:
            raise ValueError(f"We rely on a year column, which is missing in file \"{filename}\"")

        unique_year = df["year"].n_unique() == 1
        if not unique_year:
            raise ValueError(f"Each source should have a single year. \"{filename}\" did not")

        year = df["year"].first()

        # Inconsequential placeholder value for years that only have one file and no "round" column.
        round_marker = "[All]"

        if "round" in df.columns:
            unique_round = df["round"].n_unique() == 1
            if not unique_round:
                raise ValueError(
                    f"With `round` column present, it should be unique. \"{filename}\" fails")
            round_marker = df["round"].first()

        if year not in all_dataframes:
            all_dataframes[year] = {round_marker: df}
        else:
            if round_marker in all_dataframes[year]:
                raise ValueError(f"Found duplicate round \"{round}\" from \"{filename}\"")
            all_dataframes[year][round_marker] = df

        # Column types will be necessary for appending these dataframes together consistently.
        for column, data_type in df.schema.items():
            if column not in all_columns:
                all_columns[column] = data_type
            else:
                if all_columns[column] != data_type:
                    print(f"Warning: For column {column}, had type {all_columns[column]}" +
                            f"but now have {data_type}")

    return all_dataframes, all_columns

@st.cache_data
def load_gp(csv_directory="data/processed/gp", verbose=False, output_csv=None):
    """Import GP CSV files and return a single dataset.
    
    This creates a dataset covering all years with one row per solver-year combination,
    under the assumption of one file per year. This also creates an identifier out of
    the Name, Country, and Nick fields.
    """
    # Dict of columns to their types
    all_columns = {}

    all_dataframes, all_columns = collect_dataframes(csv_directory, verbose)

    # An in-progress year may be represented by round-specific data files
    dataframes = merge_dfs_by_year(all_dataframes)

    aligned_dfs = []
    for df in dataframes:
        for column, data_type in all_columns.items():
            if column not in df.columns:
                # Casting is necessary because concat will fail if the types differ, even
                # for null values.
                df = df.with_columns([pl.lit(None).cast(data_type).alias(column)])
        aligned_dfs.append(df.select(sorted(all_columns)))
    combined_df = pl.concat(aligned_dfs, how="vertical")

    combined_df = manual_adjustements(combined_df)

    # Save the combined DataFrame to a new CSV (optional)
    if output_csv:
        combined_df.to_csv(output_csv)

    # Filter out the extra heading rows
    combined_df = combined_df.filter(~((combined_df["Name"] == "Name") &
                                 (combined_df["Country"] == "Country") &
                                 (combined_df["Nick"] == "Nick")))

    # In the absence of true identifiers, using the intersection of these
    # three fields to identify users. This, unfortunately, drops five rows
    # (through the 2024 GP, that is).
    combined_df = combined_df.unique(
        subset=["Name", "Country", "Nick", "source_file"],
        keep="first"
    )

    # I believe the `Nick` is permanent, but users can decide (and change their decision) on
    # whether to show it or not. The other values they can change any time, but it looks like
    # historical scores for prior years do not update. For now I will use all three fields.
    combined_df = combined_df.with_columns(
        (
            combined_df["Name"].fill_null("Nameless") +
            " (" + 
            combined_df["Nick"].fill_null("Nickless") +
            ") - " + 
            combined_df["Country"].fill_null("Nationless")
        ).alias("user_pseudo_id")
    )

    combined_df = combined_df.with_columns(
        pl.col("Points").cast(pl.Float64).alias("Points")
    )

    combined_df = combined_df.with_columns(
            pl.col("Points")
            .rank(descending=True)
            .over("year")
            .alias("Rank_before_playoffs")
    )

    flat_playoff_results = pl.DataFrame(
        [
            {"year": year, "Playoff_rank": rank, "user_pseudo_id": solver}
            for year, results in shared.competitions.GP_PLAYOFF_RESULTS.items()
            for rank, solver in results.items()
        ]
    )

    with_playoff_rank = combined_df.join(
        flat_playoff_results, on=["year", "user_pseudo_id"], how="left")

    with_playoff_rank = with_playoff_rank.sort(
        by=["year", "Playoff_rank", "Points"], descending=[True, True, False])

    with_playoff_rank = with_playoff_rank.with_columns(
        (pl.col("user_pseudo_id").cum_count(reverse=True).over("year")).alias("Rank")
    )

    with_playoff_rank = apply_types(with_playoff_rank)

    ordered_cols = ["Name", "Country", "Nick"]

    all_columns = with_playoff_rank.columns
    for item in ordered_cols:
        all_columns.remove(item)
    ordered_cols.extend(all_columns)
    with_playoff_rank = with_playoff_rank.select(ordered_cols)

    return with_playoff_rank
