import pandas as pd


def load_all():
    """Load all the data from the raw folder"""
    raw_dir = "/data/raw"
    return {
        "users": pd.read_csv(f"{raw_dir}/users.csv"),
        "items": pd.read_csv(f"{raw_dir}/items.csv"),
        "explicit": pd.read_csv(f"{raw_dir}/explicit_ratings.csv"),
        "implicit": pd.read_csv(f"{raw_dir}/implicit_ratings.csv"),
    }
