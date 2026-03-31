from datetime import datetime

from sqlalchemy.orm import Session

from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.repositories.contracts import ShiftWorkRepositoryProtocol


class ShiftWorkRepository(ShiftWorkRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def get_open_shift_for_user(self, user_id: int) -> Shift | None:
        return (
            self.db.query(Shift)
            .filter(Shift.user_id == user_id, Shift.status == "OPEN")
            .first()
        )

    def get_open_session_for_shift(self, shift_id: int) -> WorkSession | None:
        return (
            self.db.query(WorkSession)
            .filter(WorkSession.shift_id == shift_id, WorkSession.status == "OPEN")
            .first()
        )

    def create_shift(self, *, user_id: int, start_at: datetime, status: str) -> Shift:
        shift = Shift(user_id=user_id, start_at=start_at, status=status)
        self.db.add(shift)
        self.db.flush()
        return shift

    def create_session(
        self,
        *,
        user_id: int,
        shift_id: int,
        start_at: datetime,
        status: str,
        device_label: str | None,
    ) -> WorkSession:
        session = WorkSession(
            user_id=user_id,
            shift_id=shift_id,
            start_at=start_at,
            status=status,
            device_label=device_label,
        )
        self.db.add(session)
        return session

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
