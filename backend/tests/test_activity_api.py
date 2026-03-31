from datetime import datetime, timezone
import unittest

from bootstrap import configure_test_environment

configure_test_environment()

from fastapi.testclient import TestClient

from app.core.deps import get_activity_event_service, get_current_user
from app.domain.enums import ActivityEventType, UserRole
from app.main import app
from app.models.activity_event import ActivityEvent
from app.models.user import User


def build_user(
    *,
    user_id: int,
    email: str,
    role: UserRole,
    is_active: bool = True,
) -> User:
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=email,
        password_hash="hashed",
        role=role.value,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )


def build_event(
    *,
    event_id: int,
    user_id: int,
    event_type: ActivityEventType,
) -> ActivityEvent:
    now = datetime.now(timezone.utc)
    return ActivityEvent(
        id=event_id,
        user_id=user_id,
        shift_id=11,
        session_id=31,
        allowlist_domain_id=5,
        event_type=event_type.value,
        source_url="https://example.com/home",
        source_domain="example.com",
        page_title="Home",
        occurred_at=now,
        recorded_at=now,
        duration_seconds=60 if event_type == ActivityEventType.HEARTBEAT else None,
        event_data={"section": "home"},
    )


class FakeActivityEventService:
    def __init__(self):
        self.created_payload: dict | None = None
        self.events = [
            build_event(event_id=1, user_id=2, event_type=ActivityEventType.PAGE_VIEW),
            build_event(event_id=2, user_id=3, event_type=ActivityEventType.HEARTBEAT),
        ]

    def register_event(
        self,
        *,
        user_id: int,
        event_type: ActivityEventType,
        source_url: str,
        page_title: str | None,
        occurred_at: datetime | None,
        duration_seconds: int | None,
        event_data: dict[str, str | int | float | bool | None] | None,
    ) -> ActivityEvent:
        self.created_payload = {
            "user_id": user_id,
            "event_type": event_type,
            "source_url": source_url,
            "page_title": page_title,
            "occurred_at": occurred_at,
            "duration_seconds": duration_seconds,
            "event_data": event_data,
        }
        event = build_event(event_id=3, user_id=user_id, event_type=event_type)
        event.source_url = source_url
        event.page_title = page_title
        event.duration_seconds = duration_seconds
        event.event_data = event_data
        self.events.append(event)
        return event

    def list_events(
        self,
        *,
        user_id: int | None = None,
        shift_id: int | None = None,
        session_id: int | None = None,
        allowlist_domain_id: int | None = None,
        event_type: ActivityEventType | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        events = list(self.events)
        if user_id is not None:
            events = [event for event in events if event.user_id == user_id]
        if event_type is not None:
            events = [event for event in events if event.event_type == event_type.value]
        return events[:limit]


class ActivityApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.activity_service = FakeActivityEventService()

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_employee_can_register_activity_event(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_activity_event_service] = lambda: self.activity_service

        response = self.client.post(
            "/activity/events",
            json={
                "event_type": "PAGE_VIEW",
                "source_url": "https://example.com/home",
                "page_title": "Home",
                "event_data": {"section": "home"},
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user_id"], 2)
        self.assertEqual(self.activity_service.created_payload["event_type"], ActivityEventType.PAGE_VIEW)

    def test_employee_can_list_own_activity_events(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_activity_event_service] = lambda: self.activity_service

        response = self.client.get("/activity/events/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["user_id"], 2)

    def test_employee_cannot_list_global_activity_events(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=2,
            email="employee@kpi.com",
            role=UserRole.EMPLOYEE,
        )
        app.dependency_overrides[get_activity_event_service] = lambda: self.activity_service

        response = self.client.get("/activity/events")

        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_list_global_activity_events(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: build_user(
            user_id=10,
            email="supervisor@kpi.com",
            role=UserRole.SUPERVISOR,
        )
        app.dependency_overrides[get_activity_event_service] = lambda: self.activity_service

        response = self.client.get("/activity/events?event_type=HEARTBEAT")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["event_type"], "HEARTBEAT")


if __name__ == "__main__":
    unittest.main()
