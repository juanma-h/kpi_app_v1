from datetime import datetime, timezone

from app.core.exceptions import ConflictError, InternalStateError, NotFoundError
from app.domain.enums import SessionStatus, ShiftStatus
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.repositories.contracts import ShiftWorkRepositoryProtocol


class ShiftService:
    def __init__(self, shift_work_repository: ShiftWorkRepositoryProtocol):
        self.shift_work_repository = shift_work_repository

    def start_shift(self, *, user_id: int, device_label: str | None) -> tuple[Shift, WorkSession]:
        existing_shift = self.shift_work_repository.get_open_shift_for_user(user_id)
        if existing_shift:
            raise ConflictError("Ya existe un turno abierto para este usuario.")

        now = datetime.now(timezone.utc)
        shift = self.shift_work_repository.create_shift(
            user_id=user_id,
            start_at=now,
            status=ShiftStatus.OPEN.value,
        )
        session = self.shift_work_repository.create_session(
            user_id=user_id,
            shift_id=shift.id,
            start_at=now,
            status=SessionStatus.OPEN.value,
            device_label=device_label,
        )

        self.shift_work_repository.commit()
        self.shift_work_repository.refresh(shift)
        self.shift_work_repository.refresh(session)

        return shift, session

    def get_current_shift(self, *, user_id: int) -> tuple[Shift, WorkSession]:
        shift = self.shift_work_repository.get_open_shift_for_user(user_id)
        if not shift:
            raise NotFoundError("No hay turno abierto.")

        session = self.shift_work_repository.get_open_session_for_shift(shift.id)
        if not session:
            raise InternalStateError("Turno abierto sin sesion activa.")

        return shift, session

    def end_shift(self, *, user_id: int) -> tuple[Shift, WorkSession]:
        shift, session = self.get_current_shift(user_id=user_id)
        now = datetime.now(timezone.utc)

        shift.status = ShiftStatus.CLOSED.value
        shift.end_at = now
        session.status = SessionStatus.CLOSED.value
        session.end_at = now

        self.shift_work_repository.commit()
        self.shift_work_repository.refresh(shift)
        self.shift_work_repository.refresh(session)

        return shift, session
