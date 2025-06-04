import pandas as pd


def load_lap_times(file_obj):
    """Load lap times from a CSV file into a DataFrame."""
    return pd.read_csv(file_obj)


def compute_deltas(df, time_col="lap_time"):
    """Compute lap time deltas relative to the fastest lap."""
    fastest = df[time_col].min()
    df = df.copy()
    df["delta"] = df[time_col] - fastest
    return df
