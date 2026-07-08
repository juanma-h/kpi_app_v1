from fastapi import status


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str, headers: dict[str, str] | None = None):
        self.detail = detail
        self.headers = headers or {}
        super().__init__(detail)


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, detail: str = "Credenciales invalidas o token expirado."):
        super().__init__(detail, headers={"WWW-Authenticate": "Bearer"})


class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


class ValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InternalStateError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
