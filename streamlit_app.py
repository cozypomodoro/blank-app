import streamlit as st
import pandas as pd
import importlib
import pkgutil
import inspect
import time
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# -------------------------------------------------
# FUNCTION LOADER (RELOAD SAFE)
# -------------------------------------------------
def load_analysis_functions(force_reload=False):
    functions = {}
    package_name = "analysis_functions"

    if force_reload and package_name in list(importlib.sys.modules.keys()):
        for mod in list(importlib.sys.modules.keys()):
            if mod.startswith(package_name):
                del importlib.sys.modules[mod]

    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_name)

        funcs = [
            obj for _, obj in inspect.getmembers(module)
            if inspect.isfunction(obj)
        ]

        if len(funcs) == 1:
            functions[module_name] = funcs[0]

    return functions


# -------------------------------------------------
# STATE
# -------------------------------------------------
if "workflow" not in st.session_state:
    st.session_state.workflow = []

if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0


# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🔬 No-Code Data Analysis Platform")

if st.button("🔄 Refresh analysis tools"):
    st.session_state.refresh_key += 1


analysis_funcs = load_analysis_functions(
    force_reload=True
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
# TOOL PALETTE (BUTTON GRID)
# -------------------------------------------------
st.markdown("---")
st.header("➕ Add Analysis Step")

cols = st.columns(3)

for idx, (name, func) in enumerate(analysis_funcs.items()):
    with cols[idx % 3]:
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

    # INPUT CONFIG
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

    # RUN
    if st.button(f"▶ Run Step {i+1}", key=f"run_{i}"):
        try:
            block["output"] = func(**block["inputs"])
        except Exception as e:
            block["output"] = f"❌ Error: {e}"

    # OUTPUT
    if block["output"] is not None:
        st.write("### Output")
        if isinstance(block["output"], plt.Figure):
            st.pyplot(block["output"])
        else:
            st.write(block["output"])

    st.markdown("---")




