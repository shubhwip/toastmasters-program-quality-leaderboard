import streamlit as st
import pandas as pd
from utils.metrics import calculate_points, assign_grouping

st.set_page_config(page_title="Pathways Pioneers Breakdown", layout="wide")

st.title("📘 Pathways Pioneers – Detailed Breakdown")

# ------------------ Load and Prepare Data ------------------ #
@st.cache_data
def load_data():
    file_id = st.secrets["GOOGLE_DRIVE_FILE_ID"]
    gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    df = pd.read_csv(gsheet_url)
    df = calculate_points(df)
    df = assign_grouping(df)
    df = df[df['Group'] != 'Unknown']
    return df

df = load_data()

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
df_sorted.index = df_sorted.index + 1
df_sorted.reset_index(inplace=True)
df_sorted.rename(columns={'index': '#'}, inplace=True)

# ------------------ Display ------------------ #
st.dataframe(df_sorted.set_index('#'), use_container_width=True)

st.markdown("⬅️ Use the left sidebar to return to the leaderboard.")
