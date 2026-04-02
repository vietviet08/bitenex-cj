"""Event schemas for tracking API."""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EventContext(BaseModel):
    """Event context with required fields."""

    user_agent: str
    page_url: str
    referrer: str = ""
    locale: str
    tz: str

    class Config:
        extra = "allow"  # Allow additional context fields


class EventCreate(BaseModel):
    """Schema for creating a new event."""

    event_id: str = Field(..., description="UUID v4 for event identification")
    event_name: str = Field(
        ..., pattern=r"^[a-z0-9_]+$", description="Snake_case event name"
    )
    timestamp: datetime = Field(..., description="ISO 8601 UTC timestamp")
    anonymous_id: str = Field(..., description="Anonymous visitor identifier")
    context: EventContext
    properties: dict[str, Any] = Field(default_factory=dict)

    # Optional fields
    user_id: str | None = None
    email: str | None = None
    phone: str | None = None
    device_id: str | None = None
    session_id: str | None = None

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9_]+$", v):
            raise ValueError(
                "event_name must be snake_case (lowercase letters, numbers, underscores)"
            )
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str | None) -> str | None:
        if v is not None:
            # Simple UUID validation
            uuid_pattern = (
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            )
            if not re.match(uuid_pattern, v.lower()):
                raise ValueError("user_id must be a valid UUID")
        return v


class EventResponse(BaseModel):
    """Single event in response."""

    event_id: str
    event_name: str
    timestamp: datetime
    properties: dict[str, Any]


class EventsIngestResponse(BaseModel):
    """Response for event ingestion."""

    status: str = "ok"
    ingested: int
    event_ids: list[str]
