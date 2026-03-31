from sqlalchemy.orm import Session

from app.models.allowlist_domain import AllowlistDomain
from app.repositories.contracts import AllowlistDomainRepositoryProtocol


class AllowlistDomainRepository(AllowlistDomainRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[AllowlistDomain]:
        return self.db.query(AllowlistDomain).order_by(AllowlistDomain.domain.asc()).all()

    def get_by_id(self, domain_id: int) -> AllowlistDomain | None:
        return self.db.get(AllowlistDomain, domain_id)

    def get_by_domain(self, domain: str) -> AllowlistDomain | None:
        return (
            self.db.query(AllowlistDomain)
            .filter(AllowlistDomain.domain == domain)
            .first()
        )

    def create(
        self,
        *,
        domain: str,
        description: str | None,
        created_by_user_id: int | None,
    ) -> AllowlistDomain:
        allowlist_domain = AllowlistDomain(
            domain=domain,
            description=description,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(allowlist_domain)
        return allowlist_domain

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: object) -> None:
        self.db.refresh(instance)
