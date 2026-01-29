"""Health check endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

import redis

from app.core.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter()


def _check_redis() -> str:
    """Check Redis connectivity."""
    settings = get_settings()
    try:
        client = redis.Redis.from_url(settings.redis_url)
        client.ping()
        return "ok"
    except Exception:
        return "error"


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse | JSONResponse:
    """
    Health check endpoint.

    Returns service status and connectivity to dependencies.
    """
    redis_status = _check_redis()

    if redis_status == "error":
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "redis": redis_status,
            },
        )

    return HealthResponse(
        status="ok",
        redis=redis_status,
    )


@router.get("/readyz")
def readyz() -> dict[str, str]:
    """Readiness probe for Kubernetes."""
    return {"status": "ready"}
