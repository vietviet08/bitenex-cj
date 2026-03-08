"""Common schemas used across the API."""

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    redis: str
    postgres: str | None = None
    clickhouse: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error_code: str
    message: str
    details: dict[str, Any] = {}
