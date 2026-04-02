"""Tests for health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_healthz(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/healthz")
    # May be 200 or 503 depending on Redis availability
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "redis" in data


@pytest.mark.anyio
async def test_readyz(client: AsyncClient):
    """Test readiness endpoint."""
    response = await client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
