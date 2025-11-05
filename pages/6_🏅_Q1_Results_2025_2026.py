import streamlit as st
from utils.helpers import load_incentive_winners
import pandas as pd

# ------------------ STYLING (Theme-adaptive) ------------------ #
st.markdown(
    """
    <style>
        .pillar-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 280px;
        }
        .pillar-card {
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            background-color: var(--background-color);
            border: 2px solid var(--secondary-background-color);
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .pillar-icon {
            font-size: 80px;
            margin-bottom: 15px;
            line-height: 1;
        }
        .pillar-title {
            font-size: 22px;
            font-weight: bold;
            margin: 10px 0 5px 0;
            line-height: 1.2;
            min-height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .pillar-subtitle {
            font-size: 14px;
            opacity: 0.7;
            margin-top: 5px;
        }
        /* Reduce spacing after title */
        div[data-testid="stHorizontalBlock"] {
            margin-top: 1rem !important;
        }
        .modal-icon {
            font-size: 60px;
            text-align: center;
            margin-bottom: 10px;
        }
        .modal-group-name {
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            margin: 10px 0 20px 0;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown("# 🏅 Q1 Incentive Winners")

# ------------------ Load Data ------------------ #
df_q1_results = load_incentive_winners(secret_key="D91_Q1_INCENTIVE_WINNERS")

if df_q1_results.empty:
    st.error("No data available")
    st.stop()

# ------------------ Modal Dialog Functions ------------------ #
@st.dialog("Winners", width="large")
def show_winners_modal(group_name, group_icon, group_df):
    # Display icon and group name (both centered)
    st.markdown(f'<div class="modal-icon">{group_icon}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="modal-group-name">{group_name}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sort by tier points descending
    group_df = group_df.sort_values('Tier Points', ascending=False)
    
    # Get unique tiers
    tiers = group_df['Incentive Tiers'].unique()
    
    for tier in tiers:
        tier_winners = group_df[group_df['Incentive Tiers'] == tier]
        
        # Tier emoji
        tier_lower = str(tier).lower()
        if 'gold' in tier_lower or 'platinum' in tier_lower:
            tier_emoji = "🥇"
        elif 'silver' in tier_lower:
            tier_emoji = "🥈"
        elif 'bronze' in tier_lower:
            tier_emoji = "🥉"
        else:
            tier_emoji = "🏅"
        
        st.markdown(f"### {tier_emoji} {tier}")
        
        # Display winners as simple list
        for _, winner in tier_winners.iterrows():
            st.markdown(f"**{winner['Club Name']}**")
        
        st.markdown("")  # Spacing between tiers

# ------------------ Display Pillars ------------------ #
club_groups = sorted(df_q1_results['Club Group'].unique())

# Icons for each group
icons = ["🏛️", "🏢", "⭐", "💎", "🎯", "🚀", "🌟", "🌐"]

# Add small spacing before pillars
st.markdown("<br>", unsafe_allow_html=True)

# Create columns for pillars
cols = st.columns(len(club_groups))

for idx, group in enumerate(club_groups):
    group_df = df_q1_results[df_q1_results['Club Group'] == group]
    num_winners = len(group_df)
    group_icon = icons[idx % len(icons)]
    
    with cols[idx]:
        st.markdown('<div class="pillar-container">', unsafe_allow_html=True)
        
        # Display pillar card
        st.markdown(
            f"""
            <div class="pillar-card">
                <div class="pillar-icon">{group_icon}</div>
                <div class="pillar-title">{group}</div>
                <div class="pillar-subtitle">{num_winners} Winners</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Button to open modal (pass icon to modal)
        st.button(f"View Winners", key=f"btn_{group}", use_container_width=True, 
                 on_click=show_winners_modal, args=(group, group_icon, group_df))
        
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Footer ------------------ #
st.markdown("---")
st.caption("⬅️ Use the left sidebar to return to the leaderboard")