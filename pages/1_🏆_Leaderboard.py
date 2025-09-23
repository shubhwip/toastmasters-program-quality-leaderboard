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

st.markdown("<h2 style='text-align: center;'>🏆 Program Quality Leaderboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tracking club excellence across size and progress tiers.</p>", unsafe_allow_html=True)


# ------------------ GROUP METADATA ------------------ #
group_meta = {
    'Group 1': {'Name': 'Spark Clubs', 'Description': 'Clubs with 8-16 members. Small but full of potential.'},
    'Group 2': {'Name': 'Rising Stars', 'Description': 'Clubs with 17–24 members. Gaining traction and energy.'},
    'Group 3': {'Name': 'Powerhouse Clubs', 'Description': 'Clubs with 25–40 members. Thriving on teamwork.'},
    'Group 4': {'Name': 'Pinnacle Clubs', 'Description': 'Clubs with greater than 41 members. Large and vibrant.'}
}

incentives_tiers = {
    'Pathways Pioneers': {'Name': 'Pathways Pioneers', 'Description': 'Educational Progress.'},
    'Leadership Innovators': {'Name': 'Leadership Innovators', 'Description': 'Officer Training & Club Innovation.'},
    'Excellence Champions': {'Name': 'Excellence Champions', 'Description': 'Club Operations & Planning.'},
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

# ------------------ SELECT GROUP ------------------ #
selected_incentive_tier_key = st.radio(
    "📌 Select Incentive Tier",
    options=list(incentives_tiers.keys()),
    format_func=lambda g: incentives_tiers[g]['Name'],
    horizontal=True
)
incentives_tier_name = incentives_tiers[selected_incentive_tier_key]['Name']
incentives_tier_desc = incentives_tiers[selected_incentive_tier_key]['Description']

st.markdown(f"##### Top Clubs in {incentives_tier_name} tier in {group_name}")
st.caption(f"Tracking {incentives_tier_desc} in this incentive tier leaderboard")

# ------------------ PREPARE CLUB DATA ------------------ #


@st.cache_data
def get_merged_club_data():
    df_club_performance, update_date = load_data_club_performance()
    df_pathways_pioneers = prepare_pathways_pioneers_data(df_club_performance)
    df_leadership_innovators = prepare_leadership_innovators_data(df_club_performance)
    df_excellence_champions = prepare_excellence_champions_data(df_club_performance)
    df_merged = df_pathways_pioneers.merge(
        df_leadership_innovators[['Club Name', 'Leadership Innovators']], on='Club Name'
    ).merge(
        df_excellence_champions[['Club Name', 'Excellence Champions']], on='Club Name'
    )
    df_merged['Total Club Points'] = (
        df_merged[['Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions']].sum(axis=1)
    )
    return df_merged, update_date

df_merged, update_date = get_merged_club_data()
df_filtered = df_merged[df_merged['Club Group'] == group_name].copy()

# Sort by selected incentive tier and Club Name
df_filtered = df_filtered.sort_values(
    by=[incentives_tier_name, 'Club Name'], ascending=[False, True]
).reset_index(drop=True)

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

# Dynamically order columns: Club Name, Total Club Points, <selected tier>, <other tiers>
all_tiers = ['Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions']
other_tiers = [tier for tier in all_tiers if tier != incentives_tier_name]
display_cols = [
    'Club Name',
    'Total Club Points',
    incentives_tier_name,
    'Top 3'
]

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

#### 💡 Leadership Innovators
* **Focus Area**: Officer Training & Club Innovation  
* **Achievements**: Officer training, new initiatives, timely submissions  

#### 🏛️ Excellence Champions
* **Focus Area**: Club Operations & Planning  
* **Achievements**: Club operations, district events  
""")