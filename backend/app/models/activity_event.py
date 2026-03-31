from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id", ondelete="CASCADE"), index=True, nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    allowlist_domain_id: Mapped[int] = mapped_column(
        ForeignKey("allowlist_domains.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    page_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", backref="activity_events")
    shift = relationship("Shift", backref="activity_events")
    session = relationship("Session", backref="activity_events")
    allowlist_domain = relationship("AllowlistDomain", backref="activity_events")
