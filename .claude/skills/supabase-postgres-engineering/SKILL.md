---
name: supabase-postgres-engineering
description: Design and implement optional EcoSort AI persistence features using Supabase and PostgreSQL, including schema, RLS, migrations, and privacy controls.
---

# Supabase and PostgreSQL Engineering

## Scope

Supabase is optional for the scan-only MVP. Introduce it only when an approved feature needs persistence, such as user accounts, saved scans, or scan history.

## Design principles

- Model only data required by an approved feature.
- Use migrations for schema changes.
- Define primary keys, foreign keys, constraints, indexes, and deletion behavior.
- Keep model outputs versioned so historical results remain interpretable.
- Store minimal metadata; avoid storing raw images unless explicitly required.
- Define retention and deletion behavior before enabling history.

## Security

- Enable Row Level Security on user-accessible tables.
- Write policies that enforce ownership on every read/write path.
- Never ship the Supabase service-role key in the mobile app.
- Use public/anon keys only with appropriate RLS policies.
- Keep secrets in server-side environment configuration.
- Test policies as both authorized and unauthorized users.

## Suggested entities

Only if the feature is approved, consider:
- `profiles`
- `scans`
- `detections` or a structured JSON result field

Do not create all of these automatically. Choose normalized rows versus JSON based on query requirements and document the trade-off.

## Operational standards

Use local/dev/staging/production separation where feasible. Include migration rollback or recovery considerations, backups, and schema-change tests. Do not manually edit production schema without a migration record.

## Deliverables

Provide schema diagram or table definitions, migrations, RLS policies, policy tests, environment variable names (never values), and a privacy/data-retention note.
