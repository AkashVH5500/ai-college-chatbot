# client_app.py
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="College Chatbot - Student", layout="centered")
st.title("🎓 College Assistant Chatbot")
st.markdown("Ask any college-related question — press Enter to send.")
st.divider()

# --------------------------------
# Session State for Chat History
# --------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------
# Handle User Input
# --------------------------------
user_input = st.chat_input("Type your question here...")

if user_input:
    # Display user message instantly
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --------------------------------
    # Send Request to Backend
    # --------------------------------
    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": user_input},
            timeout=30,
        )
        resp.raise_for_status()

        data = resp.json()

        # Correct keys:
        bot_reply = data.get("answer", "No reply from server.")
        matches = data.get("top_faqs", [])

    except Exception as e:
        bot_reply = f"❌ Error contacting server: {e}"
        matches = []

    # --------------------------------
    # Show bot message
    # --------------------------------
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --------------------------------
    # Suggested FAQ Buttons
    # --------------------------------
    if matches:
        st.markdown("### 🔍 Suggested related questions:")

        for i, m in enumerate(matches):
            q = m["question"]

            if st.button(f"❓ {q}", key=f"suggest_btn_{i}"):
                # Add selected FAQ question to chat and refresh
                st.session_state.messages.append({"role": "user", "content": q})
                st.experimental_rerun()
