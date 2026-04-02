"""Custom exceptions and error handling."""

from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = 400,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code="validation_error",
            message=message,
            details=details,
            status_code=422,
        )


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            error_code="not_found",
            message=f"{resource} not found",
            details={"resource": resource, "identifier": identifier},
            status_code=404,
        )


class ConflictError(AppException):
    """Resource conflict error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code="conflict",
            message=message,
            details=details,
            status_code=409,
        )


class ServiceUnavailableError(AppException):
    """External service unavailable."""

    def __init__(self, service: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code="service_unavailable",
            message=f"{service} is currently unavailable",
            details=details,
            status_code=503,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for AppException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTPException to use standard format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": "http_error",
            "message": exc.detail,
            "details": {},
        },
    )
