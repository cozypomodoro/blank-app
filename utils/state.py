import streamlit as st

def init_session():
    if "workflow" not in st.session_state:
        st.session_state["workflow"] = []
    if "df" not in st.session_state:
        st.session_state["df"] = None
