import os
#import pandas as pd
import polars as pl

import streamlit as st

import shared.constants

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
    df['Name'] = df['Name'].replace("TanTan Dai", "Tantan Dai")
    df['Name'] = df['Name'].replace("Dai Tantan", "Tantan Dai")
    df['Name'] = df['Name'].replace("Seongwon Jin", "Sung-Won Jin")
    df['Name'] = df['Name'].replace("Timothy DOYLE", "Timothy Doyle")

    # I thought nick was permanent — is that mistaken or is this from people
    # signing up for new accounts?
    df['Nick'] = df['Nick'].replace("Qyz_", "qyz")
    df['Nick'] = df['Nick'].replace("The Scrasse", "TheScrasse")
    df['Nick'] = df['Nick'].replace("x18349276", "TheScrasse")
    df['Nick'] = df['Nick'].replace("ChessCombinatorics", "BeautyOfConfigurations")
    df['Nick'] = df['Nick'].replace("CosmicCombination", "BeautyOfConfigurations")
    df['Nick'] = df['Nick'].replace("CosmicQuietude", "BeautyOfConfigurations")
    df['Nick'] = df['Nick'].replace("TheHolyGame", "BeautyOfConfigurations")
    df['Nick'] = df['Nick'].replace("TheWhisperingBullet", "BeautyOfConfigurations")
    df['Nick'] = df['Nick'].replace("TheXTrain", "BeautyOfConfigurations")
    df.loc[df["Name"] == "Darina Maratova", "Nick"] = "DarinaM"
    df.loc[df["Name"] == "Bobo Lo", "Nick"] = "Seyeonnie"
    df.loc[df["Name"] == "Izabella Tilkin", "Nick"] = "creta"
    df.loc[df["Name"] == "Ytep Flores", "Nick"] = "AlexCross"
    df.loc[df["Name"] == "Zalak Ghetia", "Nick"] = "puzzlegirl"
    df.loc[df["Name"] == "Bruno Rivara", "Nick"] = "Bruno61"
    df.loc[df["Name"] == "H. L. Vu", "Nick"] = "gimmick"
    df.loc[df["Name"] == "Karthika Balusamy", "Nick"] = "Light"
    df.loc[df["Name"] == "Minfang Lin", "Nick"] = "leafcard"
    df.loc[df["Name"] == "Paul Hlebowitsh", "Nick"] = "FLEB"
    df.loc[df["Name"] == "Ryotaro Chiba", "Nick"] = "EctoPlasma"
    df.loc[df["Name"] == "Félix Meyer", "Nick"] = "NewStar"
    df.loc[df["Name"] == "Cheryl Gaul", "Nick"] = "cgaul"
    df.loc[df["Name"] == "Howard Wilkinson", "Nick"] = "HWHW"
    df.loc[df["Name"] == "Riley Guerin", "Nick"] = "Bluey"
    df.loc[df["Name"] == "Sirawit Pulketkij", "Nick"] = "Potter"
    df.loc[df["Name"] == "Sultan GÜLTAŞ", "Nick"] = "Sultan09"
    df.loc[df["Name"] == "Taavi Piller", "Nick"] = "Taavi"
    df.loc[df["Name"] == "Virgi Puusepp", "Nick"] = "Virgip"
    df.loc[df["Name"] == "Wesley Barton", "Nick"] = "sparrowhawk73"
    df.loc[df["Name"] == "Sitanshu Sah", "Nick"] = "sitaswag"
    df.loc[df["Name"] == "Valeria Losasso", "Nick"] = "Bely"
    df.loc[df["Name"] == "daniele cassani", "Nick"] = "dany_thor"
    df.loc[df["Name"] == "akash doulani", "Nick"] = "akashdoulani78"
    df.loc[df["Name"] == "Esmeralda Kleinreesink", "Nick"] = "Esmeralda Kleinreesink"
    df.loc[df["Name"] == "James Anderson", "Nick"] = "Holboo"
    df.loc[df["Name"] == "Mohammad Amini Rad", "Nick"] = "Kobresia"
    df.loc[df["Name"] == "Sohaima Jabeen", "Nick"] = "sohaima"
    df.loc[df["Name"] == "Avinash Kumar", "Nick"] = "ak_iit"
    df.loc[df["Name"] == "Janelle Aleisonne Navarro", "Nick"] = "Alison"
    df.loc[df["Name"] == "Jimin HWANG", "Nick"] = "GGFJH"
    df.loc[df["Name"] == "Sebastian Matschke", "Nick"] = "Semax"
    df.loc[df["Name"] == "Sérgio Schwarz de Assis Farias", "Nick"] = "Schwarz"
    df.loc[df["Name"] == "Zhen Fan", "Nick"] = "FierceHAuCl4"
    df.loc[df["Name"] == "betty bei", "Nick"] = "beibeiball"
    df.loc[df["Name"] == "Ömer DURMAZ", "Nick"] = "mrdrmz"
    df.loc[df["Name"] == "Katerina Sabevska", "Nick"] = "k_2005"
    df.loc[df["Name"] == "Pat Stanford", "Nick"] = "Kaysman"
    df.loc[df["Name"] == "Pitchpreeya Jullathochai", "Nick"] = "MaiPrae"
    df.loc[df["Name"] == "Sae Joon Jang", "Nick"] = "jonahjang"
    df.loc[df["Name"] == "michael stitzel", "Nick"] = "mikeylyk"
    df.loc[df["Name"] == "Alan Filipin", "Nick"] = "alanfilipin"
    df.loc[df["Name"] == "Deepankar Sharma", "Nick"] = "Deep"
    df.loc[df["Name"] == "Jeannette Fries", "Nick"] = "swissjane"
    df.loc[df["Name"] == "Kentaro Shibata", "Nick"] = "esqn"
    df.loc[df["Name"] == "MinHyeok Choi", "Nick"] = "applejackcmh"
    df.loc[df["Name"] == "Sravani Sripada", "Nick"] = "scampy"
    df.loc[df["Name"] == "Supachai Thongsawang", "Nick"] = "AgentK"
    df.loc[df["Name"] == "Bhuvaneshwari S", "Nick"] = "Bhuvi"
    df.loc[df["Name"] == "Bret Kugler", "Nick"] = "SOTC"
    df.loc[df["Name"] == "Rohan Rao", "Nick"] = "Rohan Rao"

    # People who seem to have changed their country value
    df.loc[df["Name"] == "Jimin HWANG", "Country"] = "Korea, South"
    df.loc[df["Name"] == "James Anderson", "Country"] = "American Samoa"
    df.loc[df["Name"] == "Howard Wilkinson", "Country"] = "UK"
    df.loc[df["Name"] == "Jay Mark", "Country"] = "USA"
    df.loc[df["Name"] == "Wesley Barton", "Country"] = "Canada"
    df.loc[df["Name"] == "Josh Bao", "Country"] = "Singapore"
    df.loc[df["Name"] == "Sérgio Schwarz de Assis Farias", "Country"] = "Brazil"
    df.loc[df["Name"] == "Zhen Fan", "Country"] = "China"
    df.loc[df["Name"] == "betty bei", "Country"] = "China"
    df.loc[df["Name"] == "Kevin Lee", "Country"] = "Hong Kong"
    df.loc[df["Name"] == "Timothy O'Shea", "Country"] = "USA"
    df.loc[df["Name"] == "Bruno Rivara", "Country"] = "Switzerland"
    df.loc[df["Name"] == "H. L. Vu", "Country"] = "Vietnam"
    df.loc[df["Name"] == "Karthika Balusamy", "Country"] = "Ireland"
    df.loc[df["Name"] == "P S", "Country"] = "Israel"
    df.loc[df["Name"] == "Diana Huang", "Country"] = "USA"
    df.loc[df["Name"] == "Zalak Ghetia", "Country"] = "USA"
    df.loc[df["Name"] == "Sravani Sripada", "Country"] = "Canada"
    df.loc[df['Name'] == 'CJ Tan', 'Country'] = "Philippines"

    # df = df.with_columns(
    #     pl.when(pl.col("Name") == "TanTan Dai").then("Tantan Dai")
    #     .when(pl.col("Name") == "Dai Tantan").then("Tantan Dai")
    #     .when(pl.col("Name") == "Seongwon Jin").then("Sung-Won Jin")
    #     .when(pl.col("Name") == "Timothy DOYLE").then("Timothy Doyle")
    #     .otherwise(pl.col("Name")).alias("Name")
    # )

    # df = df.with_columns(
    #     pl.when(pl.col("Nick") == "Qyz_").then("qyz")
    #     .when(pl.col("Nick") == "The Scrasse").then("TheScrasse")
    #     .when(pl.col("Nick") == "x18349276").then("TheScrasse")
    #     .when(pl.col("Nick") == "ChessCombinatorics").then("BeautyOfConfigurations")
    #     .when(pl.col("Nick") == "CosmicCombination").then("BeautyOfConfigurations")
    #     .when(pl.col("Nick") == "CosmicQuietude").then("BeautyOfConfigurations")
    #     .when(pl.col("Nick") == "TheHolyGame").then("BeautyOfConfigurations")
    #     .when(pl.col("Nick") == "TheWhisperingBullet").then("BeautyOfConfigurations")
    #     .when(pl.col("Nick") == "TheXTrain").then("BeautyOfConfigurations")
    #     .when(pl.col("Name") == "Darina Maratova").then("DarinaM")
    #     .when(pl.col("Name") == "Bobo Lo").then("Seyeonnie")
    #     .when(pl.col("Name") == "Izabella Tilkin").then("creta")
    #     .when(pl.col("Name") == "Ytep Flores").then("AlexCross")
    #     .when(pl.col("Name") == "Zalak Ghetia").then("puzzlegirl")
    #     .when(pl.col("Name") == "Bruno Rivara").then("Bruno61")
    #     .when(pl.col("Name") == "H. L. Vu").then("gimmick")
    #     .when(pl.col("Name") == "Karthika Balusamy").then("Light")
    #     .when(pl.col("Name") == "Minfang Lin").then("leafcard")
    #     .when(pl.col("Name") == "Paul Hlebowitsh").then("FLEB")
    #     .when(pl.col("Name") == "Ryotaro Chiba").then("EctoPlasma")
    #     .when(pl.col("Name") == "Félix Meyer").then("NewStar")
    #     .when(pl.col("Name") == "Cheryl Gaul").then("cgaul")
    #     .when(pl.col("Name") == "Howard Wilkinson").then("HWHW")
    #     .when(pl.col("Name") == "Riley Guerin").then("Bluey")
    #     .when(pl.col("Name") == "Sirawit Pulketkij").then("Potter")
    #     .when(pl.col("Name") == "Sultan GÜLTAŞ").then("Sultan09")
    #     .when(pl.col("Name") == "Taavi Piller").then("Taavi")
    #     .when(pl.col("Name") == "Virgi Puusepp").then("Virgip")
    #     .when(pl.col("Name") == "Wesley Barton").then("sparrowhawk73")
    #     .when(pl.col("Name") == "Sitanshu Sah").then("sitaswag")
    #     .when(pl.col("Name") == "Valeria Losasso").then("Bely")
    #     .when(pl.col("Name") == "daniele cassani").then("dany_thor")
    #     .when(pl.col("Name") == "akash doulani").then("akashdoulani78")
    #     .when(pl.col("Name") == "Esmeralda Kleinreesink").then("Esmeralda Kleinreesink")
    #     .when(pl.col("Name") == "James Anderson").then("Holboo")
    #     .when(pl.col("Name") == "Mohammad Amini Rad").then("Kobresia")
    #     .when(pl.col("Name") == "Sohaima Jabeen").then("sohaima")
    #     .when(pl.col("Name") == "Avinash Kumar").then("ak_iit")
    #     .when(pl.col("Name") == "Janelle Aleisonne Navarro").then("Alison")
    #     .when(pl.col("Name") == "Jimin HWANG").then("GGFJH")
    #     .when(pl.col("Name") == "Sebastian Matschke").then("Semax")
    #     .when(pl.col("Name") == "Sérgio Schwarz de Assis Farias").then("Schwarz")
    #     .when(pl.col("Name") == "Zhen Fan").then("FierceHAuCl4")
    #     .when(pl.col("Name") == "betty bei").then("beibeiball")
    #     .when(pl.col("Name") == "Ömer DURMAZ").then("mrdrmz")
    #     .when(pl.col("Name") == "Katerina Sabevska").then("k_2005")
    #     .when(pl.col("Name") == "Pat Stanford").then("Kaysman")
    #     .when(pl.col("Name") == "Pitchpreeya Jullathochai").then("MaiPrae")
    #     .when(pl.col("Name") == "Sae Joon Jang").then("jonahjang")
    #     .when(pl.col("Name") == "michael stitzel").then("mikeylyk")
    #     .when(pl.col("Name") == "Alan Filipin").then("alanfilipin")
    #     .when(pl.col("Name") == "Deepankar Sharma").then("Deep")
    #     .when(pl.col("Name") == "Jeannette Fries").then("swissjane")
    #     .when(pl.col("Name") == "Kentaro Shibata").then("esqn")
    #     .when(pl.col("Name") == "MinHyeok Choi").then("applejackcmh")
    #     .when(pl.col("Name") == "Sravani Sripada").then("scampy")
    #     .when(pl.col("Name") == "Supachai Thongsawang").then("AgentK")
    #     .when(pl.col("Name") == "Bhuvaneshwari S").then("Bhuvi")
    #     .when(pl.col("Name") == "Bret Kugler").then("SOTC")
    #     .when(pl.col("Name") == "Rohan Rao").then("Rohan Rao")
    #     .otherwise(pl.col("Nick")).alias("Nick")
    # )

    # df = df.with_columns(
    #     pl.when(pl.col("Name") == "Jimin HWANG").then("Korea, South")
    #     .when(pl.col("Name") == "James Anderson").then("American Samoa")
    #     .when(pl.col("Name") == "Howard Wilkinson").then("UK")
    #     .when(pl.col("Name") == "Jay Mark").then("USA")
    #     .when(pl.col("Name") == "Wesley Barton").then("Canada")
    #     .when(pl.col("Name") == "Josh Bao").then("Singapore")
    #     .when(pl.col("Name") == "Sérgio Schwarz de Assis Farias").then("Brazil")
    #     .when(pl.col("Name") == "Zhen Fan").then("China")
    #     .when(pl.col("Name") == "betty bei").then("China")
    #     .when(pl.col("Name") == "Kevin Lee").then("Hong Kong")
    #     .when(pl.col("Name") == "Timothy O'Shea").then("USA")
    #     .when(pl.col("Name") == "Bruno Rivara").then("Switzerland")
    #     .when(pl.col("Name") == "H. L. Vu").then("Vietnam")
    #     .when(pl.col("Name") == "Karthika Balusamy").then("Ireland")
    #     .when(pl.col("Name") == "P S").then("Israel")
    #     .when(pl.col("Name") == "Diana Huang").then("USA")
    #     .when(pl.col("Name") == "Zalak Ghetia").then("USA")
    #     .when(pl.col("Name") == "Sravani Sripada").then("Canada")
    #     .when(pl.col("Name") == "CJ Tan").then("Philippines")
    #     .otherwise(pl.col("Country")).alias("Country")
    # )

    return df

