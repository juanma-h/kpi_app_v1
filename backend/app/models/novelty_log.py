from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NoveltyLog(Base):
    __tablename__ = "novelty_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    novelty_id: Mapped[int] = mapped_column(
        ForeignKey("novelties.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    author_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    shift_id: Mapped[int | None] = mapped_column(
        ForeignKey("shifts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    work_date: Mapped[date] = mapped_column(Date(), index=True, nullable=False)
    log_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    worked_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_after: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    novelty = relationship("Novelty", back_populates="logs")
    author = relationship("User", foreign_keys=[author_user_id], backref="novelty_logs")
    shift = relationship("Shift", foreign_keys=[shift_id])
    session = relationship("Session", foreign_keys=[session_id])
