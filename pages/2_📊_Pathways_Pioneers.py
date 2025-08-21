import streamlit as st
import pandas as pd
from utils.metrics import calculate_points, assign_grouping
from utils.helpers import extract_update_date
import requests
from io import BytesIO

# ------------------ HEADER ------------------ #
st.markdown(
    """
    <style>
        [data-testid="stImage"] {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

logo_id = st.secrets["GOOGLE_DRIVE_FILE_ID_LOGO"]
logo_path = f"https://drive.google.com/uc?export=download&id={logo_id}"
response = requests.get(logo_path)
if response.status_code == 200:
    st.image(BytesIO(response.content), width=1000)
else:
    st.warning("⚠️ Logo could not be loaded.")

st.markdown("<h2 style='text-align: center;'>📊 Pathways Pioneers – Detailed Breakdown</h2>", unsafe_allow_html=True)

# ------------------ Load and Prepare Data ------------------ #
@st.cache_data
def load_data(gsheet_url=None):

    df = pd.read_csv(gsheet_url)
    df = calculate_points(df)
    df = assign_grouping(df)
    df = df[df['Group'] != 'Unknown']
    return df

file_id = st.secrets["GOOGLE_DRIVE_FILE_ID_CLUB_PERFORMANCE"]
gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
df = load_data(gsheet_url)

# ------------------ Add Pathways Score ------------------ #
df['Pathways Pioneers'] = df[['L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points',
                              'COT R1 Points', 'COT R2 Points']].sum(axis=1)

# ------------------ Create Human-Readable Group ------------------ #
group_map = {
    'Group 1': 'Spark Clubs',
    'Group 2': 'Rising Stars',
    'Group 3': 'Powerhouse Clubs',
    'Group 4': 'Pinnacle Clubs'
}
df['Club Group'] = df['Group'].map(group_map)

# ------------------ Select Columns and Format ------------------ #
columns = ['Club Name', 'Club Group', 'Active Members', 'Pathways Pioneers',
           'L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points',
           'COT R1 Points', 'COT R2 Points']

df[columns[2:]] = df[columns[2:]].round(0).astype("Int64")

# ------------------ Sort and Reset Index ------------------ #
df_sorted = df[columns].sort_values(by='Club Name').reset_index(drop=True)

# ------------------ Display ------------------ #
# Extract date from filename
update_date = extract_update_date(gsheet_url)
st.caption(f"📅 Last Updated: {update_date}")
st.dataframe(df_sorted, use_container_width=True, hide_index=True)

st.markdown("⬅️ Use the left sidebar to return to the leaderboard.")
