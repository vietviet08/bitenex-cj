# Phase 1 - Event Taxonomy

## Naming Conventions
- Use snake_case for event names (e.g., page_view, sign_up, add_to_cart).
- Keep names short and action-focused (verb_noun).
- Avoid spaces, dots, or camelCase.
- Keep properties consistent across events (sku, price, currency, order_id).

## Event Sources

Frontend (Web SDK)
- Used for browser events such as page_view, add_to_cart, begin_checkout.
- SDK can be embedded into any website, including Spring Boot + Thymeleaf pages.
- SDK should not send raw IP; IP is derived server-side from request headers.

Backend (Server-side tracking)
- Used for authoritative events such as purchase_success or sign_up confirmation.
- Recommended for events that require guaranteed delivery or trusted data.

## MVP Event List

| Event Name       | Source   | Required Properties                     | Notes |
|-----------------|----------|------------------------------------------|-------|
| page_view       | Frontend | path                                      | page view in the browser |
| sign_up         | Backend  | method                                   | method = email, google, etc |
| login           | Backend  | method                                   | used for identity linking |
| add_to_cart     | Frontend | sku, price, currency, quantity           | capture item added |
| begin_checkout  | Frontend | cart_value, currency                     | first checkout step |
| purchase_success| Backend  | order_id, total, currency, item_count    | final purchase confirmation |

## Required Properties (Definitions)
- path: URL path or route, e.g. "/pricing"
- method: sign_up or login method, e.g. "email" or "google"
- sku: product SKU
- price: numeric unit price
- currency: ISO 4217 code, e.g. "USD"
- quantity: integer
- cart_value: numeric total
- order_id: order identifier (string)
- total: numeric order total
- item_count: integer count of items

## PII Guidance
- Avoid sending raw personal data in event properties.
- Prefer pseudonymous IDs (anonymous_id, user_id UUID).
- If email or phone are present, use POST /v1/identify instead of embedding them in event properties.
