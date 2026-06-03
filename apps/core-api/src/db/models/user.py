from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text

from src.db.database import Base
from src.db.models.association_tables import user_tags


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)

    nickname: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    jwt_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    actions: Mapped[List["Action"]] = relationship(
        "Action",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=user_tags,
        back_populates="users",
    )

    course_stats: Mapped[List["Stats"]] = relationship(
        "Stats",
        back_populates="user",
        cascade="all, delete-orphan",
    )
