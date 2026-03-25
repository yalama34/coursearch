from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from ..database import Base
from .association_tables import course_tags, user_tags


class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    courses: Mapped[List["Course"]] = relationship(
        "Course",
        secondary=course_tags,
        back_populates="tags",
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_tags,
        back_populates="tags",
    )
