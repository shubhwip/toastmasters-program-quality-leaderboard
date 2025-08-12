import streamlit as st
import pandas as pd
from utils.metrics import calculate_points, assign_grouping

st.set_page_config(
    page_title="District 91 Leaderboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ HEADER ------------------ #
col1, col2 = st.columns([1, 5])
with col1:
    st.image("data/logo.jpg", width=100)
with col2:
    st.markdown("## 🏆 District 91 Leaderboard")
    st.caption("Tracking club excellence across size and progress tiers.")

# ------------------ LOAD DATA FROM GOOGLE DRIVE ------------------ #
@st.cache_data
def load_and_process():
    file_id = st.secrets["GOOGLE_DRIVE_FILE_ID"]
    gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    df = pd.read_csv(gsheet_url)
    df = calculate_points(df)
    df = assign_grouping(df)
    return df

df = load_and_process()
df = df[df['Group'] != 'Unknown']  # Remove Unknown

# ------------------ GROUP METADATA ------------------ #
group_meta = {
    'Group 1': {'Name': 'Spark Clubs', 'Description': 'Clubs with fewer than 12 members. Small but full of potential.'},
    'Group 2': {'Name': 'Rising Stars', 'Description': 'Clubs with 12–20 members. Gaining traction and energy.'},
    'Group 3': {'Name': 'Powerhouse Clubs', 'Description': 'Clubs with 21–40 members. Thriving on teamwork.'},
    'Group 4': {'Name': 'Pinnacle Clubs', 'Description': 'Clubs with 41–100 members. Large and vibrant.'}
}

# ------------------ SELECT GROUP ------------------ #
selected_group_key = st.radio(
    "📌 Select Club Group",
    options=list(group_meta.keys()),
    format_func=lambda g: group_meta[g]['Name'],
    horizontal=True
)

group_name = group_meta[selected_group_key]['Name']
group_desc = group_meta[selected_group_key]['Description']

st.markdown(f"### {group_name}")
st.caption(f"_{group_desc}_")

# ------------------ PREPARE CLUB DATA ------------------ #
filtered = df[df['Group'] == selected_group_key].copy()

# Add tier points
filtered['Pathways Pioneers'] = (
    filtered[['L1 Points', 'L2 Points', 'L3 Points', 'L4 Points', 'L5 Points',
              'COT R1 Points', 'COT R2 Points']].sum(axis=1)
)
filtered['Leadership Innovators'] = 0
filtered['Excellence Champions'] = 0

# Sort by Group Rank and Club Name
filtered = filtered.sort_values(by=['Group Rank', 'Club Name'], ascending=[True, True]).reset_index(drop=True)
filtered['Top 3'] = filtered['Group Rank'] <= 3

# ------------------ DISPLAY LEADERBOARD ------------------ #
st.markdown("### 🥇 Club Leaderboard")
st.caption("Top 3 clubs in each group (based on Group Rank) will receive special incentives 🎁")

display_cols = [
    'Club Name', 'Total Club Points', 'Group Rank', 'Active Members',
    'Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions', 'Top 3'
]

numeric_cols = [
    'Total Club Points', 'Group Rank', 'Active Members',
    'Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions'
]

filtered[numeric_cols] = filtered[numeric_cols].round(0).astype("Int64")
df_to_display = filtered[display_cols].drop(columns='Top 3')

# Highlight Top 3
def highlight_top3(row):
    return ['background-color: #fff9c4' if filtered.loc[row.name, 'Top 3'] else '' for _ in row]

styled_df = df_to_display.style.apply(highlight_top3, axis=1)
st.dataframe(styled_df, use_container_width=True)

# ------------------ TIER DESCRIPTIONS ------------------ #
st.markdown("---")
st.markdown("### 🧱 Tier Definitions")
st.markdown("""
#### 🛤️ Pathways Pioneers
* **Focus Area**: Educational Progress  
* **Achievements**: Pathways L1–L5, DTM, Path Completion  
* **Data Source**: TI Dashboard, District Reports

#### 💡 Leadership Innovators
* **Focus Area**: Officer Training & Club Innovation  
* **Achievements**: Officer training, new initiatives, timely submissions  
* **Data Source**: Reports (coming soon)

#### 🏛️ Excellence Champions
* **Focus Area**: Club Operations & Planning  
* **Achievements**: Club operations, district events  
* **Data Source**: Reports (coming soon)
""")
