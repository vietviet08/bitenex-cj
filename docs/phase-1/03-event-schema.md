# Phase 1 - Event Schema

## Canonical Event Schema

Required fields:
- event_id: string (UUID v4 recommended)
- event_name: string (snake_case)
- timestamp: string (ISO 8601 UTC)
- anonymous_id: string
- context: object
- properties: object

Optional fields:
- user_id: string (UUID)
- email: string
- phone: string
- device_id: string
- session_id: string

## Context Rules

Required context fields:
- user_agent
- page_url
- referrer (can be empty string)
- locale
- tz

Notes:
- Do not send IP from the SDK. IP is derived server-side from request headers.
- Context must be a JSON object, not a string.

## Properties Rules
- Properties must be a JSON object.
- Allowed value types: string, number, boolean, object, array.
- Max event payload size: 32 KB.
- Keep property keys in snake_case.

## Idempotency Strategy
- Every POST /v1/events request must include Idempotency-Key header.
- event_id is also used for deduplication if a key is reused.
- If the same Idempotency-Key is seen again, return 200 with the previous result.

## Validation Rules
- timestamp must be ISO 8601 UTC (e.g., 2026-01-29T14:05:12Z).
- event_name must match ^[a-z0-9_]+$.
- anonymous_id is required for all events.
- user_id must be a UUID if provided.
- properties must be JSON and not exceed 32 KB.

## JSON Examples

### page_view

```json
{
  "event_id": "2efcab1c-1f7f-4b87-a6b3-1e7e8f2b0b5a",
  "event_name": "page_view",
  "timestamp": "2026-01-29T14:06:12Z",
  "anonymous_id": "anon_8a9d8f4f",
  "context": {
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

### add_to_cart

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

### purchase_success

```json
{
  "event_id": "0f7f7c15-8406-4a4d-8c2a-5c4b8a2e8f0d",
  "event_name": "purchase_success",
  "timestamp": "2026-01-29T14:12:40Z",
  "anonymous_id": "anon_8a9d8f4f",
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10",
  "context": {
    "user_agent": "Server",
    "page_url": "https://shop.example.com/checkout/success",
    "referrer": "",
    "locale": "en-US",
    "tz": "UTC+07:00"
  },
  "properties": {
    "order_id": "order_1000123",
    "total": 89.97,
    "currency": "USD",
    "item_count": 3
  }
}
```
