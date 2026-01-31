# Alembic Migrations

This folder contains Alembic migrations for the Postgres schema used by the API.

## Prerequisites
- Create `apps/api/.env` (or copy from `.env.example`) and set Postgres settings.

## Common Commands

From `apps/api`:

```bash
# Create a new migration (autogenerate from models)
alembic revision --autogenerate -m "describe change"

# Apply all migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Show current DB revision
alembic current

# Show history
alembic history
```

## Notes
- `alembic.ini` points to `migrations/`.
- The migration environment loads settings from `.env` via `app.core.config`.
