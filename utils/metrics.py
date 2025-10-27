import pandas as pd
from datetime import date, datetime
import streamlit as st

def compute_has_TC(
    df: pd.DataFrame,
    col_club: str = "Name",
    col_member: str = "Member",
    col_award: str = "Award"
) -> pd.Series:
    """
    Compute has_TC flag:
    A club gets TC if any single Member has the same prefix
    with ANY 3 consecutive level numbers (e.g., 1-2-3, 2-3-4, or 3-4-5).
    """

    # Extract prefix and numeric level (1–5)
    s = df[col_award].astype(str).str.upper().str.strip()
    extracted = s.str.extract(r"^([A-Z]+)([1-5])$")
    df["_prefix"], df["_lvl"] = extracted[0], extracted[1]

    # Convert level to int for numeric comparison
    df["_lvl"] = df["_lvl"].astype(float)

    # For each Name + Member + prefix → check if any 3 consecutive levels exist
    def has_three_consecutive(levels):
        levels = sorted(set(int(l) for l in levels if not pd.isna(l)))
        return any(
            levels[i] + 1 in levels and levels[i] + 2 in levels
            for i in range(len(levels))
        )

    tc_per_member_prefix = (
        df.dropna(subset=["_prefix", "_lvl", col_member])
          .groupby([col_club, col_member, "_prefix"])["_lvl"]
          .apply(has_three_consecutive)
          .reset_index(name="has_TC_member_prefix_full")
    )

    # A Name earns TC if any single member completes 3 consecutive levels in one prefix
    has_tc_by_name = (
        tc_per_member_prefix.groupby(col_club)["has_TC_member_prefix_full"]
                            .any()
    )

    return df[col_club].map(has_tc_by_name).fillna(False)

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

    CLUB_NUMBER = "Club Number"
    COL_AWARD = "Award"

    # Normalise awards text
    s = df[COL_AWARD].astype(str).str.upper().str.strip()

    # Row-level flags
    df["has_L4"] = s.str.endswith("4")
    df["has_L5"] = s.str.endswith("5")
    df["has_DTM"] = s.eq("DTM")
    df["has_TC"] = compute_has_TC(df)
    df["has_FF"]  = s.eq("FF")

    # Collapse to club level
    club_flags = (
        df.groupby(CLUB_NUMBER, dropna=False)[["has_L4","has_L5","has_DTM","has_TC","has_FF"]]
          .any()
          .reset_index()
    )

    # Map flags → points
    out = pd.DataFrame({
        CLUB_NUMBER: club_flags[CLUB_NUMBER],
        "L4 Points": club_flags["has_L4"].astype(int) * 40,
        "L5 Points": club_flags["has_L5"].astype(int) * 50,
        "DTM Points": club_flags["has_DTM"].astype(int) * 60,
        "TC Points":  club_flags["has_TC"].astype(int) * 60,
        "Early10_Distinguished": club_flags["has_FF"].astype(int)  * 30,
    })

    return out


def calculate_points(df: pd.DataFrame, df_edu: pd.DataFrame) -> pd.DataFrame:
    # L1
    df['L1 Points'] = df['Level 1s'] * 10
    
    # L2 (base + additional)
    df['L2 Points'] = (df['Level 2s'] + df['Add. Level 2s']) * 20
    
    # L3
    df['L3 Points'] = df['Level 3s'] * 30

    df_edu_points = compute_award_points(df_edu)

    # COT Training Rounds
    df['COT R1 Points'] = df['Off. Trained Round 1'].apply(lambda x: 20 if x >= 7 else 0)
    df['COT R2 Points'] = df['Off. Trained Round 2'].apply(lambda x: 20 if x >= 7 else 0)

    df = df.merge(df_edu_points, left_on="Club Number", right_on="Club Number", how="left").fillna(0)

    return df

def is_valid_humorous_contest(x: pd.Series) -> bool:
    """
    Returns True if the Humorous Speech Contest was held on or before 22 Oct 2025.
    """
    cutoff = datetime(2025, 10, 24)
    # Convert to datetime safely (errors='coerce' will turn invalid entries into NaT)
    dates = pd.to_datetime(x, errors='coerce', dayfirst=False)
    # Return True only if at least one valid date <= cutoff
    return (dates.notna() & (dates <= cutoff)).any()


