"""Customer Journey API - FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import router as v1_router
from app.core.config import get_settings
from app.core.exceptions import AppException, app_exception_handler, http_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    settings = get_settings()
    print(f"Starting Customer Journey API on port {settings.api_port}")
    yield
    # Shutdown
    print("Shutting down Customer Journey API")


settings = get_settings()

app = FastAPI(
    title="Customer Journey API",
    description="Event tracking, identity resolution, and analytics API for customer journey management.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include routers
app.include_router(health_router)
app.include_router(v1_router)
