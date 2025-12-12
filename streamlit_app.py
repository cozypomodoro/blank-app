import streamlit as st
import pandas as pd
import importlib
import pkgutil
import inspect
import os
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# -------------------------------------------------------------
# LOAD ANALYSIS FUNCTIONS FROM analysis_functions/ FOLDER
# -------------------------------------------------------------
def load_analysis_functions():
    functions = {}
    package_name = "analysis_functions"

    # Dynamically import everything in the folder
    package = importlib.import_module(package_name)

    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package_name + "."):
        module = importlib.import_module(module_name)

        # Expect each file to contain ONE function
        file_functions = [
            obj for name, obj in inspect.getmembers(module)
            if inspect.isfunction(obj)
        ]

        if len(file_functions) == 1:
            func = file_functions[0]
            label = module_name.split(".")[-1]   # filename = label
            functions[label] = func

        else:
            print(f"⚠ WARNING: {module_name} should contain exactly ONE function.")

    return functions


analysis_funcs = load_analysis_functions()


# -------------------------------------------------------------
# STATE SETUP
# -------------------------------------------------------------
if "workflow" not in st.session_state:
    st.session_state.workflow = []


# Each workflow block:
# {
#   "label": string,
#   "func": pointer to function,
#   "inputs": {},
#   "output": any
# }


# -------------------------------------------------------------
# FILE UPLOADER
# -------------------------------------------------------------
st.title("🔬 No-Code Data Analysis Platform")

uploaded = st.file_uploader("Upload CSV to begin", type=["csv"])

if not uploaded:
    st.stop()

df = pd.read_csv(uploaded)

st.subheader("Data Preview")
st.dataframe(df)


# -------------------------------------------------------------
# ADD BLOCK UI
# -------------------------------------------------------------
st.markdown("---")
st.header("➕ Add Analysis Step")

choices = ["<select>"] + list(analysis_funcs.keys())
selected = st.selectbox("Choose a function to add", choices)

if st.button("Add Step"):
    if selected != "<select>":
        st.session_state.workflow.append({
            "label": selected,
            "func": analysis_funcs[selected],
            "inputs": {},
            "output": None
        })


# -------------------------------------------------------------
# WORKFLOW RENDERING
# -------------------------------------------------------------
st.markdown("---")
st.header("🧪 Workflow")

for i, block in enumerate(st.session_state.workflow):

    st.subheader(f"Step {i+1}: {block['label']}")
    func = block["func"]

    # -----------------------------
    # INPUT CONFIGURATION
    # -----------------------------
    with st.expander("Configure Inputs"):

        sig = inspect.signature(func)
        new_inputs = {}

        for param_name, param in sig.parameters.items():

            # DataFrame automatically injected
            if param.annotation == pd.DataFrame or param_name == "df":
                new_inputs[param_name] = df
                st.write(f"`{param_name}` automatically set to DataFrame.")

            # Column selector for strings
            elif param.annotation == str:
                new_inputs[param_name] = st.selectbox(f"{param_name}", df.columns)

            # Integer
            elif param.annotation == int:
                new_inputs[param_name] = st.number_input(f"{param_name}", step=1, value=1)

            # Float
            elif param.annotation == float:
                new_inputs[param_name] = st.number_input(f"{param_name}", step=0.1, value=1.0)

            else:
                new_inputs[param_name] = st.text_input(f"{param_name}")

        block["inputs"] = new_inputs

    # -----------------------------
    # RUN BUTTON
    # -----------------------------
    if st.button(f"Run Step {i+1}", key=f"run_{i}"):

        try:
            result = func(**block["inputs"])
            block["output"] = result

        except Exception as e:
            block["output"] = f"❌ Error: {e}"

    # -----------------------------
    # OUTPUT DISPLAY
    # -----------------------------
    if block["output"] is not None:
        st.write("### Output:")

        if isinstance(block["output"], plt.Figure):
            st.pyplot(block["output"])
        else:
            st.write(block["output"])

    st.markdown("---")



