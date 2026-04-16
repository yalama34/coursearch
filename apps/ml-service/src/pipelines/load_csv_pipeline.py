import asyncio

# data layer
from src.data.loaders import load_all
from src.data.cleaning import (
    clean_users,
    clean_items,
    clean_explicit,
    clean_implicit,
)
from src.data.normalization import (
    normalize_items,
    normalize_explicit,
    normalize_implicit,
    build_actions,
)
from src.data.tag_processing import (
    extract_tags,
    build_tags,
    build_course_tags,
    build_user_tags,
)

# db layer
from src.db.database import async_session_maker
from src.db.repositories import save_df

# ORM models
from src.db.models import Course, Tag, Action, User

# Table (many-to-many)
from src.db.models.association_tables import user_tags, course_tags


async def load_csv_pipeline():
    """Load the CSV data into the database"""

    # 1. Load
    data = load_all()

    users = data["users"]
    items = data["items"]
    explicit = data["explicit"]
    implicit = data["implicit"]

    # 2. Cleaning
    users = clean_users(users)
    items = clean_items(items)
    explicit = clean_explicit(explicit)
    implicit = clean_implicit(implicit)

    # 3. Normalization
    items = normalize_items(items)
    explicit = normalize_explicit(explicit)
    implicit = normalize_implicit(implicit)

    # 4. Tag processing
    items = extract_tags(items)

    tags_df, tag_map = build_tags(items, users)

    course_tags_df = build_course_tags(items, tag_map)
    user_tags_df = build_user_tags(users, tag_map)

    # 5. Courses
    courses_df = items[[
        "course_id",
        "name",
        "description",
        "difficulty"
    ]].copy()

    courses_df["link"] = None
    courses_df = courses_df.astype(object)
    courses_df = courses_df.where(courses_df.notna(), None)

    # 6. Actions
    actions_df = build_actions(explicit, implicit)

    # 7. Users
    users_df = users[["user_id"]].copy()
    users_df["nickname"] = users_df["user_id"].map(lambda user_id: f"user_{user_id}")
    users_df["password"] = users_df["user_id"].map(
        lambda user_id: f"imported_user_{user_id}"
    )
    valid_course_ids = set(courses_df["course_id"])
    valid_user_ids = set(users_df["user_id"])
    actions_df = actions_df[
        actions_df["course_id"].isin(valid_course_ids)
        & actions_df["user_id"].isin(valid_user_ids)
    ].copy()

    # 8. Save to db
    async with async_session_maker() as session:

        await save_df(session, users_df, User)
        await save_df(session, tags_df, Tag)
        await save_df(session, courses_df, Course)

        await save_df(session, course_tags_df, course_tags)
        await save_df(session, user_tags_df, user_tags)

        await save_df(session, actions_df, Action)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(load_csv_pipeline())
