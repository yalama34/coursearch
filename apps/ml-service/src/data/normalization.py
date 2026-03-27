import pandas as pd


def normalize_items(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the items dataframe"""
    return df.rename(columns={
        "item_id": "course_id",
        "Difficulty": "difficulty"
    })


def normalize_explicit(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the explicit ratings dataframe"""
    df = df.rename(columns={
        "item_id": "course_id",
        "created_at": "timestamp"
    })
    df["type"] = "explicit"
    return df


def normalize_implicit(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the implicit ratings dataframe"""
    df = df.rename(columns={
        "item_id": "course_id",
        "created_at": "timestamp"
    })
    df["type"] = "view"
    return df


def build_actions(
    explicit: pd.DataFrame, 
    implicit: pd.DataFrame
) -> pd.DataFrame:
    """Build the actions dataframe"""
    
    actions = pd.concat([explicit, implicit])

    return actions[[
        "user_id",
        "course_id",
        "type",
        "timestamp"
    ]]
