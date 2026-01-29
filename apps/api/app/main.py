from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict
import redis


class Settings(BaseSettings):
    api_port: int = 8000
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
app = FastAPI(title="Customer Journey API", version="0.1.0")


def _check_redis() -> None:
    client = redis.Redis.from_url(settings.redis_url)
    client.ping()


@app.get("/healthz")
def healthz():
    try:
        _check_redis()
        return {"status": "ok", "redis": "ok"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "redis": "error"},
        )
