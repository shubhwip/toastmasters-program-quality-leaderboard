import pandas as pd
import streamlit as st
import re
from datetime import datetime
import requests
from utils.metrics import calculate_points, assign_grouping, mot_scores, calculate_contest_points, club_success_plan_scores

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

    file_id_contests = st.secrets["GOOGLE_DRIVE_FILE_ID_CONTESTS"]
    gsheet_url_contests = f"https://drive.google.com/uc?export=download&id={file_id_contests}"
    df_contests = pd.read_csv(gsheet_url_contests)

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
    file_id_mot = st.secrets["GOOGLE_DRIVE_FILE_ID_MOMENTS_OF_TRUTH"]
    gsheet_url_mot = f"https://drive.google.com/uc?export=download&id={file_id_mot}"
    df_mot = pd.read_csv(gsheet_url_mot)
    df_mot_scores = mot_scores(df_mot)

    df_leadership_innovators = df.merge(df_mot_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Add tier points
    df_leadership_innovators['Leadership Innovators'] = (
        df_leadership_innovators[['COT R1 Points', 'COT R2 Points', 'MOT_Q1', 'MOT_Q3']].sum(axis=1)
    )

    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Leadership Innovators',
               'COT R1 Points', 'COT R2 Points', 'MOT_Q1', 'MOT_Q3']
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

    # Load and process Club Success Plan data
    file_id_csp = st.secrets["GOOGLE_DRIVE_FILE_ID_CLUB_SUCCESS_PLAN"]
    gsheet_url_csp = f"https://drive.google.com/uc?export=download&id={file_id_csp}"
    df_csp = pd.read_csv(gsheet_url_csp)
    df_csp_scores = club_success_plan_scores(df_csp)

    df_excellence_champions = df.merge(df_csp_scores, left_on="Club Name", right_on="Club Name", how="left")

    # Add tier points
    df_excellence_champions['Excellence Champions'] = (
        df_excellence_champions[['Club_Success_Plan']].sum(axis=1)
    )
    # Replace NaN values with 0
    df_excellence_champions = df_excellence_champions.fillna(0)
    # Select columns and format
    columns = ['Club Name', 'Club Group', 'Active Members', 'Excellence Champions', 'Club_Success_Plan']

    # Sort and reset index
    return df_excellence_champions[columns].sort_values(by='Club Name').reset_index(drop=True)