from __future__ import annotations

from datetime import time

from sqlalchemy import ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ScheduleTemplateSlot(Base):
    __tablename__ = "schedule_template_slots"
    __table_args__ = (
        UniqueConstraint("schedule_template_id", "weekday", name="uq_schedule_template_slots_weekday"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_template_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_templates.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    weekday: Mapped[str] = mapped_column(String(10), nullable=False)
    start_time: Mapped[time] = mapped_column(Time(), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(), nullable=False)

    schedule_template = relationship("ScheduleTemplate", back_populates="slots")
