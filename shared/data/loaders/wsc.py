#import pandas as pd
import polars as pl

import streamlit as st

import shared.constants

#@st.cache_data
def process_wsc_2024(_df):
    """Process a CSV in the format used for the 2024 WSC."""
    df = _df.rename({
        "Official Rank": "Official_rank",
        "All": "Unofficial_rank",
        "Total": "WSC_total",
        "R1": "WSC_t1 points",
        "R2": "WSC_t2 points",
        "R3": "WSC_t3 points",
        "R4": "WSC_t4 points",
        "R5": "WSC_t5 points",
        "R6": "WSC_t6 points",
        "R7": "WSC_t7 points",
        "R10": "WSC_t10 points", # I don't know why they did this. To distinguish playoff rounds?
        "R11": "WSC_t11 points",
    })

    #df["Official"] = df["Official"] == "Y"
    df = df.with_columns(
        (pl.col("Official") == "Y").alias("Official"),
        #pl.col("Unofficial_rank").cast(pl.Int32).alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def process_wsc_2023(_df):
    """Process a CSV in the format used for the 2023 WSC."""
    df = _df.rename({
        "Official Rank   (w/o ties)": "Official_rank",
        "Total Score": "WSC_total",
        "Individual (before and after playoffs)": "Name",
        "Rd. 1": "WSC_t1 points",
        "Rd. 2": "WSC_t2 points",
        "Rd. 3": "WSC_t3 points",
        "Rd. 4": "WSC_t4 points",
        "Rd. 5": "WSC_t5 points",
        "Rd. 6": "WSC_t6 points",
        "Rd. 7": "WSC_t7 points",
        "Rd. 8": "WSC_t8 points",
        "Rd. 9": "WSC_t9 points",
        "Rd. 10": "WSC_t10 points",
    })

    #df["Official"] = df["Official Comp."] == "Y"
    #df["Unofficial_rank"] = df["WSC_total"].rank(ascending=False)
    df = df.with_columns(
        (pl.col("Official Comp.") == "Y").alias("Official"),
        #pl.col("WSC_total").str.replace(",", "").alias("WSC_total")
    )
    df = df.with_columns(
        pl.col("WSC_total").rank(descending=True).cast(pl.Int64).alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def process_wsc_2022(_df):
    """Process a CSV in the format used for the 2022 WSC."""
    df = _df.rename({
        "Points": "WSC_total",
        "Place": "Unofficial_rank",
        "Round 1": "WSC_t1 points",
        "Round 2": "WSC_t2 points",
        "Round 3": "WSC_t3 points",
        "Round 4": "WSC_t4 points",
        "Round 5": "WSC_t5 points",
        "Round 6": "WSC_t6 points",
        "Round 7": "WSC_t7 points",
        "Round 10": "WSC_t10 points",
        "Round 11": "WSC_t11 points",
        "Round 12": "WSC_t12 points",
    })

    # df["Name"] = (df["First name"] + " " + df["Last name"]).astype(str)
    # df["Official"] = df["Official"] == 1
    # df.loc[df["Official"], "Official_rank"] = df.loc[df["Official"], "Unofficial_rank"].rank()

    df = df.with_columns(
        (pl.col("First name") + pl.lit(" ") + pl.col("Last name")).alias("Name"),
        (pl.col("Official") == 1).alias("Official"),
        pl.col("Unofficial_rank").cast(pl.Int32).rank().cast(pl.Int64).alias("Official_rank")
    )

    return df

#@st.cache_data
def process_wsc_2019(_df):
    """Process a CSV in the format used for the 2019 WSC."""
    df = _df.rename({
        "Official": "Official_rank",
        "Pos": "Unofficial_rank",
        "Total": "WSC_total",
        "R 1": "WSC_t1 points",
        "R 2": "WSC_t2 points",
        "R 3": "WSC_t3 points",
        "R 4": "WSC_t4 points",
        "R 5": "WSC_t5 points",
        "R 6": "WSC_t6 points",
        "R 7": "WSC_t7 points",
        "R 11": "WSC_t11 points", # I don't know why they did this. To distinguish playoff rounds?
        "R 12": "WSC_t12 points",
        "R 13": "WSC_t13 points",
    })

    #df["Official"] = ~df["Official_rank"].isna()
    df = df.with_columns(
        pl.col("Official_rank").is_not_null().alias("Official")
    )

    return df

#@st.cache_data
def process_wsc_2018(_df):
    """Process a CSV in the format used for the 2018 WSC.
    
    Note: Wikipedia has Bastien in second and Tiit in third, disagreing with the ordering from our
    source file.

    Source: http://wscwpc2018.cz/wp-content/uploads/2018/11/WSC_offic_loga.pdf
    Wikipedia: https://en.wikipedia.org/wiki/World_Sudoku_Championship
    """
    df = _df.rename({
        "oﬃcial": "Official_rank",
        "index": "Unofficial_rank",
        "total": "WSC_total",
        "name": "Name",
        "round1": "WSC_t1 points",
        "round2": "WSC_t2 points",
        "round3": "WSC_t3 points",
        "round4": "WSC_t4 points",
        "round5": "WSC_t5 points",
        "round6": "WSC_t6 points",
        "round7": "WSC_t7 points",
        "round8": "WSC_t8 points",
        "round9": "WSC_t9 points",
        "round10": "WSC_t10 points",
    })

    #df["Official"] = ~df["Official_rank"].isna()
    df = df.with_columns(
        pl.col("Official_rank").is_not_null().alias("Official"),
        pl.col("Unofficial_rank").cast(pl.Int64).alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def process_wsc_2017(_df):
    """Process a CSV in the format used for the 2017 WSC."""
    df = _df.rename({
        "Official Rank": "Official_rank",
        "Overall Rank": "Unofficial_rank",
        "TOTAL": "WSC_total",
        "R01": "WSC_t1 points",
        "R02": "WSC_t2 points",
        "R03": "WSC_t3 points",
        "R04": "WSC_t4 points",
        "R05": "WSC_t5 points",
        "R06": "WSC_t6 points",
        "R07": "WSC_t7 points",
        "R11": "WSC_t11 points",
        "R12": "WSC_t12 points",
        "R13": "WSC_t13 points",
        "R14": "WSC_t14 points",
        "R15": "WSC_t15 points",
        "R16": "WSC_t16 points",
    })

    #df["Official"] = ~df["Official_rank"].isna()
    df = df.with_columns(
        pl.col("Official_rank").is_not_null().alias("Official")
    )

    return df

#@st.cache_data
def process_wsc_2016(_df):
    """Process a CSV in the format used for the 2016 WSC."""
    df = _df.rename({
        "All": "Unofficial_rank",
        "Total": "WSC_total",
        "R1": "WSC_t1 points",
        "R2": "WSC_t2 points",
        "R3": "WSC_t3 points",
        "R4": "WSC_t4 points",
        "R5": "WSC_t5 points",
        "R6": "WSC_t6 points",
        "R7": "WSC_t7 points",
        "R10": "WSC_t10 points",
        "R11": "WSC_t11 points",
        "R12": "WSC_t12 points",
    })

    # df["Name"] = (df["First name"] + " " + df["Last name"]).astype(str)
    # df["Official_rank"] = pd.to_numeric(
    #     df["Fin."].combine_first(df["Off."]), errors="coerce")
    # df["WSC_total"] = pd.to_numeric(df["WSC_total"].str.replace(",", ""), errors="coerce")
    # df["Official"] = ~df["Official_rank"].isna()

    df = df.with_columns(
        (pl.col("First name") + pl.lit(" ") + pl.col("Last name")).alias("Name"),
        pl.col("Fin.").fill_null(pl.col("Off.")).alias("Official_rank"),
        pl.col("WSC_total").str.replace(",", "").alias("WSC_total"),
        pl.col("WSC_t11 points").str.replace(",", "").alias("WSC_t11 points"),
        pl.col("WSC_t12 points").alias("WSC_t12 points")
    )
    df = df.with_columns(
        pl.col("Official_rank").is_not_null().alias("Official")
    )

    return df

#@st.cache_data
def process_wsc_2015(_df):
    """Process a CSV in the format used for the 2015 WSC."""
    df = _df.rename({
        "Total": "WSC_total",
        "Rank": "Unofficial_rank",
        "Round 1": "WSC_t1 points",
        "Round 2": "WSC_t2 points",
        "Round 3": "WSC_t3 points",
        "Round 4": "WSC_t4 points",
        "Round 5": "WSC_t5 points",
        "Round 6": "WSC_t6 points",
        "Round 8": "WSC_t8 points",
        "Round 9": "WSC_t9 points",
    })

    # df["Official_rank"] = pd.to_numeric(
    #     df["Play-off"].combine_first(df["Off. rank"]), errors="coerce")

    # df["Official"] = df["Off. rank"] != "---"

    df = df.with_columns(
        pl.col("Play-off").fill_null(pl.col("Off. rank")).replace("---", pl.lit(None)).cast(pl.Int64).alias("Official_rank"),
        (pl.col("Off. rank") != "---").alias("Official")
    )

    return df

#@st.cache_data
def process_wsc_2014(_df):
    """Process a CSV in the format used for the 2014 WSC."""
    df = _df.rename({
        "Total": "WSC_total",
        "Unofficial": "Unofficial_rank",
        "R1": "WSC_t1 points",
        "R2": "WSC_t2 points",
        "R3": "WSC_t3 points",
        "R4": "WSC_t4 points",
        "R5": "WSC_t5 points",
        "R6": "WSC_t6 points",
        "R9": "WSC_t9 points",
        "R10": "WSC_t10 points",
    })

    # # Third place tie.
    # df["Final"] = df["Final"].replace("3=", "3")

    # df["Official_rank"] = pd.to_numeric(df["Final"], errors="coerce")

    # # Original field didn't reflect playoffs for the top 10 competitors
    # playoff = df["Official_rank"] <= 10
    # df.loc[playoff, "Unofficial_rank"] = df[playoff]["Official_rank"]

    # df["Official"] = ~df["Official"].isna()

    df = df.with_columns(
        pl.col("Official").is_not_null().alias("Official"),
        # Third place tie.
        pl.col("Final").str.replace("3=", "3").alias("Final"),
        pl.col("WSC_t1 points").alias("WSC_t1 points")
    )
    df = df.with_columns(
        pl.col("Final").cast(pl.Int64).alias("Official_rank")
    )

    # Original field didn't reflect playoffs for the top 10 competitors
    df = df.with_columns(
        pl.when(pl.col("Official_rank") <= 10)
            .then(pl.col("Official_rank"))
            .otherwise(pl.col("Unofficial_rank"))
            .alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def process_wsc_2012(_df):
    """Process a CSV in the format used for the 2012 WSC."""
    df = _df.rename({
        "Total": "WSC_total",
        "All": "Unofficial_rank",
        "Competitor": "Name",
        "Part 1": "WSC_t1 points",
        "Part 2": "WSC_t2 points",
        "Part 3": "WSC_t3 points",
        "Part 4": "WSC_t4 points",
        "Part 5": "WSC_t5 points",
        "Part 6": "WSC_t6 points",
        "Part 7": "WSC_t7 points",
    })

    #df["Official_rank"] = pd.to_numeric(df["Off."], errors="coerce")

    # # Original field didn't reflect playoffs for the top 8 competitors
    # playoff = df["Official_rank"] <= 8
    # df.loc[playoff, "Unofficial_rank"] = df[playoff]["Official_rank"]

    # df["Official"] = ~df["Official_rank"].isna()

    df = df.with_columns(
        pl.col("Off.").cast(pl.Int64).alias("Official_rank"),
        pl.col("Off.").is_not_null().alias("Official")
    )

    # Original field didn't reflect playoffs for the top 8 competitors
    df = df.with_columns(
        pl.when(pl.col("Official_rank") <= 8)
            .then(pl.col("Official_rank"))
            .otherwise(pl.col("Unofficial_rank"))
            .alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def process_wsc_2011(_df):
    """Process a CSV in the format used for the 2011 WSC."""
    df = _df.rename({
        "Result": "WSC_total",
        "Nonoff": "Unofficial_rank",
        "Part 1": "WSC_t1 points",
        "Part 2": "WSC_t2 points",
        "Part 3": "WSC_t3 points",
        "Part 4": "WSC_t4 points",
        "Part 5": "WSC_t5 points",
        "Part 6": "WSC_t6 points",
        "Part 7": "WSC_t7 points",
        "Part 8": "WSC_t8 points",
        "Part 9": "WSC_t9 points",
        "Part 10": "WSC_t10 points",
    })

    # df["Name"] = (df["Name 1"] + " " + df["Name 2"]).astype(str)
    # # Validated that "Playoff" supercedes "Official" by looking at Wikipedia.
    # df["Official_rank"] = pd.to_numeric(
    #     df["Playoff"].combine_first(df["Official"]), errors="coerce")

    # # Original field didn't reflect playoffs for the top 10 competitors
    # playoff = df["Official_rank"] <= 10
    # df.loc[playoff, "Unofficial_rank"] = df[playoff]["Official_rank"]

    #df["Official"] = ~df["Official_rank"].isna()

    df = df.with_columns(
        (pl.col("Name 1") + pl.lit(" ") + pl.col("Name 2")).alias("Name"),
        pl.col("Official").is_not_null().alias("Official"),
        # Validated that "Playoff" supercedes "Official" by looking at Wikipedia.
        pl.col("Playoff").fill_null(pl.col("Official")).cast(pl.Int64).alias("Official_rank")
    )
    df = df.with_columns(
        # Original field didn't reflect playoffs for the top 10 competitors
        pl.when(pl.col("Official_rank") <= 10)
            .then(pl.col("Official_rank"))
            .otherwise(pl.col("Unofficial_rank"))
            .alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def process_wsc_2010(_df):
    """Process a CSV in the format used for the 2010 WSC."""
    df = _df.rename({
        "Score": "WSC_total",
        "Ranking": "Official_rank",
        "100m": "WSC_t1 points",
        "Long Jump": "WSC_t2 points",
        "Shot Put": "WSC_t3 points",
        "High Jump": "WSC_t4 points",
        "400m": "WSC_t5 points",
        "110m Hurdles": "WSC_t6 points",
        "Discus": "WSC_t7 points",
        "Pole Vault": "WSC_t8 points",
        "Javelin": "WSC_t9 points",
        "1500m": "WSC_t10 points",
    })

    # df['Name'] = df['Name'].str.rstrip('\n')

    # df["Official_rank"] = pd.to_numeric(df["Official_rank"], errors="coerce")
    # df["Unofficial_rank"] = df["Official_rank"]

    # # No indication of a disctinction between official and unoffical.
    # df["Official"] = True

    df = df.with_columns(
        pl.col("Name").str.replace_all("[\n]+$", "").alias("Name"),
        pl.col("Official_rank").cast(pl.Int64).alias("Official_rank"),
        pl.lit(True).alias("Official")
    )
    df = df.with_columns(
        pl.col("Official_rank").alias("Unofficial_rank")
    )

    return df

#@st.cache_data
def filter_wsc_fields(_df):
    df = _df

    """Keep the fields that we use later on and discard others."""
    kept_columns = ["year", "Name", "Official", "Official_rank", "Unofficial_rank", "WSC_total",
                    "WSC_entry"]
    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        round_name = f"WSC_t{wsc_round} points"
        if round_name in df.columns:
            kept_columns.append(round_name)

    #return df[kept_columns]
    return df.select(kept_columns)

#@st.cache_data
def numberize_round_columns(_df):
    """Convert every column to numeric, including stripping commas if necessary."""
    df = _df
    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        round_name = f"WSC_t{wsc_round} points"
        # Change string values (particularly with comma separators) to floag (see: 2016)
        #if round_name in df.columns and df[round_name].dtype == 'object':
        #    df[round_name] = pd.to_numeric(
        #        df[round_name].str.replace(',', ''), errors="coerce")
        #if round_name in df.columns:
        #    print(f"Round {round_name} has type {df.get_column(round_name).dtype}")
        if round_name in df.columns:
            if df.get_column(round_name).dtype == 'object':
                df = df.with_columns(pl.col(round_name).str.replace(',', '').cast(pl.Float64).alias(round_name))
            else:
                df = df.with_columns(pl.col(round_name).cast(pl.Float64).alias(round_name))

    df = df.with_columns(pl.col("WSC_total").cast(pl.Float64).alias("WSC_total"))

    return df

#@st.cache_data
def load_wsc(csv_directory="data/raw/wsc/"):
    """Load all WSC CSV files"""
    year_to_function = {
        # 2006 No website
        # 2007 No website
        # 2008 No website
        # 2009 Dead website
        2010: process_wsc_2010,
        2011: process_wsc_2011,
        2012: process_wsc_2012,
        # 2013 Dead website
        2014: process_wsc_2014,
        2015: process_wsc_2015,
        2016: process_wsc_2016,
        2017: process_wsc_2017,
        2018: process_wsc_2018,
        2019: process_wsc_2019,
        # 2020 no event
        # 2021 no event, although there was a WS "Competition"
        2022: process_wsc_2022, # But I only have the top 45 competitors.
        2023: process_wsc_2023,
        2024: process_wsc_2024
    }

    multiyear = None
    for year in reversed(sorted(year_to_function)):
        #data = pd.read_csv(f"{csv_directory}/wsc_{year}.csv")
        data = pl.read_csv(f"{csv_directory}/wsc_{year}.csv")
        processed = year_to_function[year](data)
        # processed["year"] = year
        # processed["WSC_entry"] = True
        # processed["WSC_total"] = pd.to_numeric(processed["WSC_total"], errors="coerce").astype(int)
        processed = processed.with_columns(
            pl.lit(year).alias("year"),
            pl.lit(True).alias("WSC_entry"),
            pl.col("WSC_total").cast(pl.Float64).alias("WSC_total")
        )
        processed = filter_wsc_fields(processed)
        processed = numberize_round_columns(processed)
        if multiyear is None:
            #multiyear = processed.copy()
            multiyear = processed
        else:
            #multiyear = pd.concat([multiyear, processed], ignore_index=True)
            min_year = 0
            if year <= min_year:
                st.write(year)
            multiyear_schema = multiyear.schema
            processed_schema = processed.schema
            for col in multiyear.columns:
                if col not in processed.columns:
                    processed = processed.with_columns(pl.lit(None).cast(multiyear_schema[col]).alias(col))
            for col in processed.columns:
                if col not in multiyear.columns:
                    multiyear = multiyear.with_columns(pl.lit(None).cast(processed_schema[col]).alias(col))
            processed = processed.select(multiyear.columns)
            if year <= min_year:
                st.write(list(zip(processed.columns, multiyear.dtypes, processed.dtypes)))
            #st.write(multiyear.dtypes)
            #st.write(processed.dtypes)
            multiyear = pl.concat([multiyear, processed], how="vertical")

    # Ensure a consistent ordering of the round columns
    round_columns = []
    for wsc_round in range(1, shared.constants.MAXIMUM_ROUND + 1):
        colname = f"WSC_t{wsc_round} points"
        if colname in multiyear:
            round_columns.append(colname)
    all_columns = [col for col in multiyear.columns if col not in round_columns] + round_columns
    #multiyear = multiyear[all_columns]
    multiyear = multiyear.select(all_columns)

    return multiyear

def polarize_wsc(wsc):
    wsc_polars = pl.from_pandas(wsc.reset_index())

    return wsc_polars
