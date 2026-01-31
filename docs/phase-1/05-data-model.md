# Phase 1 - Data Model

## Postgres (Profiles, Identity, Segments, Workflows)

Minimal schema for MVP. Use Alembic for migrations.

### users
- id UUID PRIMARY KEY
- email TEXT UNIQUE NULL
- phone TEXT UNIQUE NULL
- created_at TIMESTAMP WITH TIME ZONE NOT NULL
- updated_at TIMESTAMP WITH TIME ZONE NOT NULL

### identities
- id UUID PRIMARY KEY
- anonymous_id TEXT UNIQUE NOT NULL
- user_id UUID NULL REFERENCES users(id)
- email TEXT NULL
- phone TEXT NULL
- device_id TEXT NULL (mobile or desktop device identifier)
- first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL
- last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL

Indexes and constraints:
- UNIQUE(anonymous_id)
- INDEX(user_id)
- INDEX(email), INDEX(phone)

### segments
- id UUID PRIMARY KEY
- name TEXT UNIQUE NOT NULL
- definition_json JSONB NOT NULL
- created_at TIMESTAMP WITH TIME ZONE NOT NULL
- updated_at TIMESTAMP WITH TIME ZONE NOT NULL

### workflows
- id UUID PRIMARY KEY
- name TEXT NOT NULL
- type TEXT NOT NULL
- n8n_workflow_id TEXT NOT NULL
- enabled BOOLEAN NOT NULL DEFAULT true
- config_json JSONB NULL
- created_at TIMESTAMP WITH TIME ZONE NOT NULL
- updated_at TIMESTAMP WITH TIME ZONE NOT NULL

## ClickHouse (Event Logs and Analytics)

Append-only events table for high-volume analytics.

### events

Example DDL:

```sql
CREATE TABLE IF NOT EXISTS events (
  event_id String,
  event_name String,
  timestamp DateTime,
  anonymous_id String,
  user_id Nullable(String),
  session_id Nullable(String),
  context Map(String, String),
  properties String
)
ENGINE = MergeTree
PARTITION BY toDate(timestamp)
ORDER BY (event_name, anonymous_id, user_id, timestamp)
TTL timestamp + INTERVAL 90 DAY;
```

Notes:
- properties may be stored as JSON string for MVP; later can use JSON type.
- TTL uses EVENT_RETENTION_DAYS.
- context stored as Map for simple lookups.

## Indexing and Partitioning
- Partition by date: toDate(timestamp)
- Sort key optimized for event_name and identity lookups
- Use TTL for retention

## Retention Policy
- Controlled by EVENT_RETENTION_DAYS (default 90 days).
- Postgres profiles and identities retained until deletion request.

## What Lives Where
- Postgres: user profiles, identities, segments, workflow metadata
- ClickHouse: raw event logs and analytics queries
