# Importa modelos para que Alembic los registre en Base.metadata
from app.models.activity_event import ActivityEvent  # noqa: F401
from app.models.allowlist_domain import AllowlistDomain  # noqa: F401
from app.models.novelty import Novelty  # noqa: F401
from app.models.novelty_log import NoveltyLog  # noqa: F401
from app.models.operational_area import OperationalArea  # noqa: F401
from app.models.schedule_template import ScheduleTemplate  # noqa: F401
from app.models.schedule_template_slot import ScheduleTemplateSlot  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.shift import Shift  # noqa: F401
from app.models.source_system import SourceSystem  # noqa: F401
from app.models.user_schedule_assignment import UserScheduleAssignment  # noqa: F401
from app.models.user import User  # noqa: F401
