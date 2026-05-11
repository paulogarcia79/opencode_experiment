## Parent

[PRD-background-job-queue.md](../prd/PRD-background-job-queue.md)

## What to build

Set up the core infrastructure for background jobs. This includes adding Redis to the Docker Compose stack, installing `arq`, and evolving the database schema to support job tracking.

## Acceptance criteria

- [ ] Redis 7 service added to `docker-compose.dev.yml` and `docker-compose.prod.yml`.
- [ ] `arq` added to `pyproject.toml` dependencies.
- [ ] `NewsletterSend` model updated with `status` (Enum: pending, sent, failed), `error_message`, and `scheduled_at`.
- [ ] Alembic migration generated and applied to update the schema.
- [ ] Redis connection utility implemented in `app/redis.py`.

## Blocked by

None - can start immediately
