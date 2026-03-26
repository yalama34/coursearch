import pandas as pd


def clean_users(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the users dataframe"""
    df = df.drop_duplicates(subset=["user_id"])
    df["job"] = df["job"].fillna("unknown").str.lower().str.strip()
    df["job"] = df["job"].replace({"n/a": "unknown"})
    return df


def clean_items(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the items dataframe"""
    df = df.drop_duplicates(subset=["item_id"])
    df = df.dropna(subset=["name", "description"])

    df["description"] = df["description"].str.replace(r"\s+", " ", regex=True)

    df["nb_views"] = (
        df["nb_views"].astype(float).fillna(0).astype(int)
    )

    df["created_at"] = pd.to_numeric(df["created_at"], errors="coerce")

    return df


def clean_explicit(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the explicit dataframe"""
    df = df.drop_duplicates()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df


def clean_implicit(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the implicit dataframe"""
    df = df.drop_duplicates()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df
