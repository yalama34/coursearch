from sqlalchemy import Table, Column, Integer, ForeignKey

from ..database import Base


course_tags = Table(
    "course_tags",
    Base.metadata,

    Column(
        "course_id",
        Integer,
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


user_tags = Table(
    "user_tags",
    Base.metadata,

    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
