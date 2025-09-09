import pandas as pd
import streamlit as st
import re
from datetime import datetime
import requests
from utils.metrics import *

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


# ------------------ Load and Prepare Data ------------------ #
def load_data_club_performance(gsheet_url=None):

    file_id = st.secrets["GOOGLE_DRIVE_FILE_ID_CLUB_PERFORMANCE"]
    gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    update_date = extract_update_date(gsheet_url)
    df = pd.read_csv(gsheet_url)
    df = calculate_points(df)
    df = assign_grouping(df)
    df = df[df['Group'] != 'Unknown']
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


def prepare_pathways_pioneers_data(df_club_performance):
    """
    Process club performance data and merge with contest data to create pathways pioneers leaderboard.
    
    Args:
        df_club_performance: DataFrame with club performance data
        
    Returns:
        DataFrame with processed pathways pioneers data
    """
    df = df_club_performance.copy()
    
    group_map = {
        'Group 1': 'Spark Clubs',
        'Group 2': 'Rising Stars',
        'Group 3': 'Powerhouse Clubs',
        'Group 4': 'Pinnacle Clubs'
    }
    df['Club Group'] = df['Group'].map(group_map)

    df_contests = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_CONTESTS", ["Select Your Club", "Humorous Contest", "TableTopics Contest", "Evaluation Contest", "International Contest"])
    
    contests_points = calculate_contest_points(df_contests)

    df_pathways_pioneers = df.merge(contests_points, left_on="Club Name", right_on="Club Name", how="left")

    # Add tier points
    df_pathways_pioneers['Pathways Pioneers'] = (
        df_pathways_pioneers[['L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points', 
               'Humorous Contest', 'TableTopics Contest', 'Evaluation Contest', 'International Contest']].sum(axis=1)
    )

    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Pathways Pioneers',
               'L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points', 
               'Humorous Contest', 'TableTopics Contest', 'Evaluation Contest', 'International Contest']
    df_pathways_pioneers = df_pathways_pioneers.fillna(0)
    # Sort and reset index
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
    
    group_map = {
        'Group 1': 'Spark Clubs',
        'Group 2': 'Rising Stars',
        'Group 3': 'Powerhouse Clubs',
        'Group 4': 'Pinnacle Clubs'
    }
    df['Club Group'] = df['Group'].map(group_map)

    # Load and process MOT data
    df_mot = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_MOMENTS_OF_TRUTH", ["Select Your Club", "MOT_Q1", "MOT_Q3"])
    df_mot_scores = mot_scores(df_mot)

    df_leadership_innovators = df.merge(df_mot_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Load and process PCC data
    df_pcc = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_PATHWAYS_COMPLETION_CELEBRATION", ["Select Your Club", "Pathways_Completion_Celebration"])
    df_pcc_scores = pathways_completion_scores(df_pcc)
    df_leadership_innovators = df_leadership_innovators.merge(df_pcc_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Load and process PCC data
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

    # Add tier points
    df_leadership_innovators['Leadership Innovators'] = (
        df_leadership_innovators[['COT R1 Points', 'COT R2 Points', 'MOT_Q1', 'MOT_Q3', 
                                  'Pathways_Completion_Celebration','Mentorship_Programme',
                                  'Distinguished_Club_Partners', 'Successful_Transition_Handover']].sum(axis=1)
    )

    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Leadership Innovators',
               'COT R1 Points', 'COT R2 Points', 'MOT_Q1', 'MOT_Q3', 
                'Pathways_Completion_Celebration','Mentorship_Programme',
                'Distinguished_Club_Partners', 'Successful_Transition_Handover']
    df_leadership_innovators = df_leadership_innovators.fillna(0)
    # Sort and reset index
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
    
    group_map = {
        'Group 1': 'Spark Clubs',
        'Group 2': 'Rising Stars',
        'Group 3': 'Powerhouse Clubs',
        'Group 4': 'Pinnacle Clubs'
    }
    df['Club Group'] = df['Group'].map(group_map)

    df_qis = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_QIS", ["Select Your Club", "Quality_Initiatives"])

    df_qis_scores = quality_initiatives_scores(df_qis)
    df_excellence_champions = df.merge(df_qis_scores, left_on="Club Name", right_on="Club Name", how="left")

    df_mo = load_csv_from_secret("GOOGLE_DRIVE_FILE_ID_MEMBER_ONBOARDING", ["Select Your Club", "Member_Onboarding"])

    df_mo_scores = member_onboarding_scores(df_mo)
    df_excellence_champions = df_excellence_champions.merge(df_mo_scores, left_on="Club Name", right_on="Club Name", how="left")

    df_excellence_champions["Club_Success_Plan"] = df_excellence_champions["CSP"].apply(
    lambda x: 200 if str(x).strip().upper() == "Y" else 0
    )

    # Add tier points
    df_excellence_champions['Excellence Champions'] = (
        df_excellence_champions[['Club_Success_Plan', 'Quality_Initiatives', 'Member_Onboarding']].sum(axis=1)
    )
    # Replace NaN values with 0
    df_excellence_champions = df_excellence_champions.fillna(0)
    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Excellence Champions', 'Club_Success_Plan', 'Quality_Initiatives', 'Member_Onboarding']

    # Sort and reset index
    return df_excellence_champions[columns].sort_values(by='Club Name').reset_index(drop=True)