import unittest
from datetime import datetime, timezone

from bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import ConflictError
from app.domain.enums import SessionStatus, ShiftStatus
from app.models.session import Session as WorkSession
from app.models.shift import Shift
from app.services.shifts import ShiftService


class FakeShiftWorkRepository:
    def __init__(self):
        self.shift: Shift | None = None
        self.session: WorkSession | None = None
        self.commits = 0
        self._shift_id = 1
        self._session_id = 1

    def get_open_shift_for_user(self, user_id: int) -> Shift | None:
        if self.shift and self.shift.user_id == user_id and self.shift.status == ShiftStatus.OPEN.value:
            return self.shift
        return None

    def get_open_session_for_shift(self, shift_id: int) -> WorkSession | None:
        if self.session and self.session.shift_id == shift_id and self.session.status == SessionStatus.OPEN.value:
            return self.session
        return None

    def create_shift(self, *, user_id: int, start_at: datetime, status: str) -> Shift:
        self.shift = Shift(
            id=self._shift_id,
            user_id=user_id,
            start_at=start_at,
            status=status,
        )
        self._shift_id += 1
        return self.shift

    def create_session(
        self,
        *,
        user_id: int,
        shift_id: int,
        start_at: datetime,
        status: str,
        device_label: str | None,
    ) -> WorkSession:
        self.session = WorkSession(
            id=self._session_id,
            user_id=user_id,
            shift_id=shift_id,
            start_at=start_at,
            status=status,
            device_label=device_label,
        )
        self._session_id += 1
        return self.session

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, instance: object) -> None:
        return None


class ShiftServiceTests(unittest.TestCase):
    def test_start_shift_creates_shift_and_session(self) -> None:
        repository = FakeShiftWorkRepository()
        service = ShiftService(shift_work_repository=repository)

        shift, session = service.start_shift(user_id=7, device_label="PC-01")

        self.assertEqual(shift.user_id, 7)
        self.assertEqual(shift.status, ShiftStatus.OPEN.value)
        self.assertEqual(session.shift_id, shift.id)
        self.assertEqual(session.status, SessionStatus.OPEN.value)
        self.assertEqual(repository.commits, 1)

    def test_start_shift_rejects_duplicate_open_shift(self) -> None:
        repository = FakeShiftWorkRepository()
        repository.shift = Shift(
            id=1,
            user_id=7,
            start_at=datetime.now(timezone.utc),
            status=ShiftStatus.OPEN.value,
        )
        service = ShiftService(shift_work_repository=repository)

        with self.assertRaisesRegex(ConflictError, "turno abierto"):
            service.start_shift(user_id=7, device_label=None)

    def test_end_shift_closes_shift_and_session(self) -> None:
        repository = FakeShiftWorkRepository()
        repository.shift = Shift(
            id=1,
            user_id=7,
            start_at=datetime.now(timezone.utc),
            status=ShiftStatus.OPEN.value,
        )
        repository.session = WorkSession(
            id=1,
            user_id=7,
            shift_id=1,
            start_at=datetime.now(timezone.utc),
            status=SessionStatus.OPEN.value,
            device_label="PC-01",
        )
        service = ShiftService(shift_work_repository=repository)

        shift, session = service.end_shift(user_id=7)

        self.assertEqual(shift.status, ShiftStatus.CLOSED.value)
        self.assertEqual(session.status, SessionStatus.CLOSED.value)
        self.assertIsNotNone(shift.end_at)
        self.assertIsNotNone(session.end_at)


if __name__ == "__main__":
    unittest.main()
