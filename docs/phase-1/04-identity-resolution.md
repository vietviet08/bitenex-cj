# Phase 1 - Identity Resolution

## Definitions
- anonymous_id: client-generated ID for a browser/device.
- user_id: stable UUID for a known user.
- email: optional login identifier (avoid in raw events).
- phone: optional login identifier (avoid in raw events).
- device_id: optional device identifier (mobile or desktop fingerprint). For React Native, prefer a stable installation_id stored on device.

## Merge Rules
- anonymous_id is required for all events.
- POST /v1/identify links anonymous_id to user_id/email/phone/device_id.
- React Native SDK should persist anonymous_id locally (e.g., AsyncStorage) to survive app restarts.
- When identify is called, the system:
  - creates or updates the user record (users table)
  - upserts the mapping in identities table
  - marks the resolved user_id as the primary identity for future events
- Events in ClickHouse are not rewritten; analytics queries resolve identity by joining the identities mapping.

## Example Flow

1) First visit
- Event: page_view
- anonymous_id = anon_8a9d8f4f
- user_id not present

2) Add to cart
- Event: add_to_cart
- anonymous_id still anon_8a9d8f4f

3) Login
- Backend emits login event
- API call POST /v1/identify with anonymous_id and user_id

4) Purchase
- Event: purchase_success
- user_id is now included in events

Result: timeline and analytics show a single journey tied to user_id.

## Postgres Tables Involved

users
- id (UUID, primary key)
- email (nullable, unique)
- phone (nullable, unique)
- created_at

identities
- id (UUID, primary key)
- anonymous_id (unique, required)
- user_id (UUID, foreign key to users.id)
- email (nullable)
- phone (nullable)
- device_id (nullable)
- first_seen_at
- last_seen_at

## Merge Behavior
- If anonymous_id already maps to a user_id, reuse that mapping.
- If a new user_id is provided, set it as the primary for that anonymous_id.
- If email/phone matches an existing user, link anonymous_id to that user.
- No hard deletes; merges are recorded via updated identities rows.
