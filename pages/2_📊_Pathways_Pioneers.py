import streamlit as st
from utils.helpers import load_data_club_performance, prepare_pathways_pioneers_data

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

st.markdown("<h2 style='text-align: center;'>📊 Pathways Pioneers – Detailed Breakdown</h2>", unsafe_allow_html=True)

df_club_performance, update_date = load_data_club_performance()

df_pathways_pioneers = prepare_pathways_pioneers_data(df_club_performance)

# ------------------ Display ------------------ #
# Extract date from filename

st.caption(f"📅 Last Updated: {update_date}")
st.dataframe(df_pathways_pioneers, use_container_width=True, hide_index=True)

st.markdown("⬅️ Use the left sidebar to return to the leaderboard.")
