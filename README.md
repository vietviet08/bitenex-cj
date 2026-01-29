# Customer Journey Tracking & Automation Platform (MVP)

A lightweight platform to capture user events, resolve identities, analyze journeys (timeline, funnel, retention), and trigger automations (abandoned cart, onboarding, churn warning). Built around a Web Tracking SDK, a FastAPI Event Collector, Postgres + ClickHouse storage, n8n workflows, and a Next.js dashboard.

## Quick Start (5 minutes)

```
# 1) Create env files from the snippets in the Environment Variables section

# 2) Start infra
Docker compose -f infra/docker-compose/docker-compose.yml up -d

# 3) Run Postgres migrations
cd apps/api
alembic upgrade head

# 4) Start API
uvicorn app.main:app --reload --port 8000

# 5) Start Web (new terminal)
cd ../web
pnpm install
pnpm dev

# 6) Send a test event (new terminal)
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-evt-0001" \
  -d '{"event_id":"b7f9dd2d-3a9c-4e7d-9f18-2e8f8c5f7e6a","event_name":"add_to_cart","timestamp":"2026-01-29T14:05:12Z","anonymous_id":"anon_8a9d8f4f","user_id":"f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10","session_id":"sess_001","context":{"user_agent":"Mozilla/5.0","page_url":"https://shop.example.com/product/sku-123","referrer":"https://google.com","locale":"en-US","tz":"UTC+07:00"},"properties":{"sku":"sku-123","price":29.99,"currency":"USD","quantity":1}}'
```

## Architecture

```mermaid
graph LR
  subgraph Client
    SDK[Web Tracking SDK]
  end

  subgraph Ingestion
    API[FastAPI Event Collector]
    Redis[(Redis Streams)]
  end

  subgraph Storage
    PG[(Postgres)]
    CH[(ClickHouse)]
  end

  subgraph Automation
    N8N[n8n Workflows]
  end

  subgraph UI
    Web[Next.js Dashboard]
  end

  SDK -->|HTTP /v1/events| API
  SDK -->|HTTP /v1/identify| API
  API -->|Validate + Enrich| Redis
  API -->|Profiles + Identity| PG
  Redis -->|Ingest Events| CH
  CH -->|Analytics Queries| Web
  PG -->|Profiles + Segments| Web
  API -->|Webhook Triggers| N8N
  N8N -->|Email/SMS/API| Ext[External Services]
```

## Folder Structure

```
apps/
  api/                # FastAPI service
  web/                # Next.js dashboard
packages/
  sdk-web/            # Web Tracking SDK
infra/
  docker-compose/     # MVP docker-compose stack
openspec/             # Specs and project conventions
docs/                 # Docs and sample workflows
```

## Prerequisites

- Docker + Docker Compose
- Python 3.11+
- Node.js 18+ (pnpm recommended)
- Redis CLI (optional for debugging)

## Environment Variables

Create env files based on the examples below.

### `apps/api/.env`

```
API_PORT=8000
JWT_SECRET=change-me
POSTGRES_DSN=postgresql+psycopg://app:app@localhost:5432/cj
CLICKHOUSE_DSN=clickhouse://default:@localhost:8123/cj
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_PER_MIN=120
EVENT_RETENTION_DAYS=90
```

### `apps/web/.env.local`

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_PROVIDER=jwt
```

### `packages/sdk-web/.env`

```
SDK_API_BASE_URL=http://localhost:8000
SDK_WRITE_KEY=dev-write-key
```

### `infra/docker-compose/.env`

```
POSTGRES_DB=cj
POSTGRES_USER=app
POSTGRES_PASSWORD=app
CLICKHOUSE_DB=cj
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
REDIS_PASSWORD=
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin
N8N_WEBHOOK_URL=http://localhost:5678
```

## Local Development (Docker Compose)

From the repo root:

```
Docker compose -f infra/docker-compose/docker-compose.yml up -d
```

Then:

```
# Postgres migrations
cd apps/api
alembic upgrade head

# API
uvicorn app.main:app --reload --port 8000

# Web
cd ../web
pnpm install
pnpm dev

