"""Analytics schemas for timeline, funnel, and segment APIs."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """Single event in user timeline."""

    event_name: str
    timestamp: datetime
    properties: dict[str, Any]


class TimelineResponse(BaseModel):
    """User journey timeline response."""

    user_id: str
    events: list[TimelineEvent]


class FunnelRequest(BaseModel):
    """Query parameters for funnel analysis (used for validation)."""

    from_date: date = Field(..., alias="from")
    to_date: date = Field(..., alias="to")
    steps: list[str] = Field(
        ..., min_length=2, description="Comma-separated event names"
    )

    class Config:
        populate_by_name = True


class FunnelResponse(BaseModel):
    """Funnel analysis response."""

    from_date: date = Field(..., serialization_alias="from")
    to_date: date = Field(..., serialization_alias="to")
    steps: list[str]
    counts: list[int]

    class Config:
        populate_by_name = True


class SegmentDefinition(BaseModel):
    """Segment definition with include/exclude rules."""

    include: dict[str, Any] = Field(..., description="Events to include")
    exclude: dict[str, Any] | None = Field(None, description="Events to exclude")


class SegmentPreviewRequest(BaseModel):
    """Request to preview a segment."""

    name: str = Field(..., description="Segment name")
    definition: SegmentDefinition


class SegmentPreviewResponse(BaseModel):
    """Segment preview response."""

    segment_id: str
    estimated_users: int
