import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="College Assistant Chatbot", layout="centered")
st.title("College Assistant Chatbot")
st.write("Ask a question about college information.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Type your question and press Enter")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": question},
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "The server returned no answer.")
        matches = data.get("top_faqs", [])
    except requests.RequestException as exc:
        answer = f"Could not contact the chatbot service: {exc}"
        matches = []

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
        if matches:
            with st.expander("Related FAQ entries"):
                for item in matches:
                    st.markdown(f"**{item['question']}**")
                    st.write(item["answer"])
