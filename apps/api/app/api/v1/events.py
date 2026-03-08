"""Event tracking endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from redis.asyncio import Redis

from app.core.security import TokenPayload, require_operator
from app.db.redis import get_redis
from app.schemas.events import EventCreate, EventsIngestResponse
from app.services.event_service import EventService, IdempotencyService

router = APIRouter()


@router.post("/events", response_model=EventsIngestResponse)
async def ingest_event(
    event: EventCreate,
    request: Request,
    redis: Annotated[Redis, Depends(get_redis)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    _: Annotated[TokenPayload, Depends(require_operator)],
) -> EventsIngestResponse:
    """
    Ingest a single event.

    Requires operator or admin role.
    Idempotency-Key header is required for deduplication.
    """
    # Check idempotency
    idempotency_service = IdempotencyService(redis)
    cached = await idempotency_service.get(idempotency_key)
    if cached:
        return EventsIngestResponse(**cached)

    # Get client IP for enrichment
    client_ip = request.client.host if request.client else None

    # Ingest event
    event_service = EventService(redis)
    await event_service.ingest_event(event, client_ip)

    # Build response
    response = EventsIngestResponse(
        status="ok",
        ingested=1,
        event_ids=[event.event_id],
    )

    # Cache for idempotency
    await idempotency_service.check_and_set(
        idempotency_key,
        response.model_dump(),
    )

    return response


@router.post("/events/batch", response_model=EventsIngestResponse)
async def ingest_events_batch(
    events: list[EventCreate],
    request: Request,
    redis: Annotated[Redis, Depends(get_redis)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    _: Annotated[TokenPayload, Depends(require_operator)],
) -> EventsIngestResponse:
    """
    Ingest multiple events in batch.

    Requires operator or admin role.
    """
    # Check idempotency
    idempotency_service = IdempotencyService(redis)
    cached = await idempotency_service.get(idempotency_key)
    if cached:
        return EventsIngestResponse(**cached)

    # Get client IP for enrichment
    client_ip = request.client.host if request.client else None

    # Ingest events
    event_service = EventService(redis)
    await event_service.ingest_batch(events, client_ip)

    # Build response
    response = EventsIngestResponse(
        status="ok",
        ingested=len(events),
        event_ids=[e.event_id for e in events],
    )

    # Cache for idempotency
    await idempotency_service.check_and_set(
        idempotency_key,
        response.model_dump(),
    )

    return response
