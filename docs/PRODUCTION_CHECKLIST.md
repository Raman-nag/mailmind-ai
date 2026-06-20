# Production Checklist

## Environment Verification

- `ENVIRONMENT=production` is set in Render.
- Render service uses the expected start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Render health check path is configured intentionally.
- No local `.env` file is committed or copied into the image.
- Runtime logs confirm the app started in production mode.
- API docs exposure is intentionally disabled, protected, or accepted for the release.

## Secret Verification

- `SECRET_KEY` is production-only, randomly generated, and at least 32 bytes of entropy.
- `DATABASE_URL` points to the production Supabase/PostgreSQL database.
- `GEMINI_API_KEY` is valid, backend-only, and not embedded in the APK.
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` match the production Google OAuth app.
- `SUPABASE_URL` and `SUPABASE_KEY` are set in Render only.
- No real secrets appear in `render.yaml`, docs, source files, logs, APK assets, or git history.
- Secrets are rotated after any accidental exposure.

## OAuth Verification

- `GOOGLE_REDIRECT_URI` is HTTPS and matches Google Cloud Console exactly.
- `OAUTHLIB_INSECURE_TRANSPORT` is not set in production.
- Gmail OAuth state is generated, persisted/signed, and validated on callback before launch.
- Gmail OAuth callback binds tokens to the authenticated user, not a hardcoded account.
- PKCE is enabled for OAuth authorization code flow.
- Token exchange checks HTTP status and rejects OAuth error responses.
- Gmail refresh tokens are encrypted at rest or protected by an approved equivalent control.
- OAuth logs do not include authorization codes, access tokens, refresh tokens, or full callback URLs.

## Database Verification

- Alembic migrations have been run against production.
- Production database access is restricted to required services and operators.
- Supabase automated backups or point-in-time recovery are enabled according to the project plan.
- Gmail token tables and sensitive columns have encryption/rotation controls planned.
- Application database user has the least privileges needed by the backend.
- `/api/v1/health/db` is removed, protected, or accepted as a documented temporary risk.

## Chroma Verification

- `CHROMA_DB_PATH=/var/data/chromadb` is set in Render.
- Render persistent disk `mailmind-chromadb` is mounted at `/var/data`.
- Chroma data survives restart and redeploy in a staging verification.
- Chroma backup and restore process from `docs/BACKUP_RECOVERY.md` has been tested.
- Local `backend/chromadb/` data is not committed.
- Backend is not horizontally scaled while using a single attached Chroma disk.

## APK Verification

- APK points only to the production HTTPS backend URL.
- APK does not contain `GEMINI_API_KEY`, `SUPABASE_KEY`, Google client secret, database URL, or JWT secret.
- APK does not use localhost, emulator, or staging backend URLs for release builds.
- OAuth redirect/deep-link behavior matches the production Google OAuth configuration.
- Release build uses production signing keys and secure build pipeline storage.
- Debug logging is disabled or minimized in release builds.
- Network traffic from the APK is HTTPS-only except for explicitly approved development builds.

## Final Release Gate

- Critical and High findings in `docs/SECURITY_REVIEW.md` are fixed or explicitly risk-accepted.
- Render environment values are reviewed by two maintainers.
- A smoke test covers register, login, authenticated API access, Gmail connect, email sync, RAG query, and health check.
- Logs from the smoke test contain no secrets, tokens, email bodies, or OAuth callback URLs.
- Backup and recovery instructions have a named owner and tested schedule.