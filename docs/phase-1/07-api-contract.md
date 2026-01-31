# Phase 1 - API Contract

## Endpoints (MVP)
- POST /v1/events
- POST /v1/identify
- GET /v1/users/{id}/timeline
- GET /v1/funnels
- POST /v1/segments/preview

## Auth and RBAC
- API uses JWT for authentication.
- Roles: admin, analyst, operator (basic RBAC).
- Write endpoints require operator or admin.
- Analytics endpoints require analyst or admin.

Events can be sent from Web SDK, React Native SDK, or server-side tracking.

## POST /v1/events

Request (single event)

```json
{
  "event_id": "2efcab1c-1f7f-4b87-a6b3-1e7e8f2b0b5a",
  "event_name": "page_view",
  "timestamp": "2026-01-29T14:06:12Z",
  "anonymous_id": "anon_8a9d8f4f",
  "context": {
    "platform": "web",
    "user_agent": "Mozilla/5.0",
    "page_url": "https://shop.example.com/",
    "referrer": "https://google.com",
    "locale": "en-US",
    "tz": "UTC+07:00"
  },
  "properties": {
    "path": "/"
  }
}
```

Headers
- Idempotency-Key: unique key for the request

Response

```json
{
  "status": "ok",
  "ingested": 1,
  "event_ids": ["2efcab1c-1f7f-4b87-a6b3-1e7e8f2b0b5a"]
}
```

## POST /v1/identify

Request

```json
{
  "anonymous_id": "anon_8a9d8f4f",
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10",
  "email": "user@example.com",
  "phone": "+12065550123",
  "device_id": "device_001"
}
```

Response

```json
{
  "status": "ok",
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10"
}
```

## GET /v1/users/{id}/timeline

Response

```json
{
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10",
  "events": [
    {
      "event_name": "page_view",
      "timestamp": "2026-01-29T14:06:12Z",
      "properties": {"path": "/"}
    },
    {
      "event_name": "add_to_cart",
      "timestamp": "2026-01-29T14:05:12Z",
      "properties": {"sku": "sku-123", "price": 29.99}
    }
  ]
}
```

## GET /v1/funnels

Query params
- from: 2026-01-01
- to: 2026-01-31
- steps: page_view,add_to_cart,purchase_success

Response

```json
{
  "from": "2026-01-01",
  "to": "2026-01-31",
  "steps": ["page_view", "add_to_cart", "purchase_success"],
  "counts": [1000, 320, 120]
}
```

## POST /v1/segments/preview

Request

```json
{
  "name": "cart_no_purchase_2h",
  "definition": {
    "include": {
      "event": "add_to_cart",
      "within_minutes": 120
    },
    "exclude": {
      "event": "purchase_success",
      "within_minutes": 120
    }
  }
}
```

Response

```json
{
  "segment_id": "seg_cart_no_purchase_2h",
  "estimated_users": 58
}
```

## Standard Error Format

```json
{
  "error_code": "validation_error",
  "message": "Invalid payload",
  "details": {
    "field": "timestamp",
    "reason": "must be ISO 8601 UTC"
  }
}
```

## Conventions and Constraints
- Use snake_case for event names and property keys.
- Avoid sensitive PII in raw events; use identify endpoint instead.
- Payload size limit: 32 KB per event.
- Timestamp must be ISO 8601 UTC format.
