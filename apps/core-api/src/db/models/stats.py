from datetime import datetime, timezone

from sqlalchemy import (
    ForeignKey,
    DateTime,
    Integer,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.db.database import Base


class Stats(Base):
    __tablename__ = "stats"
    
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_stats_user_course",
        ),
    )

    stats_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    total_watch_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="course_stats",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="user_stats",
    )
