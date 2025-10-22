import pandas as pd
import streamlit as st
import re
from datetime import datetime
import requests
from utils.metrics import *
import io

def extract_update_date(file_url):
    """Extract and format the last update date from filename in content-disposition header."""
    response = requests.get(file_url)
    content_disposition = response.headers.get('content-disposition', '')
    filename = re.findall("filename=(.+)", content_disposition)
    filename = filename[0] if filename else "Unknown"
    
    match = re.search(r"(\d{2})_(\d{2})_(\d{4})", filename)
    if match:
        day, month, year = match.groups()
        date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
        return date_obj.strftime("%B %d, %Y")
    return "Unknown"

def load_club_performance_data(secret_key: str) -> pd.DataFrame:
    """
    Loads Club Performance data from Google Drive using a secret key.
    
    Args:
        secret_key (str): The key to access the file ID from Streamlit secrets.

    Returns:
        pd.DataFrame: Cleaned DataFrame with valid club names.
    """
    try:
        file_id = st.secrets[secret_key]
        gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        df = pd.read_csv(gsheet_url)
        try:
            update_date = df.iloc[-1]['Division'][-10:]
        except Exception:
            update_date = "Not available"

        df = df[df["Club Name"].notna()]  # Filter rows with non-empty club names
        return df, update_date

    except Exception as e:
        st.warning(f"Could not load Club Performance data: {e}")
        return pd.DataFrame(), 'January 01, 1900'  # Return empty DataFrame on failure

# ------------------ Load and Prepare Data ------------------ #
def load_data_club_performance(gsheet_url=None):

    df_base, quater_base_date = load_club_performance_data(secret_key = "GOOGLE_DRIVE_FILE_ID_CLUB_PERFORMANCE_BASE")
    df_latest, update_date = load_club_performance_data(secret_key = "GOOGLE_DRIVE_FILE_ID_CLUB_PERFORMANCE")
    
    base_col = ['District', 'Division', 'Area', 'Club Number', 'Club Name',
       'Club Status', 'CSP', 'Mem. Base', 'Active Members', 'Net Growth']
    other_col = ['Club Number', 'Goals Met', 'Level 1s', 'Level 2s', 'Add. Level 2s', 'Level 3s',
       'Level 4s, Path Completions, or DTM Awards',
       'Add. Level 4s, Path Completions, or DTM award', 'New Members',
       'Add. New Members', 'Off. Trained Round 1', 'Off. Trained Round 2',
       'Mem. dues on time Oct', 'Mem. dues on time Apr', 'Off. List On Time',
       'Club Distinguished Status']

    df = df_base[base_col].merge(df_latest[other_col], on='Club Number', how='left')

    new_clubs = df_latest[~df_latest["Club Number"].isin(df_base["Club Number"])]

    df = pd.concat([df, new_clubs], ignore_index=True)

    df_edu_achievements = load_edu_ach_data("GOOGLE_DRIVE_FILE_ID_EDU_ACHIEVEMENTS", ["Club", "Name", "Award", "Date"])

    df = calculate_points(df, df_edu_achievements)
    df = assign_grouping(df)
    # df = df[df['Group'] != 'Unknown']
    return df, update_date

def load_csv_from_secret(secret_key: str, columns: list[str]) -> pd.DataFrame:
    """
    Loads a CSV from Google Drive using a file ID stored in Streamlit secrets.
    If loading fails, returns an empty DataFrame with the given columns.
    """
    try:
        file_id = st.secrets[secret_key]
        gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        df = pd.read_csv(gsheet_url)
    except Exception as e:
        # st.warning(f"Could not load file for {secret_key}: {e}")
        df = pd.DataFrame(columns=columns)
    return df

