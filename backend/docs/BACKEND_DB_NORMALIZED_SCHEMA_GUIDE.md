# Backend Normalized Schema (nexus_norm) Guide

<!--nav-->
[Previous](BACKEND_CHANGELOG.md) | [Next](BACKEND_EMAIL_LOCAL_TESTING_GUIDE.md) | [Home](/README.md)

---
<!--/nav-->


This repo contains a **proposed normalized schema** in `db_normalized/new_db_schema.sql`.

To avoid breaking the current website behavior (and to avoid frontend changes), the backend introduces this schema **side-by-side** under a separate PostgreSQL schema named `nexus_norm`.

## What This Change Does (and Does Not Do)

**Does:**
- Adds an Alembic revision that can create the `nexus_norm` schema + tables from `db_normalized/new_db_schema.sql`.
- Adds a small set of SQLAlchemy model stubs under `backend/app/models/nexus_norm/` for future incremental adoption.

**Does not (yet):**
- Migrate any production data from `public.*` into `nexus_norm.*`.
- Switch the running API to read/write `nexus_norm.*`.
- Change any frontend-facing REST routes, request bodies, or response shapes.

## How To Apply The Migration

From `backend/`:

1. Ensure `DATABASE_URL` points at the DB you want to migrate.
2. Run:
   - `alembic upgrade head`

The revision `backend/alembic/versions/f19c2a7b3d10_create_nexus_norm_schema.py` reads and executes `db_normalized/new_db_schema.sql` statement-by-statement.

## How To Verify

In psql:
- `\\dn` should show `nexus_norm`
- `\\dt nexus_norm.*` should show the normalized tables (e.g. `schools`, `users`, `events`, â€¦)

## Notes / Caveats

- The SQL includes `CREATE EXTENSION IF NOT EXISTS citext;`. On some managed Postgres providers this requires elevated privileges.
- Because this is side-by-side, the current app can continue using `public.*` tables until the backend is explicitly updated to cut over.

## Optional Settings (No Behavior Change By Default)

The backend settings now include:
- `NEXUS_NORM_ENABLED` (default: false)
- `NEXUS_NORM_SCHEMA` (default: `nexus_norm`)

These are placeholders for a future backend cutover; current endpoints still use `public.*`.

