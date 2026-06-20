# MailMind AI Release Guide

## Environment Setup

Create a backend environment with Python dependencies installed from `backend/requirements.txt`.

Required backend environment variables:

- `APP_NAME`
- `DATABASE_URL`
- `SECRET_KEY` or `JWT_SECRET`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `GEMINI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `CHROMA_DB_PATH` or `CHROMA_PATH`
- `CHROMA_EMAIL_COLLECTION`
- `SUPABASE_URL`
- `SUPABASE_KEY`

Optional production controls:

- `ENVIRONMENT=production`
- `DEMO_CLEANUP_GRACE_HOURS=24`
- `EXPIRED_USER_CLEANUP_INTERVAL_SECONDS=3600`

## Migration Execution

From the backend directory:

```bash
alembic upgrade head
```

Always run migrations before starting a backend version that depends on new schema fields.

## Backend Startup

Development startup:

```bash
uvicorn app.main:app --reload
```

Production startup should use the hosting platform's ASGI process manager. The backend must be started with production environment variables already loaded.

## Production Environment Variables

Store secrets in the deployment platform's secret manager or environment variable store. Do not commit `.env` files containing production values.

Use `JWT_SECRET` or `SECRET_KEY` for signing access tokens. Use `CHROMA_PATH` or `CHROMA_DB_PATH` for Chroma persistence. Supabase credentials should stay backend-only.

## Validation Checklist

Before release:

- Run `python -m compileall app`.
- Run `alembic upgrade head`.
- Start the backend.
- Verify `/docs` loads.
- Verify registration and login.
- Verify protected APIs reject expired users.
- Verify expired users can submit feedback.
- Verify cleanup waits for feedback submission or the grace period.
- Verify logs are generated and contain no secrets.

## APK Release Preparation Dependencies

APK release preparation belongs to the Flutter project and should happen after backend validation. Required dependencies usually include:

- Flutter SDK
- Android SDK
- Java/JDK compatible with the Flutter version
- Android signing key and signing configuration
- Production API base URL configuration

Do not embed backend secrets, Gemini keys, database credentials, Supabase service keys, or Google client secrets in the APK.

## Release Notes

For each backend release, record:

- Git revision
- Migration head
- Environment name
- API base URL
- Known risks
- Rollback plan