def load_data_from_secret(secret_key: str, columns: list[str]) -> pd.DataFrame:
    """
    Loads a CSV or XLSX file from Google Drive using a file ID stored in Streamlit secrets.
    Automatically detects the format based on file extension or content.
    If loading fails, returns an empty DataFrame with the given columns.
    """

    try:
        file_id = st.secrets[secret_key]
        gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        # Fetch the file bytes
        response = requests.get(gsheet_url)
        response.raise_for_status()
        content = response.content

        # Try to infer the type from headers or extension
        if "xlsx" in gsheet_url.lower() or response.headers.get("Content-Type", "").endswith("sheet"):
            df = pd.read_excel(io.BytesIO(content))
        elif "csv" in gsheet_url.lower() or "text" in response.headers.get("Content-Type", ""):
            df = pd.read_csv(io.BytesIO(content))
        else:
            # Fallback attempt: try CSV first, then Excel
            try:
                df = pd.read_csv(io.BytesIO(content))
            except Exception:
                df = pd.read_excel(io.BytesIO(content))

    except Exception as e:
        # st.warning(f"Could not load file for {secret_key}: {e}")
        df = pd.DataFrame(columns=columns)

    return df

def load_edu_ach_data(secret_key: str, columns: list[str]) -> pd.DataFrame:
    """
    Loads a CSV from Google Drive using a file ID stored in Streamlit secrets.
    If loading fails, returns an empty DataFrame with the given columns.
    """
    try:
        file_id = st.secrets[secret_key]
        gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        df = pd.read_excel(gsheet_url, sheet_name="Sheet1", skiprows=1)
    except Exception as e:
        st.warning(f"Could not load Education Achievements data: {e}")
        df = pd.DataFrame(columns=columns)
    return df

def prepare_pathways_pioneers_data(df_club_performance):
    """
    Process club performance data and merge with contest data to create pathways pioneers leaderboard.
    
    Args:
        df_club_performance: DataFrame with club performance data
        
    Returns:
        DataFrame with processed pathways pioneers data
    """
    df = df_club_performance.copy()

    df_contests = load_data_from_secret("GOOGLE_DRIVE_FILE_ID_CONTESTS", ["Select Your Club", "Humorous Contest", "TableTopics Contest", "Evaluation Contest", "International Contest"])
    
    contests_points = calculate_contest_points(df_contests)

    df_pathways_pioneers = df.merge(contests_points, left_on="Club Name", right_on="Club Name", how="left")

    df_pathways_pioneers = df_pathways_pioneers.fillna(0)

    # Add tier points
    df_pathways_pioneers['Pathways Pioneers'] = (
        df_pathways_pioneers[['L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points', 'DTM Points', 'TC Points', 
               'Humorous Contest', 'TableTopics Contest', 'Evaluation Contest', 'International Contest']].sum(axis=1)
    )

    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Pathways Pioneers',
               'L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points', 'DTM Points', 'TC Points',
               'Humorous Contest', 'TableTopics Contest', 'Evaluation Contest', 'International Contest']
    
    # Sort and reset index
    df_pathways_pioneers = df_pathways_pioneers[df_pathways_pioneers['Active Members'] >= 8]
    return df_pathways_pioneers[columns].sort_values(by='Club Name').reset_index(drop=True)

