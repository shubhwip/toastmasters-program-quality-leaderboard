import streamlit as st
from utils.helpers import extract_update_date, load_data_club_performance, prepare_pathways_pioneers_data, prepare_leadership_innovators_data, prepare_excellence_champions_data
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

st.markdown("<h2 style='text-align: center;'>🏆 Program Quality Leaderboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tracking club excellence across size and progress tiers.</p>", unsafe_allow_html=True)


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

df_club_performance, update_date = load_data_club_performance()

df_pathways_pioneers = prepare_pathways_pioneers_data(df_club_performance)
df_leadership_innovators = prepare_leadership_innovators_data(df_club_performance)
df_excellence_champions = prepare_excellence_champions_data(df_club_performance)

df_filtered = df_pathways_pioneers[df_pathways_pioneers['Club Group'] == group_name].copy()

df_filtered = df_filtered.merge(
    df_leadership_innovators[['Club Name', 'Leadership Innovators']])
df_filtered = df_filtered.merge(
    df_excellence_champions[['Club Name', 'Excellence Champions']])

df_filtered['Total Club Points'] = (
        df_filtered[['Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions']].sum(axis=1)
    )

# Sort by Total Points and Club Name
df_filtered = df_filtered.sort_values(by=['Total Club Points', 'Club Name'], ascending=[False, True]).reset_index(drop=True)

# Add rank and mark top 3
df_filtered['Group Rank'] = df_filtered.index + 1
df_filtered['Top 3'] = df_filtered['Group Rank'] <= 3
# Convert numeric columns to integers
numeric_cols = ['Total Club Points', 'Group Rank', 'Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions']
df_filtered[numeric_cols] = df_filtered[numeric_cols].astype(int)

# ------------------ DISPLAY LEADERBOARD ------------------ #
st.markdown("### 🥇 Leaderboard")
st.caption("Top 3 clubs in each group (based on Group Rank) will receive special incentives 🎁")

# Extract date from filename
st.caption(f"📅 Last Updated: {update_date}")

display_cols = [
    'Club Name', 'Total Club Points', 
    'Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions', 'Top 3'
]

numeric_cols = [
    'Total Club Points', 'Group Rank', 'Active Members',
    'Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions'
]

# filtered[numeric_cols] = filtered[numeric_cols].round(0).astype("Int64")
df_to_display = df_filtered[display_cols].drop(columns='Top 3')

# Highlight Top 3
def highlight_top3(row):
    return ['background-color: #fff9c4' if df_filtered.loc[row.name, 'Top 3'] else '' for _ in row]

styled_df = df_to_display.style.apply(highlight_top3, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True)

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