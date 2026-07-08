import unittest
from datetime import datetime, timezone

from tests.bootstrap import configure_test_environment

configure_test_environment()

from app.core.exceptions import ConflictError, NotFoundError
from app.models.allowlist_domain import AllowlistDomain
from app.services.allowlist_domains import AllowlistDomainService


class FakeAllowlistRepository:
    def __init__(self):
        self.entries: list[AllowlistDomain] = []
        self.commits = 0
        self._next_id = 1

    def list_all(self) -> list[AllowlistDomain]:
        return list(self.entries)

    def get_by_id(self, domain_id: int) -> AllowlistDomain | None:
        return next((entry for entry in self.entries if entry.id == domain_id), None)

    def get_by_domain(self, domain: str) -> AllowlistDomain | None:
        return next((entry for entry in self.entries if entry.domain == domain), None)

    def create(
        self,
        *,
        domain: str,
        description: str | None,
        created_by_user_id: int | None,
    ) -> AllowlistDomain:
        now = datetime.now(timezone.utc)
        entry = AllowlistDomain(
            id=self._next_id,
            domain=domain,
            description=description,
            is_active=True,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        self._next_id += 1
        self.entries.append(entry)
        return entry

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, instance: object) -> None:
        return None


class AllowlistDomainServiceTests(unittest.TestCase):
    def test_create_domain_normalizes_input(self) -> None:
        repository = FakeAllowlistRepository()
        service = AllowlistDomainService(allowlist_repository=repository)

        domain = service.create_domain(
            raw_domain="https://Portal.Example.com/reportes",
            description="Portal KPI",
            created_by_user_id=1,
        )

        self.assertEqual(domain.domain, "portal.example.com")
        self.assertEqual(domain.description, "Portal KPI")
        self.assertEqual(repository.commits, 1)

    def test_create_domain_rejects_duplicates(self) -> None:
        repository = FakeAllowlistRepository()
        service = AllowlistDomainService(allowlist_repository=repository)
        service.create_domain(raw_domain="example.com", description=None, created_by_user_id=1)

        with self.assertRaisesRegex(ConflictError, "allowlist"):
            service.create_domain(
                raw_domain="https://example.com/home",
                description=None,
                created_by_user_id=1,
            )

    def test_set_domain_status_requires_existing_entry(self) -> None:
        repository = FakeAllowlistRepository()
        service = AllowlistDomainService(allowlist_repository=repository)

        with self.assertRaisesRegex(NotFoundError, "no existe"):
            service.set_domain_status(domain_id=99, is_active=False)


if __name__ == "__main__":
    unittest.main()
