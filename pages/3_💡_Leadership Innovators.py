import streamlit as st
from utils.helpers import load_data_club_performance, prepare_leadership_innovators_data
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

st.markdown("<h2 style='text-align: center;'> 💡 Leadership Innovators – Detailed Breakdown</h2>", unsafe_allow_html=True)

# ------------------ Load and Prepare Data ------------------ #
df_club_performance, update_date = load_data_club_performance()

df_leadership_innovators = prepare_leadership_innovators_data(df_club_performance)

# ------------------ Display ------------------ #
# Extract date from filename
st.caption(f"📅 Last Updated: {update_date}")
st.dataframe(df_leadership_innovators, use_container_width=True, hide_index=True)

st.markdown("⬅️ Use the left sidebar to return to the leaderboard.")
