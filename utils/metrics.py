import pandas as pd
from datetime import date

def compute_award_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute award-based points per club.
    
    Rules:
    - Level 4 (40 points): if ANY of these codes appear: 
        DL4, EC4, EH4, IP4, LD4, MS4, PI4, PM4, SR4, VC4
    - Level 5 (50 points): if ANY of these codes appear: 
        EC5, EH5, IP5, LD5, MS5, PM5, SR5, VC5
    - DTM (60 points)
    - TC  (60 points)
    - FF  (30 points)
    """

    if df.empty:
        return pd.DataFrame(columns=[
            "Club Name", "Level_4_Points", "Level_5_Points",
            "DTM_Points", "TC_Points", "Early10_Distinguished"
        ])

    COL_CLUB = "Name"
    COL_AWARD = "Award"

    # Normalise awards text
    s = df[COL_AWARD].astype(str).str.upper().str.strip()

    # Define code sets
    level4_codes = {"DL4","EC4","EH4","IP4","LD4","MS4","PI4","PM4","SR4","VC4"}
    level5_codes = {"EC5","EH5","IP5","LD5","MS5","PM5","SR5","VC5"}

    # Row-level flags
    df["has_L4"] = s.isin(level4_codes)
    df["has_L5"] = s.isin(level5_codes)
    df["has_DTM"] = s.eq("DTM")
    df["has_TC"]  = s.eq("TC")
    df["has_FF"]  = s.eq("FF")

    # Collapse to club level
    club_flags = (
        df.groupby(COL_CLUB, dropna=False)[["has_L4","has_L5","has_DTM","has_TC","has_FF"]]
          .any()
          .reset_index()
    )

    # Map flags → points
    out = pd.DataFrame({
        "Club Name": club_flags[COL_CLUB],
        "L4 Points": club_flags["has_L4"].astype(int) * 40,
        "L5 Points": club_flags["has_L5"].astype(int) * 50,
        "DTM Points":     club_flags["has_DTM"].astype(int) * 60,
        "TC Points":      club_flags["has_TC"].astype(int)  * 60,
        "Early10_Distinguished":      club_flags["has_FF"].astype(int)  * 30,
    })

    return out


def calculate_points(df: pd.DataFrame, df_edu: pd.DataFrame) -> pd.DataFrame:
    # L1
    df['L1 Points'] = df['Level 1s'].clip(upper=4) * 10
    
    # L2 (base + additional)
    df['L2 Points'] = (df['Level 2s'] + df['Add. Level 2s']).clip(upper=2) * 20
    
    # L3
    df['L3 Points'] = df['Level 3s'].clip(upper=2) * 30

    df_edu_points = compute_award_points(df_edu)

    # COT Training Rounds
    df['COT R1 Points'] = df['Off. Trained Round 1'].apply(lambda x: 20 if x >= 7 else 0)
    df['COT R2 Points'] = df['Off. Trained Round 2'].apply(lambda x: 20 if x >= 7 else 0)

    df = df.merge(df_edu_points, left_on="Club Name", right_on="Club Name", how="left").fillna(0)

    return df

def calculate_contest_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns one row per club with four contest scores as columns.
    Score = 10 if contest date is entered, else 0.
    """

    COL_CLUB = "Select Your Club"
    date_cols = {
        "Humorous Contest": "Date the Humorous Speech Contest was held",
        "TableTopics Contest": "Date the Table Topics Contest was held",
        "Evaluation Contest": "Date the Evaluation Contest was held",
        "International Contest": "Date the International Speech Contest was held",
    }

    # Handle empty input → return empty with expected columns
    if df.empty:
        return pd.DataFrame(
            columns=["Club Name"] + list(date_cols.keys())
        )

    # Clean club names
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    # Start with club column
    scores = pd.DataFrame()
    scores["Club Name"] = df[COL_CLUB].unique()

    # For each contest, compute max score
    for contest, col in date_cols.items():
        scores_contest = (
            df.groupby(COL_CLUB)[col]
              .apply(lambda x: 10 if x.notna().any() and (x.astype(str).str.strip() != "").any() else 0)
              .reset_index(name=contest)
        )
        scores = scores.merge(scores_contest, left_on="Club Name", right_on=COL_CLUB).drop(columns=[COL_CLUB])

    return scores


def assign_grouping(df: pd.DataFrame) -> pd.DataFrame:
    # Define group by active members
    def get_group(members):
        if members <= 16:
            return 'Group 1'
        elif 17 <= members <= 24:
            return 'Group 2'
        elif 25 <= members <= 40:
            return 'Group 3'
        elif members >= 41:
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

    df['Club Group'] = df['Group'].map(lambda g: group_meta[g]['Name'])
    df['Group Description'] = df['Group'].map(lambda g: group_meta[g]['Description'])

    # Rank within group
    # df = df.sort_values(['Group', 'Total Club Points'], ascending=[True, False])
    # df['Group Rank'] = df.groupby('Group')['Total Club Points'].rank(method='dense', ascending=False).astype(int)

    return df

def mot_scores(df: pd.DataFrame) -> pd.DataFrame:
    COL_CLUB = "Select Your Club"
    COL_DATE = "Date the MOT session was conducted"

    # If input is empty → return empty with expected columns
    if df.empty:
        return pd.DataFrame(columns=["Club Name", "MOT_Q1", "MOT_Q3"])
    
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()
    # convert to datetime (dayfirst since it's dd/mm/yyyy)
    mot_dates = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce").dt.date

    q1_start, q1_end = date(2025, 7, 1), date(2025, 12, 31)
    q2_start, q2_end = date(2026, 1, 1), date(2026, 6, 30)

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "MOT_Q1": ((mot_dates >= q1_start) & (mot_dates <= q1_end)).astype(int) * 15,
        "MOT_Q3": ((mot_dates >= q2_start) & (mot_dates <= q2_end)).astype(int) * 15
    })

    return df_out.groupby("Club Name", as_index=False).max()

def pathways_completion_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Pathways_Completion_Celebration
    - 10 points if the club is listed (i.e., participated)
    """

    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Pathways_Completion_Celebration": 10
    })

    return df_out.groupby("Club Name", as_index=False).max()

def mentorship_programme_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Mentorship_Programme
    - 10 points if the club is listed (i.e., participated)
    """

    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Mentorship_Programme": 10
    })

    return df_out.groupby("Club Name", as_index=False).max()

def distinguished_club_partners_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Distinguished_Club_Partners
    - 50 points if the club is listed (i.e., helped another club become distinguished)
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Distinguished_Club_Partners": 50
    })

    return df_out.groupby("Club Name", as_index=False).max()

def successful_handover_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Successful_Transition_Handover
    - 20 points if the club is listed (i.e., submitted handover report)
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Successful_Transition_Handover": 20
    })

    return df_out.groupby("Club Name", as_index=False).max()

def quality_initiatives_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Quality_Initiatives
    - 15 points if the club submitted a unique quality initiative (e.g., Speakathon, themed meeting)
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Quality_Initiatives": 15
    })

    return df_out.groupby("Club Name", as_index=False).max()

def member_onboarding_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Member_Onboarding
    - 10 points if the club reported having a member onboarding program
    """
    COL_CLUB = "Select Your Club"

    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Name": df[COL_CLUB],
        "Member_Onboarding": 10
    })

    return df_out.groupby("Club Name", as_index=False).max()
