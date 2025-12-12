import streamlit as st
from analysis.graphs import line_plot, histogram
from analysis.statistics import summary_stats

def render_workflow():
    df = st.session_state.get("df")

    if df is None:
        st.warning("Please upload a dataset first.")
        return

    for i, block in enumerate(st.session_state["workflow"]):
        with st.container(border=True):
            st.subheader(f"Step {i+1}: {block['type']}")

            # ---------------------
            # INPUT PANEL
            # ---------------------
            with st.expander("Configure Inputs"):
                if block["type"] == "Line Plot":
                    x = st.selectbox("X column", df.columns, key=f"x{i}")
                    y = st.selectbox("Y column", df.columns, key=f"y{i}")
                    if st.button("Run", key=f"run{i}"):
                        block["inputs"] = {"x": x, "y": y}
                        block["output"] = line_plot(df, x, y)

                elif block["type"] == "Histogram":
                    col = st.selectbox("Column", df.columns, key=f"h{i}")
                    bins = st.number_input("Bins", 5, 200, 30, key=f"bins{i}")
                    if st.button("Run", key=f"run2{i}"):
                        block["inputs"] = {"col": col, "bins": bins}
                        block["output"] = histogram(df, col, bins)

                elif block["type"] == "Summary Stats":
                    col = st.selectbox("Column", df.columns, key=f"s{i}")
                    if st.button("Run", key=f"run3{i}"):
                        block["inputs"] = {"col": col}
                        block["output"] = summary_stats(df, col)

            # ---------------------
            # OUTPUT PANEL
            # ---------------------
            if block["output"] is not None:
                st.write("### Output:")
                st.write(block["output"])
