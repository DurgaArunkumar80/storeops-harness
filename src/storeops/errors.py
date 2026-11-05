"""Typed error hierarchy for StoreOps API."""

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Standard error codes."""

    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class AppError(Exception):
    """Base application error with structured error information."""

    def __init__(
        self, code: ErrorCode | str, message: str, status_code: int = 500, details: Any = None
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(ErrorCode.NOT_FOUND, message, 404, details)


class ValidationError(AppError):
    """Validation failed."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(ErrorCode.VALIDATION_ERROR, message, 400, details)


class UnauthorizedError(AppError):
    """User not authenticated."""

    def __init__(self, message: str = "Unauthorized", details: Any = None) -> None:
        super().__init__(ErrorCode.UNAUTHORIZED, message, 401, details)


class ForbiddenError(AppError):
    """User lacks permission."""

    def __init__(self, message: str = "Forbidden", details: Any = None) -> None:
        super().__init__(ErrorCode.FORBIDDEN, message, 403, details)


class ConflictError(AppError):
    """Resource conflict."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(ErrorCode.CONFLICT, message, 409, details)
