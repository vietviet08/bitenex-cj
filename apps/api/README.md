# Customer Journey API

FastAPI-based event collector and analytics API for customer journey tracking.

## Features

- **Event Tracking**: Ingest events via Web SDK with validation and enrichment
- **Identity Resolution**: Link anonymous visitors to authenticated users
- **Analytics**: User timeline, funnel analysis, segment preview
- **Automation**: Integration with n8n for workflow triggers

## Project Structure

```
apps/api/
├── app/
│   ├── api/                    # API routes
│   │   ├── health.py           # Health check endpoints
│   │   └── v1/                 # API v1 endpoints
│   │       ├── events.py       # POST /v1/events
│   │       ├── identify.py     # POST /v1/identify
│   │       └── analytics.py    # Timeline, funnel, segment endpoints
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Pydantic settings
│   │   ├── security.py         # JWT auth and RBAC
│   │   └── exceptions.py       # Custom exceptions
│   ├── db/                     # Database connections
│   │   ├── postgres.py         # SQLAlchemy async session
│   │   ├── clickhouse.py       # ClickHouse client
│   │   └── redis.py            # Redis client and event queue
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── identity.py
│   │   ├── segment.py
│   │   └── workflow.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── events.py
│   │   ├── identity.py
│   │   └── analytics.py
│   ├── services/               # Business logic
│   │   ├── event_service.py
│   │   ├── identity_service.py
│   │   └── analytics_service.py
│   └── main.py                 # FastAPI application
├── migrations/                 # Alembic migrations
├── tests/                      # Test suite
├── pyproject.toml              # Project dependencies
└── .env.example                # Environment template
```

## Quick Start

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Start the API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Open API docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/v1/events` | POST | Ingest single event |
| `/v1/events/batch` | POST | Ingest batch events |
| `/v1/identify` | POST | Link anonymous_id to user |
| `/v1/users/{id}/timeline` | GET | Get user event timeline |
| `/v1/funnels` | GET | Funnel conversion analysis |
| `/v1/segments/preview` | POST | Preview segment estimation |

## Authentication

API uses JWT tokens with role-based access:
- `admin`: Full access
- `analyst`: Read access to analytics endpoints
- `operator`: Write access to events and identify

## Development

```bash
# Run tests
pytest

# Type checking
mypy app

# Linting
ruff check app
```
