import matplotlib.pyplot as plt
import pandas as pd

def run(df: pd.DataFrame, column: str, bins: int):
    fig, ax = plt.subplots()
    ax.hist(df[column], bins=bins)
    ax.set_title(f"Histogram of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    return fig
