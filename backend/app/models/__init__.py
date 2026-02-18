# Importa modelos para que Alembic los registre en Base.metadata
from app.models.user import User  # noqa: F401
from app.models.shift import Shift  # noqa: F401
from app.models.session import Session  # noqa: F401
