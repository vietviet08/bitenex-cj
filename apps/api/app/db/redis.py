"""Redis connection and utilities for event queue."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import get_settings


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency to get Redis connection."""
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@asynccontextmanager
async def get_redis_context() -> AsyncGenerator[Redis, None]:
    """Context manager for Redis connection (for non-request usage)."""
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


class EventQueue:
    """Redis Streams-based event queue."""

    STREAM_KEY = "events:ingested"

    def __init__(self, client: Redis):
        self.client = client

    async def enqueue(self, event: dict[str, Any]) -> str:
        """Add event to the stream. Returns message ID."""
        import json

        message_id = await self.client.xadd(
            self.STREAM_KEY,
            {"data": json.dumps(event)},
        )
        return message_id

    async def enqueue_batch(self, events: list[dict[str, Any]]) -> list[str]:
        """Add multiple events to the stream."""
        message_ids = []
        for event in events:
            msg_id = await self.enqueue(event)
            message_ids.append(msg_id)
        return message_ids

    async def dequeue(
        self,
        count: int = 100,
        block_ms: int = 1000,
        last_id: str = "0",
    ) -> list[tuple[str, dict[str, Any]]]:
        """Read events from the stream."""
        import json

        messages = await self.client.xread(
            {self.STREAM_KEY: last_id},
            count=count,
            block=block_ms,
        )
        if not messages:
            return []

        result = []
        for _, entries in messages:
            for msg_id, data in entries:
                event = json.loads(data["data"])
                result.append((msg_id, event))
        return result

    async def ack(self, message_ids: list[str], group: str = "processor") -> int:
        """Acknowledge processed messages."""
        if not message_ids:
            return 0
        return await self.client.xack(self.STREAM_KEY, group, *message_ids)
