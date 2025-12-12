import matplotlib.pyplot as plt

def run(df, column: str, bins: int = 10):
    fig, ax = plt.subplots()
    ax.hist(df[column], bins=bins)
    ax.set_title(f"Histogram of {column}")
    return fig

