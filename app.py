import streamlit as st
import pandas as pd
from utils.metrics import calculate_points, assign_grouping

st.set_page_config(page_title="District 91 Leaderboard", layout="wide")

# Logo
st.image("data/logo.jpg", width=120)
st.title("🏆 District 91 Leaderboard")

# Load and process data from Google Drive
@st.cache_data
def load_and_process():
    file_id = st.secrets["GOOGLE_DRIVE_FILE_ID"]
    gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    df = pd.read_csv(gsheet_url)
    df = calculate_points(df)
    df = assign_grouping(df)
    return df

df = load_and_process()

# Filter out Unknown group
df = df[df['Group'] != 'Unknown']

# Add display label for radio toggle
df['Group Display'] = df['Group'] + " – " + df['Group Name']
group_options = (
    df[['Group', 'Group Display']]
    .drop_duplicates()
    .sort_values('Group')
    .set_index('Group')['Group Display']
    .to_dict()
)

# Use radio button for toggle
selected_group_key = st.radio(
    "Select Club Group",
    options=list(group_options.keys()),
    format_func=lambda g: group_options[g],
    horizontal=True
)

# Filter and sort
filtered = df[df['Group'] == selected_group_key].sort_values(by='Total Club Points', ascending=False)

# Group description
group_name = filtered['Group Name'].iloc[0]
group_desc = filtered['Group Description'].iloc[0]

st.subheader(f"{selected_group_key} – {group_name}")
st.caption(f"_{group_desc}_")

# Columns to show
cols = [
    'Club Name', 'Total Club Points', 'Group Rank',
    'Active Members', 'L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points',
    'COT R1 Points', 'COT R2 Points'
]

# Round all numeric columns
filtered[cols[1:]] = filtered[cols[1:]].round(0).astype(int)

# Highlight Total Club Points and Group Rank
styled_df = (
    filtered[cols]
    .reset_index(drop=True)
    .style
    .applymap(lambda val: 'background-color: #e0f7e9', subset=['Total Club Points'])
    .applymap(lambda val: 'background-color: #e6f0fa', subset=['Group Rank'])
)

# Show styled table
st.dataframe(styled_df, use_container_width=True)
