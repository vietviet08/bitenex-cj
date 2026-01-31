"""ClickHouse database connection for event analytics."""

from typing import Any

import clickhouse_connect
from clickhouse_connect.driver import Client

from app.core.config import get_settings


def get_clickhouse_client() -> Client:
    """Get ClickHouse client instance."""
    settings = get_settings()
    return clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        database=settings.clickhouse_db,
    )


async def execute_query(
    query: str, parameters: dict[str, Any] | None = None
) -> list[dict]:
    """Execute a ClickHouse query and return results as list of dicts."""
    client = get_clickhouse_client()
    try:
        result = client.query(query, parameters=parameters)
        columns = result.column_names
        return [dict(zip(columns, row)) for row in result.result_rows]
    finally:
        client.close()


async def insert_events(events: list[dict[str, Any]]) -> int:
    """Insert events into ClickHouse."""
    if not events:
        return 0

    client = get_clickhouse_client()
    try:
        columns = list(events[0].keys())
        data = [[event.get(col) for col in columns] for event in events]
        client.insert("events", data, column_names=columns)
        return len(events)
    finally:
        client.close()
