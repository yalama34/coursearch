from typing import Any


import ast

import pandas as pd


def parse_list(x: str) -> list:
    """Parse a string to a list"""
    try:
        return ast.literal_eval(x)
    except:
        return []


def extract_tags(df: pd.DataFrame) -> pd.DataFrame:
    """Extract the tags from the dataframe"""
    for col in ["Job", "Software", "Theme"]:
        df[col] = df[col].apply(parse_list)

    def collect(row: pd.Series) -> list:
        """Collect the tags from the row"""
        tags = []

        tags += row["Job"]
        tags += row["Software"]
        tags += row["Theme"]

        if row["language"]:
            tags.append(row["language"])

        if row["type"]:
            tags.append(row["type"])

        return list(set([t.lower().strip() for t in tags]))

    df["tags"] = df.apply(collect, axis=1)

    return df


def build_tags(
    items_df: pd.DataFrame, 
    users_df: pd.DataFrame
) -> tuple[pd.DataFrame, dict]:
    """Build the tags dataframe"""

    all_tags = set()

    for tags in items_df["tags"]:
        all_tags.update(tags)

    user_jobs = users_df["job"].dropna().unique()
    all_tags.update([j.lower().strip() for j in user_jobs if j != "unknown"])

    tags_df = pd.DataFrame({"name": list(all_tags)})
    tags_df["tag_id"] = range(1, len(tags_df) + 1)

    mapping = dict(zip(tags_df["name"], tags_df["tag_id"]))

    return tags_df, mapping


def build_course_tags(
    df: pd.DataFrame, 
    mapping: dict
) -> pd.DataFrame:
    """Build the course with tags dataframe"""

    rows = []

    for _, row in df.iterrows():
        for tag in row["tags"]:
            rows.append({
                "course_id": row["course_id"],
                "tag_id": mapping[tag]
            })

    return pd.DataFrame(rows)


def build_user_tags(
    users_df: pd.DataFrame, 
    tag_map: dict
) -> pd.DataFrame:
    """Build the users with tags dataframe"""

    rows = []

    for _, row in users_df.iterrows():
        job = row["job"]

        if job and job != "unknown":
            rows.append({
                "user_id": row["user_id"],
                "tag_id": tag_map[job]
            })

    return pd.DataFrame(rows)
