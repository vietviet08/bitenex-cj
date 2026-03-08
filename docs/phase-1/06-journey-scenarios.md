# Phase 1 - Journey Scenarios

Note: Journeys can be triggered by events from both Web and React Native SDKs, as well as server-side events.

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

## Journey 3: Onboarding to First Order

Trigger condition

- Event: sign_up
- No purchase_success within the initial activation window

Time window

- First check after 10 minutes
- Follow-up after 6 hours if no first order exists

Segment definition

- Users with sign_up in the last 24 hours
- Exclude users with purchase_success

Dedupe rules

- One workflow per user_id per sign-up lifecycle
- Dedupe key: onboarding_first_order:{user_id}

Action outcome

- Send welcome nudge shortly after signup
- Issue first-order voucher if still inactive

Sample webhook payload to n8n

```json
{
  "journey": "onboarding_first_order",
  "trigger_event": "sign_up",
  "event_time": "2026-03-08T09:15:00Z",
  "user_id": "5d90c3d9-bb7c-4a6e-9f8f-3c45e2a6b2d1",
  "anonymous_id": "anon_5c2a1d3f",
  "segment_id": "seg_onboarding_first_order",
  "dedupe_key": "onboarding_first_order:5d90c3d9-bb7c-4a6e-9f8f-3c45e2a6b2d1",
  "properties": {
    "city": "HCM",
    "platform": "mobile",
    "deep_link": "bitenex://home"
  }
}
```

## Journey 4: Abandoned Checkout Recovery

Trigger condition

- Event: begin_checkout
- No purchase_success within 30 minutes

Time window

- First reminder after 30 minutes
- Recovery offer after 2 hours if no conversion

Segment definition

- Users with begin_checkout in the last 2 hours
- Exclude users with purchase_success in the same checkout lifecycle

Dedupe rules

- One recovery workflow per checkout session
- Dedupe key: abandoned_checkout:{checkout_session_id}

Action outcome

- Send checkout reminder push or email
- Send recovery offer if still abandoned

Sample webhook payload to n8n

```json
{
  "journey": "abandoned_checkout_recovery",
  "trigger_event": "begin_checkout",
  "event_time": "2026-03-08T14:05:12Z",
  "user_id": "f9c6e2b0-2a28-4d54-95a1-2d7e8e2d3a10",
  "anonymous_id": "anon_8a9d8f4f",
  "segment_id": "seg_abandoned_checkout",
  "dedupe_key": "abandoned_checkout:chk_456",
  "properties": {
    "checkout_session_id": "chk_456",
    "cart_value": 185000,
    "currency": "VND",
    "merchant_name": "Bun Cha Ha Noi",
    "deep_link": "bitenex://checkout"
  }
}
```

## Journey 5: Delivered to Review and Reorder

Trigger condition

- Event: order_delivered

Time window

- Review request after 20 minutes
- Review reminder after 24 hours if no review
- Reorder reminder after 3 days if positive review but no reorder

Segment definition

- Users with delivered orders
- Branch by review status and review rating

Dedupe rules

- One workflow per delivered order
- Dedupe key: delivered_review_reorder:{order_id}

Action outcome

- Ask for review
- Issue reorder voucher on positive review
- Send reorder reminder if user does not come back

Sample webhook payload to n8n

```json
{
  "journey": "delivered_review_reorder",
  "trigger_event": "order_delivered",
  "event_time": "2026-03-08T18:25:00Z",
  "user_id": "8bc2af21-2e3a-4e70-9e38-9987a88fd101",
  "segment_id": "seg_delivered_review_reorder",
  "dedupe_key": "delivered_review_reorder:ord_789",
  "properties": {
    "order_id": "ord_789",
    "merchant_name": "Com Tam 24h",
    "deep_link_review": "bitenex://order/food-rating",
    "deep_link_reorder": "bitenex://home"
  }
}
```
