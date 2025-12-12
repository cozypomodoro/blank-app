import streamlit as st
import pandas as pd
import importlib
import inspect
import os
import sys
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# -------------------------------------------------
# FORCE PYTHON TO SEE analysis_functions
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis_functions")

if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# -------------------------------------------------
# LOAD ANALYSIS FUNCTIONS (ROBUST)
# -------------------------------------------------
def load_analysis_functions():
    functions = {}

    if not os.path.exists(ANALYSIS_DIR):
        return functions

    for file in os.listdir(ANALYSIS_DIR):
        if not file.endswith(".py"):
            continue
        if file == "__init__.py":
            continue

        module_name = file[:-3]
        full_module = f"analysis_functions.{module_name}"

        try:
            if full_module in sys.modules:
                del sys.modules[full_module]

            module = importlib.import_module(full_module)
            importlib.reload(module)

            funcs = [
                obj for _, obj in inspect.getmembers(module)
                if inspect.isfunction(obj)
            ]

            if len(funcs) == 1:
                functions[module_name] = funcs[0]

        except Exception as e:
            st.warning(f"Failed to load {file}: {e}")

    return functions


# -------------------------------------------------
# STATE
# -------------------------------------------------
if "workflow" not in st.session_state:
    st.session_state.workflow = []


# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🔬 No-Code Data Analysis Platform")

analysis_funcs = load_analysis_functions()

if not analysis_funcs:
    st.warning(
        "No analysis functions found.\n\n"
        "Make sure:\n"
        "• analysis_functions/__init__.py exists\n"
        "• Each .py file has EXACTLY ONE function\n"
        "• You restarted Streamlit after adding files"
    )


# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
uploaded = st.file_uploader("Upload CSV", type=["csv"])

if not uploaded:
    st.stop()

df = pd.read_csv(uploaded)
st.subheader("Data Preview")
st.dataframe(df)


# -------------------------------------------------
# ADD STEP (BUTTON GRID)
# -------------------------------------------------
st.markdown("---")
st.header("➕ Add Analysis Step")

cols = st.columns(3)

for i, (name, func) in enumerate(analysis_funcs.items()):
    with cols[i % 3]:
        if st.button(name.replace("_", " ").title()):
            st.session_state.workflow.append({
                "label": name,
                "func": func,
                "inputs": {},
                "output": None
            })


# -------------------------------------------------
# WORKFLOW
# -------------------------------------------------
st.markdown("---")
st.header("🧪 Workflow")

for i, block in enumerate(st.session_state.workflow):

    st.subheader(f"Step {i+1}: {block['label'].replace('_',' ').title()}")
    func = block["func"]

    with st.expander("Configure Inputs"):
        sig = inspect.signature(func)
        inputs = {}

        for param_name, param in sig.parameters.items():

            if param_name == "df":
                inputs[param_name] = df
                st.write("Dataset automatically provided.")

            elif param.annotation == str:
                inputs[param_name] = st.selectbox(
                    param_name, df.columns, key=f"{i}_{param_name}"
                )

            elif param.annotation == int:
                inputs[param_name] = st.number_input(
                    param_name, value=10, step=1, key=f"{i}_{param_name}"
                )

            elif param.annotation == float:
                inputs[param_name] = st.number_input(
                    param_name, value=1.0, step=0.1, key=f"{i}_{param_name}"
                )

            else:
                inputs[param_name] = st.text_input(
                    param_name, key=f"{i}_{param_name}"
                )

        block["inputs"] = inputs

    if st.button(f"▶ Run Step {i+1}", key=f"run_{i}"):
        try:
            block["output"] = func(**block["inputs"])
        except Exception as e:
            block["output"] = f"❌ Error: {e}"

    if block["output"] is not None:
        st.write("### Output")
        if isinstance(block["output"], plt.Figure):
            st.pyplot(block["output"])
        else:
            st.write(block["output"])

    st.markdown("---")





