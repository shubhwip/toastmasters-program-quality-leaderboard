# pages/2_chat.py
import streamlit as st
from utils.llm_chat import get_chat_response
import time
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

st.markdown("<h2 style='text-align: center;'>💬 Ask the Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Get help about scoring, club groups, or terminology.</p>", unsafe_allow_html=True)

# Custom CSS to fix chat at bottom
st.markdown("""
    <style>
    .chat-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #fff;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
        padding: 20px 0 10px 0;
        z-index: 100;
    }
    .chat-history {
        max-height: 300px;
        overflow-y: auto;
        margin-bottom: 80px;
    }
    .chat-input-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #fff;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
        padding: 10px 0 10px 0;
        z-index: 100;
    }
    .block-container {
        padding-bottom: 80px !important;
    }
    </style>
""", unsafe_allow_html=True)

# st.markdown("### 🤖 Ask the Assistant")
# st.caption("Get help about scoring, club groups, or terminology.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_input_popup" not in st.session_state:
    st.session_state["chat_input_popup"] = ""

# Display chat history above the input
st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for entry in st.session_state.chat_history:
    sender = "🧑‍💼 You" if entry["sender"] == "user" else "🤖 Assistant"
    bubble_color = "#e0f7fa" if entry["sender"] == "user" else "#f1f1f1"
    st.markdown(
        f"""
        <div style="background-color:{bubble_color}; padding:10px; border-radius:10px; margin-bottom:5px;">
            <strong>{sender}</strong> <span style="float:right; font-size:12px; color:#888;">{entry['timestamp']}</span>
            <br>{entry['message']}
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

def submit_chat():
    user_input = st.session_state["chat_input_popup"]
    if user_input:
        st.session_state.chat_history.append({
            "sender": "user",
            "message": user_input,
            "timestamp": time.strftime("%H:%M")
        })
        response = get_chat_response(user_input)
        st.session_state.chat_history.append({
            "sender": "bot",
            "message": response,
            "timestamp": time.strftime("%H:%M")
        })
        st.session_state["chat_input_popup"] = ""  # Clear input on next rerun

# Create a placeholder for the fixed chat input bar
chat_input_placeholder = st.empty()
with chat_input_placeholder.container():
    st.markdown('<div class="chat-input-bar">', unsafe_allow_html=True)
    with st.form(key="chat_form"):
        st.text_input("Type your question:", key="chat_input_popup")
        send = st.form_submit_button("Send", on_click=submit_chat)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("⬅️ Use the left sidebar to return to the leaderboard.")