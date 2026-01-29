# Phase 1 - Journey Scenarios

## Journey 1: Abandoned Cart

Trigger condition
- Event: add_to_cart
- No purchase_success within 2 hours

Time window
- Evaluate within 2 hours after add_to_cart

Segment definition
- Users with add_to_cart in last 2 hours
- Exclude users with purchase_success in same window

Dedupe rules
- One workflow per user_id or anonymous_id per 24 hours
- Dedupe key: abandoned_cart:{user_id|anonymous_id}:{date}

Action outcome
- Send reminder email or SMS
- Optional follow-up after 24 hours if no purchase_success

Sample webhook payload to n8n

```json
{
  "journey": "abandoned_cart",
  "trigger_event": "add_to_cart",
  "event_time": "2026-01-29T14:05:12Z",
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10",
  "anonymous_id": "anon_8a9d8f4f",
  "segment_id": "seg_abandoned_cart",
  "dedupe_key": "abandoned_cart:f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10:2026-01-29",
  "properties": {
    "sku": "sku-123",
    "price": 29.99,
    "currency": "USD",
    "quantity": 1
  }
}
```

## Journey 2: Onboarding

Trigger condition
- Event: sign_up
- No purchase_success within 7 days

Time window
- Evaluate daily for 7 days after sign_up

Segment definition
- Users with sign_up in last 7 days
- Exclude users with purchase_success

Dedupe rules
- One onboarding workflow per user_id
- Dedupe key: onboarding:{user_id}

Action outcome
- Send welcome email sequence
- Invite user to complete profile

Sample webhook payload to n8n

```json
{
  "journey": "onboarding",
  "trigger_event": "sign_up",
  "event_time": "2026-01-29T09:15:00Z",
  "user_id": "5d90c3d9-bb7c-4a6e-9f8f-3c45e2a6b2d1",
  "anonymous_id": "anon_5c2a1d3f",
  "segment_id": "seg_onboarding",
  "dedupe_key": "onboarding:5d90c3d9-bb7c-4a6e-9f8f-3c45e2a6b2d1",
  "properties": {
    "method": "email"
  }
}
```
