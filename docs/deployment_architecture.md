# MailMind AI Deployment Architecture

## System Overview

MailMind AI is composed of a Flutter mobile client, a FastAPI backend, Supabase/PostgreSQL persistence, Gemini AI services, ChromaDB vector storage, a lightweight backend scheduler, and rotating file logs.

```text
Flutter APK
  -> FastAPI backend
  -> Supabase / PostgreSQL
  -> Gemini API
  -> ChromaDB
  -> Scheduler
  -> Rotating logs
```

## Components

### Flutter APK

The Flutter APK is the mobile client. It should call the FastAPI API over HTTPS and store only short-lived user session data locally. Demo-expired and feedback UI flows should remain client features layered over backend responses.

### FastAPI Backend

FastAPI owns authentication, Gmail integration, email ingestion, summarization, RAG, agent orchestration, demo lifecycle enforcement, feedback submission, cleanup, and logging.

The backend should run behind a production HTTP server or platform-managed ASGI runtime with TLS termination, health checks, and environment-based configuration.

### Supabase / PostgreSQL

PostgreSQL stores users, Gmail tokens/accounts, emails, memories, actions, and feedback. Alembic is the source of truth for schema changes.

Supabase can provide the managed PostgreSQL database. Application access should use service credentials stored only as environment variables.

### Gemini

Gemini powers email summarization, agent reasoning, action extraction, and embeddings. The Gemini API key must be provided through the backend environment and must never be logged or shipped in the mobile app.

### ChromaDB

ChromaDB stores email vectors with metadata including `user_id` and `email_id`. Cleanup deletes vectors by `user_id` metadata. For production, use persistent storage with backups aligned to the database retention policy.

### Scheduler

The backend scheduler runs in-process and periodically:

1. Marks expired demo users.
2. Assigns a one-time cleanup grace timestamp.
3. Cleans users only after feedback is submitted or the grace period passes.

For multi-instance production deployments, run only one scheduler instance or move the scheduler into a single worker process to avoid duplicate cleanup attempts.

### Logging

Backend logs use a rotating file handler under `logs/`. Logs should record operational events without secrets, tokens, email body content, or full OAuth URLs.

## Deployment Recommendations

- Run the backend with production environment variables, not `.env` files committed to source control.
- Use HTTPS for all mobile-to-backend traffic.
- Run Alembic migrations before serving a new backend version.
- Keep Gemini, database, Supabase, and Google OAuth credentials out of the APK.
- Configure log collection and rotation at the hosting platform level in addition to app-level rotation.
- Ensure ChromaDB persistent storage is mounted on durable disk.
- If scaling FastAPI horizontally, isolate the cleanup scheduler to a single instance.
