import os
import pandas as pd

import streamlit as st

import shared.constants

@st.cache_data
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

    return df

@st.cache_data
def load_gp(csv_directory="data/processed/gp", verbose=False, output_csv=None):
    """Import GP CSV files and return a single dataset.
    
    This creates a dataset covering all years with one row per
    solver-year combination. This also creates an identifier out of
    the Name, Country, and Nick fields.
    """
    dataframes = []

    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            if verbose:
                print(f"Parsing file {filename}")
            file_path = os.path.join(csv_directory, filename)

            df = pd.read_csv(file_path)
            df['source_file'] = filename
            dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df = manual_adjustements(combined_df)

    # Save the combined DataFrame to a new CSV (optional)
    if output_csv:
        combined_df.to_csv(output_csv, index=False)

    # Filter out the extra heading rows
    combined_df = combined_df[~((combined_df["Name"] == "Name") &
                                (combined_df["Country"] == "Country") &
                                (combined_df["Nick"] == "Nick"))]

    # In the absence of true identifiers, using the intersection of these
    # three fields to identify users. This, unfortunately, drops five rows
    # (through the 2024 GP, that is).
    combined_df.drop_duplicates(
        subset=("Name", "Country", "Nick", "source_file"), keep="first", inplace=True)

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

    combined_df["Points"] = pd.to_numeric(combined_df["Points"], errors="coerce")
    combined_df["Rank_before_playoffs"] = combined_df.groupby("year")["Points"].rank(ascending=False)

    flat_playoff_results = pd.DataFrame([
        {"year": year, "Playoff_rank": rank, "user_pseudo_id": solver}
        for year, results in shared.constants.GP_PLAYOFF_RESULTS.items()
        for rank, solver in results.items()
    ])

    with_playoff_rank = pd.merge(combined_df, flat_playoff_results, how="left", on=["year", "user_pseudo_id"])
 
    # Create a ranking within each year that first uses `Playoff_rank`` and then descending `Points``
    with_playoff_rank = with_playoff_rank.sort_values(by=["year", "Playoff_rank", "Points"], ascending=[False, True, False])
    with_playoff_rank["Rank"] = with_playoff_rank.groupby("year").cumcount() + 1
    with_playoff_rank.set_index("user_pseudo_id", inplace=True)

    return with_playoff_rank

