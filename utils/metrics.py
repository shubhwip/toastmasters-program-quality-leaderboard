import pandas as pd

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
