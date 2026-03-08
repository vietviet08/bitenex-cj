"""Analytics endpoints for timeline, funnel, and segment preview."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.security import TokenPayload, require_analyst
from app.schemas.analytics import (
    FunnelResponse,
    SegmentPreviewRequest,
    SegmentPreviewResponse,
    TimelineResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/users/{user_id}/timeline", response_model=TimelineResponse)
async def get_user_timeline(
    user_id: str,
    _: Annotated[TokenPayload, Depends(require_analyst)],
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> TimelineResponse:
    """
    Get user's event timeline.

    Returns events in reverse chronological order.
    Requires analyst or admin role.
    """
    service = AnalyticsService()
    return await service.get_user_timeline(user_id, limit=limit, offset=offset)


@router.get("/funnels", response_model=FunnelResponse)
async def get_funnel(
    _: Annotated[TokenPayload, Depends(require_analyst)],
    from_date: date = Query(..., alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., alias="to", description="End date (YYYY-MM-DD)"),
    steps: str = Query(
        ...,
        description="Comma-separated event names for funnel steps",
        example="page_view,add_to_cart,purchase_success",
    ),
) -> FunnelResponse:
    """
    Calculate funnel conversion.

    Provides conversion counts for each step in the funnel.
    Requires analyst or admin role.
    """
    steps_list = [s.strip() for s in steps.split(",") if s.strip()]
    if len(steps_list) < 2:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="At least 2 funnel steps are required",
        )

    service = AnalyticsService()
    return await service.get_funnel(from_date, to_date, steps_list)


@router.post("/segments/preview", response_model=SegmentPreviewResponse)
async def preview_segment(
    request: SegmentPreviewRequest,
    _: Annotated[TokenPayload, Depends(require_analyst)],
) -> SegmentPreviewResponse:
    """
    Preview a segment definition.

    Estimates the number of users matching the segment criteria.
    Requires analyst or admin role.
    """
    service = AnalyticsService()
    return await service.preview_segment(request)
