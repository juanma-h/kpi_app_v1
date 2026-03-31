from urllib.parse import urlparse

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.allowlist_domain import AllowlistDomain
from app.repositories.contracts import AllowlistDomainRepositoryProtocol


class AllowlistDomainService:
    def __init__(self, allowlist_repository: AllowlistDomainRepositoryProtocol):
        self.allowlist_repository = allowlist_repository

    def list_domains(self) -> list[AllowlistDomain]:
        return list(self.allowlist_repository.list_all())

    def create_domain(
        self,
        *,
        raw_domain: str,
        description: str | None,
        created_by_user_id: int | None,
    ) -> AllowlistDomain:
        domain = self.normalize_domain(raw_domain)
        existing = self.allowlist_repository.get_by_domain(domain)
        if existing:
            raise ConflictError("El dominio ya existe en la allowlist.")

        allowlist_domain = self.allowlist_repository.create(
            domain=domain,
            description=description,
            created_by_user_id=created_by_user_id,
        )
        self.allowlist_repository.commit()
        self.allowlist_repository.refresh(allowlist_domain)
        return allowlist_domain

    def set_domain_status(self, *, domain_id: int, is_active: bool) -> AllowlistDomain:
        allowlist_domain = self.allowlist_repository.get_by_id(domain_id)
        if not allowlist_domain:
            raise NotFoundError("El dominio solicitado no existe.")

        allowlist_domain.is_active = is_active
        self.allowlist_repository.commit()
        self.allowlist_repository.refresh(allowlist_domain)
        return allowlist_domain

    @staticmethod
    def normalize_domain(raw_domain: str) -> str:
        candidate = raw_domain.strip().lower()
        if not candidate:
            raise ValidationError("El dominio es obligatorio.")

        parsed = urlparse(candidate if "://" in candidate else f"//{candidate}")
        host = parsed.hostname or candidate.split("/")[0].split(":")[0]
        normalized = host.rstrip(".")

        if not normalized or " " in normalized:
            raise ValidationError("El dominio enviado no es valido.")

        return normalized
