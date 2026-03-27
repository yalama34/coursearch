import pandas as pd


def load_all():
    """Load all the data from the raw folder"""
    return {
        "users": pd.read_csv("data/raw/users.csv"),
        "items": pd.read_csv("data/raw/items.csv"),
        "explicit": pd.read_csv("data/raw/explicit_ratings.csv"),
        "implicit": pd.read_csv("data/raw/implicit_ratings.csv"),
    }