def calculate_contest_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns one row per club with four contest scores as columns.
    Score = 10 if contest date is entered, else 0.
    """

    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"
    date_cols = {
        "Humorous Contest": "Date the Humorous Speech Contest was held",
        "TableTopics Contest": "Date the Table Topics Contest was held",
        "Evaluation Contest": "Date the Evaluation Contest was held",
        "International Contest": "Date the International Speech Contest was held",
    }

    # Handle empty input → return empty with expected columns
    if df.empty:
        return pd.DataFrame(
            columns=["Club Number"] + list(date_cols.keys())
        )

    # Clean club names
    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    # Start with club column
    scores = pd.DataFrame()
    scores[CLUB_NUMBER] = df[CLUB_NUMBER].unique()

    # For each contest, compute max score
    for contest, col in date_cols.items():
        if contest == "Humorous Contest":
            # Apply cutoff rule using the helper function
            scores_contest = (
                df.groupby(CLUB_NUMBER)[col]
                .apply(lambda x: 10 if is_valid_humorous_contest(x) else 0)
                .reset_index(name=contest)
            )
        else:
            # Default rule (any non-empty date)
            scores_contest = (
                df.groupby(CLUB_NUMBER)[col]
                .apply(lambda x: 10 if x.notna().any() and (x.astype(str).str.strip() != "").any() else 0)
                .reset_index(name=contest)
            )

        scores = scores.merge(scores_contest, left_on="Club Number", right_on=CLUB_NUMBER)

    scores["Club Number"] = scores["Club Number"].astype(int)

    return scores


def assign_grouping(df: pd.DataFrame) -> pd.DataFrame:
    # Define group by active members
    def get_group(members):
        if 8 <= members <= 16:
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

    df['Club Group'] = df['Group'].apply(lambda g: group_meta[g]['Name'] if g != 'Unknown' else None)
    df['Group Description'] = df['Group'].map(lambda g: group_meta[g]['Description'] if g != 'Unknown' else None)

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
    
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()
    # convert to datetime (dayfirst since it's dd/mm/yyyy)
    mot_dates = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce").dt.date

    q1_start, q1_end = date(2025, 7, 1), date(2025, 12, 31)
    q2_start, q2_end = date(2026, 1, 1), date(2026, 6, 30)

    df_out = pd.DataFrame({
        CLUB_NUMBER: df[CLUB_NUMBER],
        "MOT_Q1": ((mot_dates >= q1_start) & (mot_dates <= q1_end)).astype(int) * 15,
        "MOT_Q3": ((mot_dates >= q2_start) & (mot_dates <= q2_end)).astype(int) * 15
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def pathways_completion_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Pathways_Completion_Celebration
    - 10 points if the club is listed (i.e., participated)
    """

    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        CLUB_NUMBER: df[CLUB_NUMBER],
        "Pathways_Completion_Celebration": 10
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def mentorship_programme_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Mentorship_Programme
    - 10 points if the club is listed (i.e., participated)
    """

    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        CLUB_NUMBER: df[CLUB_NUMBER],
        "Mentorship_Programme": 10
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def distinguished_club_partners_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Distinguished_Club_Partners
    - 50 points if the club is listed (i.e., helped another club become distinguished)
    """
    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Number": df[CLUB_NUMBER],
        "Distinguished_Club_Partners": 50
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def successful_handover_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Successful_Transition_Handover
    - 20 points if the club is listed (i.e., submitted handover report)
    """
    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        CLUB_NUMBER: df[CLUB_NUMBER],
        "Successful_Transition_Handover": 20
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def quality_initiatives_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Quality_Initiatives
    - 15 points if the club submitted a unique quality initiative (e.g., Speakathon, themed meeting)
    """
    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        "Club Number": df[CLUB_NUMBER],
        "Quality_Initiatives": 15
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def member_onboarding_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club | Member_Onboarding
    - 10 points if the club reported having a member onboarding program
    """
    COL_CLUB = "Select Your Club"
    CLUB_NUMBER = "Club Number"

    df[CLUB_NUMBER] = df[COL_CLUB].str.split('---- ').str[-1].str.strip()
    df[COL_CLUB] = df[COL_CLUB].str.split(' ----').str[0].str.strip()

    df_out = pd.DataFrame({
        CLUB_NUMBER: df[CLUB_NUMBER],
        "Member_Onboarding": 10
    })

    df_out[CLUB_NUMBER] = df_out[CLUB_NUMBER].astype(int)

    return df_out.groupby(CLUB_NUMBER, as_index=False).max()

def pathway_enrollment_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns Club Number | 100%_Pathway_Registration
    - 10 points if all members in a club are enrolled in Pathways
    """
    
    df.columns = df.iloc[0]   # Set second row as header
    df = df[1:].reset_index(drop=True)   # Drop the old header row

    df.rename(columns={'Club ID': 'Club Number'}, inplace=True)
    CLUB_NUMBER = "Club Number"
    COL_PATHWAYS = "Is Pathways Enrolled"

    # If either column missing, return empty result
    if CLUB_NUMBER not in df.columns or COL_PATHWAYS not in df.columns:
        return pd.DataFrame(columns=[CLUB_NUMBER, "100%_Pathway_Registration"])

    # Clean
    df[CLUB_NUMBER] = df[CLUB_NUMBER].astype(str).str.strip()
    df[COL_PATHWAYS] = df[COL_PATHWAYS].astype(str).str.strip()

    # Group and score
    def all_yes(series):
        return series.str.lower().eq("yes").all()

    scores = (
        df.groupby(CLUB_NUMBER)[COL_PATHWAYS]
        .apply(all_yes)
        .reset_index(name="All_Yes")
    )

    scores["100%_Pathway_Registration"] = scores["All_Yes"].apply(lambda x: 10 if x else 0)
    scores.drop(columns="All_Yes", inplace=True)

    scores[CLUB_NUMBER] = scores[CLUB_NUMBER].astype(int)

    return scores
