from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    EMPLOYEE = "EMPLOYEE"


class ShiftStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SessionStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class ActivityEventType(StrEnum):
    PAGE_VIEW = "PAGE_VIEW"
    HEARTBEAT = "HEARTBEAT"
    IDLE = "IDLE"
    RESUME = "RESUME"


class Weekday(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class NoveltyPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NoveltyStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class NoveltyLogType(StrEnum):
    DAILY_UPDATE = "DAILY_UPDATE"
    STATUS_CHANGE = "STATUS_CHANGE"
    ASSIGNMENT = "ASSIGNMENT"
    COMMENT = "COMMENT"
    RESOLUTION = "RESOLUTION"
