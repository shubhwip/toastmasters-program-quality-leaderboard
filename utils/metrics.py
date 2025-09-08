import pandas as pd
from datetime import date

def calculate_points(df: pd.DataFrame) -> pd.DataFrame:
    # L1
    df['L1 Points'] = df['Level 1s'].clip(upper=4) * 100
    
    # L2 (base + additional)
    df['L2 Points'] = (df['Level 2s'] + df['Add. Level 2s']).clip(upper=2) * 200
    
    # L3
    df['L3 Points'] = df['Level 3s'].clip(upper=2) * 300

    # L4 – only once
    df['L4 Points'] = df['Level 4s, Path Completions, or DTM Awards'].apply(lambda x: 400 if x >= 1 else 0)

    # L5 – only once
    df['L5 Points'] = df['Add. Level 4s, Path Completions, or DTM award'].apply(lambda x: 500 if x >= 1 else 0)

    # COT Training Rounds
    df['COT R1 Points'] = df['Off. Trained Round 1'].apply(lambda x: 200 if x >= 7 else 0)
    df['COT R2 Points'] = df['Off. Trained Round 2'].apply(lambda x: 200 if x >= 7 else 0)

    # Total Points
    df['Total Club Points'] = df[
        ['L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points', 'COT R1 Points', 'COT R2 Points']
    ].sum(axis=1)

    return df

def calculate_contest_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns one row per club with four contest scores as columns.
    Score = 100 if contest date is entered, else 0.
    """

    COL_CLUB = "Select Your Club"
    date_cols = {
        "Humorous Contest": "Date the Humorous Speech Contest was held",
        "TableTopics Contest": "Date the Table Topics Contest was held",
        "Evaluation Contest": "Date the Evaluation Contest was held",
        "International Contest": "Date the International Speech Contest was held",
    }

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()
    
    # Start with club column
    scores = pd.DataFrame()
    scores["Club Name"] = df[COL_CLUB].unique()

    # For each contest, compute max score (so multiple submissions collapse to one score per club)
    for contest, col in date_cols.items():
        scores_contest = (
            df.groupby(COL_CLUB)[col]
              .apply(lambda x: 100 if x.notna().any() and (x.astype(str).str.strip() != "").any() else 0)
              .reset_index(name=contest)
        )
        scores = scores.merge(scores_contest, left_on="Club Name", right_on=COL_CLUB).drop(columns=[COL_CLUB])

    return scores

def assign_grouping(df: pd.DataFrame) -> pd.DataFrame:
    # Define group by active members
    def get_group(members):
        if members < 12:
            return 'Group 1'
        elif 12 <= members <= 20:
            return 'Group 2'
        elif 21 <= members <= 40:
            return 'Group 3'
        elif 41 <= members <= 100:
            return 'Group 4'
        else:
            return 'Unknown'

    # Apply group
    df['Group'] = df['Active Members'].apply(get_group)

    # Add group name and description
    group_meta = {
        'Group 1': {'Name': 'Spark Clubs', 'Description': 'Small but full of potential, these clubs are just igniting.'},
        'Group 2': {'Name': 'Rising Stars', 'Description': 'Gaining traction, these clubs are building energy and cohesion.'},
        'Group 3': {'Name': 'Powerhouse Clubs', 'Description': 'Well-established, these clubs thrive on teamwork and synergy.'},
        'Group 4': {'Name': 'Pinnacle Clubs', 'Description': 'Large, vibrant clubs at the peak of influence and activity.'},
        'Unknown': {'Name': 'Undefined', 'Description': 'Club size not in defined range.'}
    }

    df['Group Name'] = df['Group'].map(lambda g: group_meta[g]['Name'])
    df['Group Description'] = df['Group'].map(lambda g: group_meta[g]['Description'])

    # Rank within group
    df = df.sort_values(['Group', 'Total Club Points'], ascending=[True, False])
    df['Group Rank'] = df.groupby('Group')['Total Club Points'].rank(method='dense', ascending=False).astype(int)

    return df

def mot_scores(df: pd.DataFrame) -> pd.DataFrame:
    COL_CLUB = "Select Your Club"
    COL_DATE = "Date the MOT session was conducted"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()
    # convert to datetime (dayfirst since it's dd/mm/yyyy)
    mot_dates = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce").dt.date

    q1_start, q1_end = date(2025, 7, 1), date(2025, 12, 31)
    q2_start, q2_end = date(2026, 1, 1), date(2026, 6, 30)

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "MOT_Q1": ((mot_dates >= q1_start) & (mot_dates <= q1_end)).astype(int) * 150,
        "MOT_Q3": ((mot_dates >= q2_start) & (mot_dates <= q2_end)).astype(int) * 150
    })

    return df_out.groupby("Club Name", as_index=False).max()

def club_success_plan_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Club_Success_Plan
    - 200 points if 'Club Success Plan Submission Date' has a valid date
    """

    COL_CLUB = "Select Your Club"
    COL_DATE = "Club Success Plan Submission Date"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    # Convert to datetime (handles dd/mm/yyyy nicely)
    plan_dates = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce")

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Club_Success_Plan": plan_dates.notna().astype(int) * 200
    })

    # One row per club (200 if any submission)
    return df_out.groupby("Club Name", as_index=False).max()


def pathways_completion_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Pathways_Completion_Celebration
    - 100 points if the club is listed (i.e., participated)
    """

    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Pathways_Completion_Celebration": 100
    })

    return df_out.groupby("Club Name", as_index=False).max()

def mentorship_programme_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Mentorship_Programme
    - 100 points if the club is listed (i.e., participated)
    """

    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Mentorship_Programme": 100
    })

    return df_out.groupby("Club Name", as_index=False).max()

def distinguished_club_partners_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Distinguished_Club_Partners
    - 500 points if the club is listed (i.e., helped another club become distinguished)
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Distinguished_Club_Partners": 500
    })

    return df_out.groupby("Club Name", as_index=False).max()

def successful_handover_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Successful_Transition_Handover
    - 200 points if the club is listed (i.e., submitted handover report)
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Successful_Transition_Handover": 200
    })

    return df_out.groupby("Club Name", as_index=False).max()

def quality_initiatives_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Quality_Initiatives
    - 150 points if the club submitted a unique quality initiative (e.g., Speakathon, themed meeting)
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Quality_Initiatives": 150
    })

    return df_out.groupby("Club Name", as_index=False).max()

def member_onboarding_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Member_Onboarding
    - 100 points if the club reported having a member onboarding program
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Member_Onboarding": 100
    })

    return df_out.groupby("Club Name", as_index=False).max()
