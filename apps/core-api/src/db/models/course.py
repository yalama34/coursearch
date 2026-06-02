from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text

from src.db.database import Base
from src.db.models.association_tables import course_tags


class Course(Base):
    __tablename__ = "courses"

    course_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    difficulty: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    link: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    actions: Mapped[List["Action"]] = relationship(
        "Action",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=course_tags,
        back_populates="courses",
    )

    user_stats: Mapped[List["Stats"]] = relationship(
        "Stats",
        back_populates="course",
        cascade="all, delete-orphan",
    )
