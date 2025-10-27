import streamlit as st
from utils.helpers import generate_leaderboard_excel, load_data_club_performance, prepare_pathways_pioneers_data, prepare_leadership_innovators_data, prepare_excellence_champions_data
import numpy as np
from io import BytesIO
from openpyxl import Workbook

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

st.markdown("<h2 style='text-align: center;'>🏆 Quarterly Incentives Leaderboard</h2>", unsafe_allow_html=True)
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
# st.caption(f"Tracking {incentives_tier_desc} in this incentive tier leaderboard")

# ------------------ PREPARE CLUB DATA ------------------ #


@st.cache_data
def get_merged_club_data():
    df_club_performance, update_date = load_data_club_performance()
    df_pathways_pioneers = prepare_pathways_pioneers_data(df_club_performance)
    df_leadership_innovators = prepare_leadership_innovators_data(df_club_performance)
    df_excellence_champions = prepare_excellence_champions_data(df_club_performance)
    df_merged = df_pathways_pioneers.merge(
        df_leadership_innovators[['Club Number', 'Leadership Innovators']], on='Club Number'
    ).merge(
        df_excellence_champions[['Club Number', 'Excellence Champions']], on='Club Number'
    )
    df_merged['Total Club Points'] = (
        df_merged[['Pathways Pioneers', 'Leadership Innovators', 'Excellence Champions']].sum(axis=1)
    )
    return df_merged, update_date

df_merged, update_date = get_merged_club_data()
df_filtered = df_merged[df_merged['Club Group'] == group_name].copy()

df_filtered = df_filtered.sort_values(
    by=[incentives_tier_name, 'Total Club Points', 'Club Name'],
    ascending=[False, False, True],
    kind="mergesort"
).reset_index(drop=True)

candidates = df_filtered[incentives_tier_name] > 0
df_rank = df_filtered.loc[candidates].copy()

df_rank["Group Rank"] = (
    df_rank
    .sort_values(by=[incentives_tier_name, 'Total Club Points', 'Club Name'],
                 ascending=[False, False, True], kind="mergesort")
    .rank(method="min", ascending=False, 
          numeric_only=False, axis=0,
          na_option='bottom',
          pct=False)
    [incentives_tier_name]
)  

df_rank["_key"] = list(zip(df_rank[incentives_tier_name], df_rank["Total Club Points"]))

df_rank = df_rank.sort_values(by=[incentives_tier_name, 'Total Club Points', 'Club Name'],
                              ascending=[False, False, True], kind="mergesort")

df_rank["Group Rank"] = range(1, len(df_rank) + 1)

if len(df_rank) >= 3:
    third_score = df_rank.iloc[2][incentives_tier_name]
    third_points = df_rank.iloc[2]["Total Club Points"]
    df_rank["Top 3"] = (
        (df_rank[incentives_tier_name] > third_score) |
        ((df_rank[incentives_tier_name] == third_score) &
         (df_rank["Total Club Points"] >= third_points))
    )
else:
    df_rank["Top 3"] = True

df_filtered = df_filtered.merge(
    df_rank[["Club Name", "Top 3"]],
    on="Club Name",
    how="left"
)
df_filtered["Top 3"] = df_filtered["Top 3"].fillna(False)

df_filtered[['Total Club Points', incentives_tier_name]] = df_filtered[['Total Club Points', incentives_tier_name]].astype(int)

display_cols = ['Club Name', incentives_tier_name, 'Total Club Points', 'Top 3']
df_to_display = df_filtered[display_cols].drop(columns='Top 3')

def highlight_top3(row):
    return ['background-color: rgba(255, 215, 0, 0.25);' if df_filtered.loc[row.name, 'Top 3'] else '' for _ in row]

styled_df = df_to_display.style.apply(highlight_top3, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Add this download button in your Streamlit app (place it where you want the button to appear)
leaderboard_file = generate_leaderboard_excel(df_merged, group_meta, incentives_tiers)

st.download_button(
    label="📥 Download Full Leaderboard (Excel)",
    data=leaderboard_file,
    file_name="District_91_Leaderboard.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

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