# SDK (optional local build)
cd ../../packages/sdk-web
pnpm install
pnpm build
```

n8n is included in the Compose stack and runs at `http://localhost:5678`.

## ClickHouse Initialization

ClickHouse tables are created via init SQL scripts mounted by Docker Compose or by a dedicated setup step in the API. Alembic only manages Postgres schemas. Ensure ClickHouse tables exist before sending high-volume events.

## Running Services

- API: `http://localhost:8000`
- Web Dashboard: `http://localhost:3000`
- n8n: `http://localhost:5678`

## API Endpoints (MVP)

- `POST /v1/events` - Ingest single or batch events (requires `Idempotency-Key` header)
- `POST /v1/identify` - Link identity attributes to `anonymous_id`
- `GET /v1/users/{id}/timeline` - User journey timeline
- `GET /v1/funnels?from=2026-01-01&to=2026-01-31&steps=page_view,add_to_cart,purchase_success` - Funnel analytics
- `POST /v1/segments/preview` - Segment membership preview

## Sample Event Payload

Event names use snake_case, for example: `page_view`, `sign_up`, `add_to_cart`, `begin_checkout`, `purchase_success`.

```json
{
  "event_id": "f2a1c7c0-9f2c-4c62-9c4a-5a4f9b6d9e7b",
  "event_name": "add_to_cart",
  "timestamp": "2026-01-29T14:05:12Z",
  "anonymous_id": "anon_8a9d8f4f",
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10",
  "session_id": "sess_001",
  "context": {
    "user_agent": "Mozilla/5.0",
    "page_url": "https://shop.example.com/product/sku-123",
    "referrer": "https://google.com",
    "locale": "en-US",
    "tz": "UTC+07:00"
  },
  "properties": {
    "sku": "sku-123",
    "price": 29.99,
    "currency": "USD",
    "quantity": 1
  }
}
```

Note: IP is derived server-side from request headers, not sent by the SDK.

## Identity Resolution (How it Works)

- Every event must include `anonymous_id`.
- `POST /v1/identify` links `anonymous_id` to `user_id`, email, phone, and/or device_id.
- When a match occurs, profiles are merged in Postgres and future events map to the resolved identity.
- Timeline and analytics queries use the resolved user identity for consistent journeys.

## End-to-End Test (curl)

```
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-evt-0002" \
  -d '{"event_id":"2efcab1c-1f7f-4b87-a6b3-1e7e8f2b0b5a","event_name":"page_view","timestamp":"2026-01-29T14:06:12Z","anonymous_id":"anon_8a9d8f4f","context":{"user_agent":"Mozilla/5.0","page_url":"https://shop.example.com/","referrer":"https://google.com","locale":"en-US","tz":"UTC+07:00"},"properties":{"path":"/"}}'
```

## n8n Workflows (Sample)

Recommended location for workflow JSONs: `docs/n8n/`.

Import and run:
1. Open n8n at `http://localhost:5678`
2. Click Import -> upload a JSON workflow from `docs/n8n/`
3. Configure credentials (SMTP, Twilio, internal API keys)
4. Enable workflow and trigger with webhook or cron

Common samples:
- Abandoned cart reminder (webhook -> delay -> email/SMS)
- Onboarding sequence (cron -> segment query -> email series)
- Churn warning (segment preview -> CRM update)

## Troubleshooting

- Events not appearing: check Redis Streams length and ClickHouse connectivity; verify `Idempotency-Key`.
- 401 Unauthorized: ensure JWT secret and token issuer are aligned across API and web.
- No timeline data: confirm identity resolution and that `anonymous_id` is present.
- n8n webhooks fail: verify `N8N_WEBHOOK_URL` and exposed ports.
- ClickHouse errors: confirm database and table creation during initialization.

## Deployment Notes (MVP)

- Use Docker Compose for a single-node deployment.
- Back up Postgres (profiles, segments, workflows) and ClickHouse (events).
- Configure retention via `EVENT_RETENTION_DAYS` and periodic cleanup jobs.
- Put the API and n8n behind a reverse proxy with TLS in production.
- Scale ingest by adding more API workers and Redis Streams consumers.