@st.cache_data
def load_gp(csv_directory="data/processed/gp", verbose=False, output_csv=None):
    """Import GP CSV files and return a single dataset.
    
    This creates a dataset covering all years with one row per
    solver-year combination. This also creates an identifier out of
    the Name, Country, and Nick fields.
    """
    dataframes = []
    all_columns = set()

    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            if verbose:
                print(f"Parsing file {filename}")
            file_path = os.path.join(csv_directory, filename)

            df = pl.read_csv(file_path)
            df['source_file'] = filename
            #df = df.with_columns(
            #    pl.lit(filename).alias("source_file")
            #)
            dataframes.append(df)
            all_columns.update(df.columns)

    aligned_dfs = []
    for df in dataframes:
        missing_columns = all_columns - set(df.columns)
        for col in missing_columns:
            df = df.with_columns([pl.lit(None).alias(col)])
        aligned_dfs.append(df.select(sorted(all_columns)))

    combined_df = pl.concat(aligned_dfs, how="vertical")

    print(combined_df.columns)
    combined_df = manual_adjustements(combined_df)

    # Save the combined DataFrame to a new CSV (optional)
    if output_csv:
        combined_df.to_csv(output_csv, index=False)
        #combined_df.to_csv(output_csv)

    # Filter out the extra heading rows
    combined_df = combined_df[~((combined_df["Name"] == "Name") &
                                (combined_df["Country"] == "Country") &
                                (combined_df["Nick"] == "Nick"))]
    # combined_df = combined_df.filter(~((combined_df["Name"] == "Name") &
    #                             (combined_df["Country"] == "Country") &
    #                             (combined_df["Nick"] == "Nick")))

    # In the absence of true identifiers, using the intersection of these
    # three fields to identify users. This, unfortunately, drops five rows
    (through the 2024 GP, that is).
    combined_df.drop_duplicates(
       subset=("Name", "Country", "Nick", "source_file"), keep="first", inplace=True)
    # combined_df = combined_df.unique(
    #     subset=["Name", "Country", "Nick", "source_file"],
    #     keep="first"
    # )

    # I believe the `Nick` is permanent, but users can decide (and change their decision) on
    # whether to show it or not. The other values they can change any time, but it looks like
    # historical scores for prior years do not update. For now I will use all three fields.
    #sep = "_"
    #combined_df["user_pseudo_id"] = (combined_df["Name"].fillna('None') + sep +
    #                                 combined_df["Nick"].fillna('None') + sep +
    #                                 combined_df["Country"].fillna('None'))
    #
    combined_df["user_pseudo_id"] = (combined_df['Name'].fillna('Nameless') +
                                     " (" + 
                                     combined_df['Nick'].fillna('Nickless') +
                                     ") - " +
                                     combined_df['Country'].fillna('Nationless'))
    
    # combined_df = combined_df.with_columns(
    #     (
    #         combined_df["Name"].fill_null("Nameless") + 
    #         " (" + 
    #         combined_df["Nick"].fill_null("Nickless") + 
    #         ") - " + 
    #         combined_df["Country"].fill_null("Nationless")
    #     ).alias("user_pseudo_id")
    # )

    combined_df["Points"] = pd.to_numeric(combined_df["Points"], errors="coerce")
    # combined_df = combined_df.with_columns(
    #     pl.col("Points").cast(pl.Float32).alias("Points")
    # )

    combined_df["Rank_before_playoffs"] = combined_df.groupby("year")["Points"].rank(ascending=False)
    # combined_df = combined_df.with_columns(
    #     combined_df.groupby("year").agg(
    #         pl.col("Points").rank(method="ordinal", descending=True).alias("Rank_before_playoffs")
    #     )["Rank_before_playoffs"]
    # )

    flat_playoff_results = pd.DataFrame([
        {"year": year, "Playoff_rank": rank, "user_pseudo_id": solver}
        for year, results in shared.constants.GP_PLAYOFF_RESULTS.items()
        for rank, solver in results.items()
    ])
    # flat_playoff_results = pl.DataFrame(
    #     [
    #         {"year": year, "Playoff_rank": rank, "user_pseudo_id": solver}
    #         for year, results in shared.constants.GP_PLAYOFF_RESULTS.items()
    #         for rank, solver in results.items()
    #     ]
    # )

    with_playoff_rank = pd.merge(combined_df, flat_playoff_results, how="left", on=["year", "user_pseudo_id"])
    # with_playoff_rank = combined_df.join(
    #     flat_playoff_results, on=["year", "user_pseudo_id"], how="left")
 
    with_playoff_rank = with_playoff_rank.sort_values(by=["year", "Playoff_rank", "Points"], ascending=[False, True, False])
    # with_playoff_rank = with_playoff_rank.sort(
    #     by=["year", "Playoff_rank", "Points"], descending=[False, True, False])

    with_playoff_rank["Rank"] = with_playoff_rank.groupby("year").cumcount() + 1
    # with_playoff_rank = with_playoff_rank.with_columns(
    #     pl.col("user_pseudo_id").cumcount().over("year").alias("Rank") + 1
    # )
    #with_playoff_rank.set_index("user_pseudo_id", inplace=True)

    return with_playoff_rank

