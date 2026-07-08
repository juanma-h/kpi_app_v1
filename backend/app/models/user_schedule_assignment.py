from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserScheduleAssignment(Base):
    __tablename__ = "user_schedule_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    schedule_template_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_templates.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    effective_from: Mapped[date] = mapped_column(Date(), nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", foreign_keys=[user_id], backref="schedule_assignments")
    schedule_template = relationship("ScheduleTemplate", back_populates="assignments")
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id], backref="managed_schedule_assignments")
