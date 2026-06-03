from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Integer
from sqlalchemy import Enum as SqlEnum

from ..database import Base
from src.domain.enum.action_type import ActionType


class Action(Base):
    __tablename__ = "actions"

    action_id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False,
    )

    action_type: Mapped[ActionType] = mapped_column(
        "type",
        SqlEnum(
            ActionType,
            name="actiontype",
            values_callable=lambda enum: [member.name for member in enum],
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    value: Mapped[int | None] = mapped_column(
        Integer,
        default=None,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="actions",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="actions",
    )
