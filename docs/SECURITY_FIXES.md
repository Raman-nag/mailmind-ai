# Security Fixes

## Files Modified

- `backend/app/api/v1/gmail.py`
- `backend/app/core/config/base.py`
- `backend/app/core/config/production.py`
- `backend/app/main.py`
- `backend/app/models/__init__.py`
- `backend/app/models/oauth_state.py`
- `backend/app/repositories/oauth_state_repository.py`
- `backend/alembic/versions/c4b7f2a9d8e1_create_oauth_states_table.py`
- `backend/.env.production.example`
- `render.yaml`
- `deployment/render_deployment.md`
- `docs/SECURITY_FIXES.md`

## Risks Mitigated

### Gmail OAuth user binding

Gmail OAuth tokens are no longer stored against the hardcoded `test@mailmind.ai` account. `/api/v1/gmail/connect` now requires the authenticated backend user and creates an OAuth state record tied to that user's `user_id`. `/api/v1/gmail/callback` resolves the callback user from the validated state record before storing tokens.

### OAuth state validation

OAuth state is now generated with `secrets.token_urlsafe(32)`, persisted in the new `oauth_states` table, sent to Google during authorization, and required on callback. Missing, unknown, used, or expired states are rejected. States expire after 10 minutes and are marked used after successful token storage.

### Token exchange validation

The Gmail callback now checks Google token exchange HTTP status with `raise_for_status()`, rejects OAuth error payloads, requires an `access_token`, and uses a request timeout. Existing refresh tokens are preserved when Google does not return a new refresh token.

### Production secret validation

`ProductionSettings` now fails startup when `SECRET_KEY` is shorter than 32 characters. This prevents production deployments from starting with weak JWT signing secrets.

### Configurable CORS

CORS allowed origins are now driven by `CORS_ALLOWED_ORIGINS`. The setting accepts a comma-separated environment value and is passed into FastAPI's CORS middleware. Render now declares `CORS_ALLOWED_ORIGINS` as a manually supplied environment variable.

## Remaining Deferred Risks

These risks remain intentionally deferred because they were outside Sprint 9 Stage 6B scope:

- Gmail access and refresh tokens are still stored without application-level encryption.
- Login and registration endpoints still need rate limiting and brute-force controls.
- PKCE remains disabled in the Google OAuth flow.
- JWTs still use minimal claims and email-based `sub` values.
- Detailed health endpoints and API docs may still expose operational information if left public.
- Password policy remains permissive.

## Migration Impact

A new Alembic migration creates the `oauth_states` table. Deployments must run migrations before using Gmail OAuth connect/callback in production.

Migration file:

```text
backend/alembic/versions/c4b7f2a9d8e1_create_oauth_states_table.py
```

The migration is additive and does not alter existing users, Gmail tokens, emails, or RAG data.

## Deployment Notes

Set `CORS_ALLOWED_ORIGINS` in Render to the production frontend origins, separated by commas:

```bash
CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
```

Set `SECRET_KEY` to a production-only random value of at least 32 characters. Shorter values now fail startup in production.