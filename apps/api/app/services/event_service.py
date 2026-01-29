"""Event ingestion and processing service."""

from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis

from app.db.redis import EventQueue
from app.schemas.events import EventCreate


class EventService:
    """Service for event ingestion and enrichment."""

    def __init__(self, redis_client: Redis):
        self.queue = EventQueue(redis_client)

    async def ingest_event(
        self,
        event: EventCreate,
        client_ip: str | None = None,
    ) -> str:
        """
        Validate, enrich, and enqueue a single event.
        Returns the message ID from Redis Streams.
        """
        enriched = self._enrich_event(event, client_ip)
        message_id = await self.queue.enqueue(enriched)
        return message_id

    async def ingest_batch(
        self,
        events: list[EventCreate],
        client_ip: str | None = None,
    ) -> list[str]:
        """Ingest multiple events in batch."""
        enriched_events = [self._enrich_event(e, client_ip) for e in events]
        message_ids = await self.queue.enqueue_batch(enriched_events)
        return message_ids

    def _enrich_event(
        self,
        event: EventCreate,
        client_ip: str | None = None,
    ) -> dict[str, Any]:
        """Enrich event with server-side data."""
        event_dict = event.model_dump(mode="json")

        # Add server-side enrichment
        event_dict["_enriched"] = {
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "client_ip": client_ip,
        }

        return event_dict


class IdempotencyService:
    """Service for handling idempotent requests."""

    KEY_PREFIX = "idempotency:"
    TTL_SECONDS = 86400  # 24 hours

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def check_and_set(
        self,
        idempotency_key: str,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Check if idempotency key exists.
        If exists, return the cached result.
        If not, store the result and return None.
        """
        import json

        key = f"{self.KEY_PREFIX}{idempotency_key}"
        existing = await self.redis.get(key)

        if existing:
            return json.loads(existing)

        await self.redis.setex(key, self.TTL_SECONDS, json.dumps(result))
        return None

    async def get(self, idempotency_key: str) -> dict[str, Any] | None:
        """Get cached result for idempotency key."""
        import json

        key = f"{self.KEY_PREFIX}{idempotency_key}"
        existing = await self.redis.get(key)
        return json.loads(existing) if existing else None
