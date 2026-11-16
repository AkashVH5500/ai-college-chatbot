import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

st.set_page_config(page_title="College Chatbot - Admin", layout="wide")
st.title("Admin Dashboard - FAQ Manager")

if not ADMIN_PASSWORD:
    st.error("Set ADMIN_PASSWORD in your local .env file before launching the admin interface.")
    st.stop()

password = st.text_input("Admin password", type="password")
if password != ADMIN_PASSWORD:
    st.warning("Enter the configured admin password to continue.")
    st.stop()

st.success("Authenticated for this local demo.")
st.caption("This password check is intended for local development only; it is not production authentication.")

try:
    response = requests.get(f"{BACKEND_URL}/faqs", timeout=10)
    response.raise_for_status()
    faqs = response.json()
except requests.RequestException as exc:
    st.error(f"Could not load FAQs: {exc}")
    st.stop()

st.header("Existing FAQs")
if not faqs:
    st.info("No FAQs are available yet.")

for faq in faqs:
    with st.expander(f"#{faq['id']} - {faq['question'][:80]}"):
        new_question = st.text_input(
            "Question",
            value=faq["question"],
            key=f"question-{faq['id']}",
        )
        new_answer = st.text_area(
            "Answer",
            value=faq["answer"],
            key=f"answer-{faq['id']}",
        )

        col_update, col_delete = st.columns(2)
        with col_update:
            if st.button("Save changes", key=f"save-{faq['id']}"):
                try:
                    updated = requests.put(
                        f"{BACKEND_URL}/faqs/{faq['id']}",
                        json={"question": new_question, "answer": new_answer},
                        timeout=20,
                    )
                    updated.raise_for_status()
                    st.success("FAQ updated.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Update failed: {exc}")

        with col_delete:
            if st.button("Delete FAQ", key=f"delete-{faq['id']}"):
                try:
                    deleted = requests.delete(
                        f"{BACKEND_URL}/faqs/{faq['id']}",
                        timeout=20,
                    )
                    deleted.raise_for_status()
                    st.success("FAQ deleted.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Delete failed: {exc}")

st.divider()
st.header("Add FAQ")
with st.form("add-faq"):
    question = st.text_input("Question")
    answer = st.text_area("Answer")
    submitted = st.form_submit_button("Add FAQ")

if submitted:
    if not question.strip() or not answer.strip():
        st.error("Both question and answer are required.")
    else:
        try:
            added = requests.post(
                f"{BACKEND_URL}/faqs",
                json={"question": question, "answer": answer},
                timeout=20,
            )
            added.raise_for_status()
            st.success("FAQ added.")
            st.rerun()
        except requests.RequestException as exc:
            st.error(f"Could not add FAQ: {exc}")
