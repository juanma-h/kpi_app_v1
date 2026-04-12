from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Novelty(Base):
    __tablename__ = "novelties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    area_id: Mapped[int] = mapped_column(
        ForeignKey("operational_areas.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    source_system_id: Mapped[int] = mapped_column(
        ForeignKey("source_systems.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    reported_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reported_shift_id: Mapped[int | None] = mapped_column(
        ForeignKey("shifts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reported_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    external_reference: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    order_reference: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    customer_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    novelty_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    first_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    area = relationship("OperationalArea", back_populates="novelties")
    source_system = relationship("SourceSystem", back_populates="novelties")
    reported_by = relationship("User", foreign_keys=[reported_by_user_id], backref="reported_novelties")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], backref="assigned_novelties")
    reported_shift = relationship("Shift", foreign_keys=[reported_shift_id])
    reported_session = relationship("Session", foreign_keys=[reported_session_id])
    logs = relationship(
        "NoveltyLog",
        back_populates="novelty",
        cascade="all, delete-orphan",
        order_by="desc(NoveltyLog.work_date), desc(NoveltyLog.logged_at), desc(NoveltyLog.id)",
    )
