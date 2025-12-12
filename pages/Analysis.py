import streamlit as st
from utils.blocks import render_workflow
from utils.state import init_session

init_session()   # ensure workflow list exists

st.title("📊 Analysis Workflow")
st.write("Add steps to build your analysis pipeline.")

# --- Add Step Menu ---
with st.expander("➕ Add Analysis Step"):
    step_type = st.selectbox("Choose step type:", 
                             ["Line Plot", "Histogram", "Summary Stats"])
    if st.button("Add Step"):
        st.session_state["workflow"].append({
            "type": step_type,
            "inputs": {},
            "output": None
        })
        st.success(f"Added: {step_type}")

# --- Render all steps ---
render_workflow()

