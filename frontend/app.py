# frontend/app.py
import streamlit as st
import pandas as pd
import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="E-Commerce NL→SQL Chat", layout="wide")
st.title("🧠 E-Commerce Insights — Natural Language → SQL (with memory)")

# --- Initialize conversation_id from query params or session state ---
query_params = st.query_params
if "conversation_id" in query_params:
    conv_id = query_params["conversation_id"][0]
    st.session_state.conversation_id = conv_id
elif "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
    conv_id = st.session_state.conversation_id
else:
    conv_id = st.session_state.conversation_id

# --- Sidebar ---
with st.sidebar:
    st.markdown("## Session")
    st.write(f"Conversation id: `{conv_id}`")

    if st.button("New Conversation"):
        # Generate new conversation ID
        new_id = str(uuid.uuid4())
        st.session_state.conversation_id = new_id

        # Clear other session keys if needed
        keys_to_clear = [k for k in st.session_state.keys() if k != "conversation_id"]
        for key in keys_to_clear:
            del st.session_state[key]

        # Update URL query params to trigger rerun
        st.query_params["conversation_id"] = [new_id]

    if st.button("Health Check API"):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=4)
            st.success(r.json())
        except Exception as e:
            st.error(str(e))

# --- User Input ---
query = st.text_input(
    "Ask a question about the dataset",
    value="Top 10 product categories by total sales in 2017"
)
limit = st.number_input(
    "Max rows to return (enforced)",
    value=100, step=10, min_value=1
)

# --- Run Query ---
if st.button("Run Query"):
    if not query.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Calling backend / generating SQL..."):
            try:
                payload = {
                    "prompt": query,
                    "conversation_id": conv_id,
                    "limit": int(limit)
                }
                resp = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                st.error(f"Request failed: {e}")
                st.stop()

        # --- Display SQL ---
        st.subheader("Generated SQL")
        st.code(data.get("sql", "-- no sql returned --"), language="sql")

        # --- Display Results ---
        st.subheader(f"Results ({data.get('rows_count', 0)} rows)")
        rows = data.get("result", {}).get("rows", [])
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
        else:
            st.write("No rows returned.")

        st.markdown("---")
        st.subheader("Conversation ID (use for follow-ups)")
        st.write(data.get("conversation_id"))
