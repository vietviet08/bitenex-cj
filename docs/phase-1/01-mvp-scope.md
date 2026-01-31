# Phase 1 - MVP Scope

## Goals
- Deliver a working Customer Journey Tracking and Automation MVP in 6 to 8 weeks.
- Enable event tracking via a JavaScript Web SDK embedded in any website (including Spring Boot + Thymeleaf pages) and a React Native SDK for mobile apps (customer, merchant, driver).
- Provide identity resolution (anonymous_id to user_id/email/phone/device_id mapping).
- Provide analytics views: user timeline, funnels, segment preview.
- Trigger automation workflows through n8n (abandoned cart, onboarding, churn warning).

## Non-Goals
- Real-time streaming analytics at massive scale (Kafka, Flink) beyond MVP needs.
- Advanced ML models for churn prediction or personalization.
- Multi-tenant enterprise controls (SAML, SCIM, custom RBAC policies).
- Native iOS/Android SDKs (Swift/Kotlin) beyond the React Native SDK.
- Full data warehouse export and BI tooling.

## Minimum Feature Set

Tracking
- Web Tracking SDK sends events to the FastAPI collector.
- React Native Tracking SDK sends events to the FastAPI collector.
- Collector validates, enriches, and enqueues events via Redis Streams.
- Events are stored in ClickHouse for analytics.

Identity Resolution
- anonymous_id is required for all events.
- POST /v1/identify links anonymous_id to user_id/email/phone/device_id.
- Identity merges ensure consistent journeys across sessions and logins.

Analytics
- User journey timeline (GET /v1/users/{id}/timeline).
- Funnel analytics with steps and date range (GET /v1/funnels).
- Segment preview (POST /v1/segments/preview).

Automation (n8n)
- Abandoned cart reminder.
- Onboarding sequence.
- Churn warning (basic rule-based trigger).

## Deliverables Checklist
- [ ] Web Tracking SDK package with README and sample usage
- [ ] React Native Tracking SDK package with README and sample usage
- [ ] FastAPI Event Collector with validation, enrichment, and Redis Streams ingest
- [ ] Postgres schema for users, identities, segments, workflows (Alembic)
- [ ] ClickHouse events table and init scripts
- [ ] Basic identity resolution and merge rules
- [ ] Analytics endpoints for timeline, funnel, and segment preview
- [ ] n8n workflows for abandoned cart and onboarding
- [ ] Next.js dashboard with timeline, funnel, and segment preview pages
- [ ] Docker Compose stack for local dev and single-node MVP deploy
- [ ] End-to-end test script using curl
