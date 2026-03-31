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