def prepare_leadership_innovators_data(df_club_performance):
    """
    Process club performance data and merge with MOT data to create leadership innovators leaderboard.
    
    Args:
        df_club_performance: DataFrame with club performance data
        
    Returns:
        DataFrame with processed leadership innovators data
    """
    df = df_club_performance.copy()

    # Load and process MOT data
    df_mot = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_MOMENTS_OF_TRUTH", ["Select Your Club", "MOT_Q1", "MOT_Q3"])
    df_mot_scores = mot_scores(df_mot)

    df_leadership_innovators = df.merge(df_mot_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Load and process PCC data
    df_pcc = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_PATHWAYS_COMPLETION_CELEBRATION", ["Select Your Club", "Pathways_Completion_Celebration"])
    df_pcc_scores = pathways_completion_scores(df_pcc)
    df_leadership_innovators = df_leadership_innovators.merge(df_pcc_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Load and process Mentorship Program data
    df_mp = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_MENTORSHIP_PROGRAM", ["Select Your Club", "Mentorship_Programme"])
    df_mp_scores = mentorship_programme_scores(df_mp)
    df_leadership_innovators = df_leadership_innovators.merge(df_mp_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Load and process dcp data
    df_dcp = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_DCP", ["Select Your Club", "Distinguished_Club_Partners"])
    df_dcp_scores = distinguished_club_partners_scores(df_dcp)
    df_leadership_innovators = df_leadership_innovators.merge(df_dcp_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Load and process sth data
    df_sth = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_STH", ["Select Your Club", "Successful_Transition_Handover"])
    df_sth_scores = successful_handover_scores(df_sth)
    df_leadership_innovators = df_leadership_innovators.merge(df_sth_scores, left_on="Club Name", right_on="Club Name", how="left")

    df_leadership_innovators['President_Distinguished'] = 0
    df_leadership_innovators['Smedley_Distinguished'] = 0

    df_leadership_innovators = df_leadership_innovators.fillna(0)

    # Add tier points
    df_leadership_innovators['Leadership Innovators'] = (
        df_leadership_innovators[['COT R1 Points', 'COT R2 Points', 'MOT_Q1', 'MOT_Q3', 
                                  'Pathways_Completion_Celebration','Mentorship_Programme',
                                  'President_Distinguished', 'Smedley_Distinguished',
                                  'Distinguished_Club_Partners', 'Successful_Transition_Handover']].sum(axis=1)
    )

    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Leadership Innovators',
               'COT R1 Points', 'COT R2 Points', 'MOT_Q1', 'MOT_Q3', 
                'Pathways_Completion_Celebration','Mentorship_Programme',
                'President_Distinguished', 'Smedley_Distinguished',
                'Distinguished_Club_Partners', 'Successful_Transition_Handover']
    
    # Sort and reset index
    df_leadership_innovators = df_leadership_innovators[df_leadership_innovators['Active Members'] >= 8]
    return df_leadership_innovators[columns].sort_values(by='Club Name').reset_index(drop=True)

def prepare_excellence_champions_data(df_club_performance):
    """
    Process club performance data and merge with Club Success Plan data to create excellence champions leaderboard.
    
    Args:
        df_club_performance: DataFrame with club performance data
        
    Returns:
        DataFrame with processed excellence champions data
    """
    df = df_club_performance.copy()

    df_qis = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_QIS", ["Select Your Club", "Quality_Initiatives"])

    df_qis_scores = quality_initiatives_scores(df_qis)
    df_excellence_champions = df.merge(df_qis_scores, left_on="Club Name", right_on="Club Name", how="left")

    df_mo = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_MEMBER_ONBOARDING", ["Select Your Club", "Member_Onboarding"])

    df_mo_scores = member_onboarding_scores(df_mo)
    df_excellence_champions = df_excellence_champions.merge(df_mo_scores, left_on="Club Name", right_on="Club Name", how="left")

    df_excellence_champions["Club_Success_Plan"] = df_excellence_champions["CSP"].apply(
    lambda x: 20 if str(x).strip().upper() == "Y" else 0
    )

    df_excellence_champions['FirstTime_Distinguished'] = 0
    df_excellence_champions['100%_Pathway_Registration'] = 0

    # Replace NaN values with 0
    df_excellence_champions = df_excellence_champions.fillna(0)

    # Add tier points
    df_excellence_champions['Excellence Champions'] = (
        df_excellence_champions[['Club_Success_Plan', 'FirstTime_Distinguished', 'Early10_Distinguished', 'Quality_Initiatives', '100%_Pathway_Registration', 'Member_Onboarding']].sum(axis=1)
    )
    
    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Excellence Champions', 'Club_Success_Plan', 'FirstTime_Distinguished', 'Early10_Distinguished', 'Quality_Initiatives', '100%_Pathway_Registration', 'Member_Onboarding']

    # Sort and reset index
    df_excellence_champions = df_excellence_champions[df_excellence_champions['Active Members'] >= 8]
    return df_excellence_champions[columns].sort_values(by='Club Name').reset_index(drop=True)