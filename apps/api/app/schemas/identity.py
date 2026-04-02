"""Identity schemas for user resolution."""

from pydantic import BaseModel, Field


class IdentifyRequest(BaseModel):
    """Request to link anonymous_id to user identifiers."""

    anonymous_id: str = Field(..., description="Anonymous visitor identifier")
    user_id: str | None = Field(None, description="Authenticated user UUID")
    email: str | None = Field(None, description="User email address")
    phone: str | None = Field(None, description="User phone number")
    device_id: str | None = Field(None, description="Device identifier")


class IdentifyResponse(BaseModel):
    """Response for identity resolution."""

    status: str = "ok"
    user_id: str
