# admin_app.py
import os
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="College Chatbot - Admin", layout="wide")
st.title("🛠 Admin Dashboard – FAQ Manager")

# Simple password auth (developer/admin only)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # change in env!

password = st.text_input("Enter admin password", type="password")
if password != ADMIN_PASSWORD:
    st.warning("Enter correct admin password to continue.")
    st.stop()

st.success("Authenticated as admin.")

st.divider()
st.header("📚 FAQ List")

# Fetch FAQs
try:
    resp = requests.get(f"{BACKEND_URL}/faqs", timeout=10)
    resp.raise_for_status()
    faqs = resp.json()
except Exception as e:
    st.error(f"Error loading FAQs from server: {e}")
    st.stop()

# Display FAQs in table
if faqs:
    for faq in faqs:
        with st.expander(f"#{faq['id']} – {faq['question'][:80]}"):
            st.write("**Question:**", faq["question"])
            st.write("**Answer:**", faq["answer"])

            col1, col2 = st.columns(2)

            # Edit form
            with col1:
                st.subheader("Edit FAQ")
                new_q = st.text_input(
                    f"Edit Question (ID {faq['id']})",
                    value=faq["question"],
                    key=f"edit_q_{faq['id']}",
                )
                new_a = st.text_area(
                    f"Edit Answer (ID {faq['id']})",
                    value=faq["answer"],
                    key=f"edit_a_{faq['id']}",
                )
                if st.button(f"💾 Save (ID {faq['id']})", key=f"save_{faq['id']}"):
                    try:
                        up_resp = requests.put(
                            f"{BACKEND_URL}/faqs/{faq['id']}",
                            json={"question": new_q, "answer": new_a},
                            timeout=10,
                        )
                        up_resp.raise_for_status()
                        st.success("FAQ updated.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

            # Delete button
            with col2:
                st.subheader("Delete FAQ")
                if st.button(f"🗑 Delete (ID {faq['id']})", key=f"delete_{faq['id']}"):
                    try:
                        del_resp = requests.delete(
                            f"{BACKEND_URL}/faqs/{faq['id']}", timeout=10
                        )
                        del_resp.raise_for_status()
                        st.success("FAQ deleted.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
else:
    st.info("No FAQs available yet.")

st.divider()
st.header("➕ Add New FAQ")

with st.form("add_faq_form"):
    q_new = st.text_input("Question")
    a_new = st.text_area("Answer")
    submitted = st.form_submit_button("Add FAQ")

    if submitted:
        if not q_new.strip() or not a_new.strip():
            st.error("Question and Answer cannot be empty.")
        else:
            try:
                add_resp = requests.post(
                    f"{BACKEND_URL}/faqs",
                    json={"question": q_new, "answer": a_new},
                    timeout=10,
                )
                add_resp.raise_for_status()
                st.success("FAQ added successfully.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to add FAQ: {e}")
