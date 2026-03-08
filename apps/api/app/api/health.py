"""Health check endpoints."""

import redis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.db.clickhouse import get_clickhouse_client
from app.db.postgres import engine as postgres_engine
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


async def _check_postgres() -> str:
    """Check Postgres connectivity."""
    try:
        async with postgres_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


def _check_clickhouse() -> str:
    """Check ClickHouse connectivity."""
    client = None
    try:
        client = get_clickhouse_client()
        client.query("SELECT 1")
        return "ok"
    except Exception:
        return "error"
    finally:
        if client is not None:
            client.close()


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse | JSONResponse:
    """
    Health check endpoint.

    Returns service status and connectivity to dependencies.
    """
    redis_status = _check_redis()
    postgres_status = await _check_postgres()
    clickhouse_status = _check_clickhouse()

    if "error" in (redis_status, postgres_status, clickhouse_status):
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "redis": redis_status,
                "postgres": postgres_status,
                "clickhouse": clickhouse_status,
            },
        )

    return HealthResponse(
        status="ok",
        redis=redis_status,
        postgres=postgres_status,
        clickhouse=clickhouse_status,
    )


@router.get("/readyz")
def readyz() -> dict[str, str]:
    """Readiness probe for Kubernetes."""
    return {"status": "ready"}
