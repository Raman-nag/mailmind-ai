# Security Review

## Scope

Reviewed backend authentication, JWT handling, secret management, OAuth configuration, CORS, environment usage, production settings, logging, health endpoints, Chroma persistence, and Render deployment configuration.

Primary files reviewed:

- `backend/app/main.py`
- `backend/app/core/config/base.py`
- `backend/app/core/config/development.py`
- `backend/app/core/config/production.py`
- `backend/app/core/security.py`
- `backend/app/core/logging.py`
- `backend/app/dependencies/auth.py`
- `backend/app/middleware/demo_access_validator.py`
- `backend/app/middleware/error_logging.py`
- `backend/app/api/v1/auth.py`
- `backend/app/api/v1/gmail.py`
- `backend/app/api/v1/health.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/google_oauth_service.py`
- `backend/app/services/google_credentials_service.py`
- `backend/app/services/health_service.py`
- `backend/app/models/gmail_token.py`
- `backend/app/db/session.py`
- `backend/.env.production.example`
- `backend/Dockerfile`
- `render.yaml`
- `.gitignore`
- `deployment/render_deployment.md`
- production docs under `docs/`

## Findings

### 1. OAuth insecure transport was forced globally

Severity: High

Evidence: `backend/app/main.py` previously set `OAUTHLIB_INSECURE_TRANSPORT=1` at import time for all environments.

Risk: OAuth libraries may allow non-HTTPS OAuth redirects or token exchange behavior in production, weakening Google OAuth transport guarantees.

Status: Fixed. The setting is now enabled only when `ENVIRONMENT` is not `production`.

Recommended fix: Keep `ENVIRONMENT=production` on Render and ensure Google OAuth redirect URIs use HTTPS only.

### 2. Gmail OAuth callback is not bound to the authenticated user

Severity: Critical

Evidence: `backend/app/api/v1/gmail.py` stores callback tokens against hardcoded email `test@mailmind.ai`.

Risk: OAuth tokens can be associated with the wrong account. In production, this can cause cross-user token assignment, broken account linking, or unauthorized Gmail access if the test user exists.

Recommended fix: Replace the hardcoded user lookup with a state-bound OAuth flow. Generate and persist a signed, expiring state value tied to the authenticated user before redirecting to Google, then validate it in the callback before saving tokens.

### 3. OAuth state is returned but not validated

Severity: Critical

Evidence: `/api/v1/gmail/connect` returns `state`, but `/api/v1/gmail/callback` does not read or validate `state`.

Risk: The OAuth flow is vulnerable to CSRF/account-linking attacks. An attacker can potentially cause a victim session or backend callback to accept an authorization code from an unrelated Google account.

Recommended fix: Persist state server-side or issue a signed state token containing user ID, nonce, expiration, and intended redirect. Validate state before token exchange and reject missing, expired, or mismatched state.

### 4. PKCE is explicitly disabled for Google OAuth

Severity: High

Evidence: `backend/app/services/google_oauth_service.py` sets `flow.autogenerate_code_verifier = False` with a comment saying PKCE is disabled.

Risk: Authorization code interception is easier to exploit. PKCE is especially important for mobile/client-initiated OAuth flows.

Recommended fix: Enable PKCE and store/validate the code verifier through the OAuth flow. Use Google OAuth best practices for installed/mobile clients and backend-assisted OAuth.

### 5. Gmail OAuth callback does not validate token exchange success

Severity: High

Evidence: `backend/app/api/v1/gmail.py` calls `requests.post(...).json()` and then stores `access_token` / `refresh_token` without checking HTTP status, `error`, or required fields.

Risk: Failed token exchanges can create invalid token records. Error responses may be treated as successful callbacks.

Recommended fix: Call `raise_for_status()`, reject OAuth error responses, validate required token fields, and log sanitized error categories only.

### 6. Gmail tokens are stored in plaintext

Severity: High

Evidence: `backend/app/models/gmail_token.py` stores `access_token` and `refresh_token` as plain `String` columns.

Risk: A database leak exposes live or refreshable Google tokens.

Recommended fix: Encrypt OAuth tokens at rest using envelope encryption or a managed KMS-backed application secret. Restrict database access and rotate affected refresh tokens after any suspected exposure.

### 7. JWT secret strength is not validated in production

Severity: High

Evidence: `SECRET_KEY` is required by settings, but `ProductionSettings` does not enforce length, entropy, or placeholder rejection.

Risk: A weak JWT signing secret allows token forgery. The accepted `JWT_SECRET` alias is useful for compatibility but should still map to a strong secret.

Recommended fix: Require at least 32 random bytes, preferably 64+ characters from a secure generator. Add production startup validation that rejects empty, short, or known placeholder values.

### 8. JWT claims are minimal

Severity: Medium

Evidence: `backend/app/core/security.py` creates tokens with `sub` and `exp` only. `backend/app/dependencies/auth.py` validates signature and expiration, then trusts `sub` as email.

Risk: Tokens lack issuer, audience, token ID, issued-at timestamp, and subject stability. Email-based subject identifiers can be problematic if emails change.

Recommended fix: Add `iss`, `aud`, `iat`, and `jti`; use immutable user ID as `sub`; validate issuer and audience in all JWT decode paths.

### 9. No login rate limiting or brute-force protection

Severity: High

Evidence: `backend/app/api/v1/auth.py` and `backend/app/services/auth_service.py` have no rate limiter, lockout, IP throttling, or abuse controls.

Risk: Credential stuffing and password brute-force attempts can run unchecked.

Recommended fix: Add per-IP and per-account rate limits for login/register, failed-login counters, and Render/WAF-level request throttling where available.

### 10. Password policy is too permissive

Severity: Medium

Evidence: `backend/app/schemas/user.py` accepts `password: str` without minimum length or complexity checks.

Risk: Users can register weak passwords.

Recommended fix: Enforce minimum length, reject common passwords, and consider breached password checks. Keep bcrypt hashing.

### 11. Production CORS is localhost-only and not environment-configured

Severity: Medium

Evidence: `backend/app/main.py` uses `allow_origin_regex=r"http://localhost:\d+"` with credentials enabled.

Risk: Browser-based production clients will fail unless served from localhost. If widened later in code, credentialed CORS can become dangerous without explicit origin allowlisting.

Recommended fix: Add explicit `CORS_ALLOWED_ORIGINS` configuration. In production, allow only the deployed frontend/admin origins over HTTPS. Keep localhost origins development-only.

### 12. Public health endpoints expose dependency status

Severity: Medium

Evidence: `/api/v1/health` returns `database`, `chromadb`, and `gemini` status. `/api/v1/health/db` returns database connectivity and query result.

Risk: Public unauthenticated health endpoints reveal service dependencies and can help attackers fingerprint infrastructure. `/health/db` is more specific than a platform health check needs.

Recommended fix: Keep a minimal public liveness endpoint for Render. Move detailed dependency readiness behind authentication or restrict it to internal/admin access. Remove or protect `/api/v1/health/db` before production launch.

### 13. API docs are publicly accessible

Severity: Medium

Evidence: `DemoAccessValidator.allowed_paths` allows `/docs`, `/openapi.json`, and `/redoc`.

Risk: Public OpenAPI docs expose endpoint shape and request models, increasing reconnaissance value.

Recommended fix: Disable docs in production or protect them behind admin authentication/network controls.

### 14. Logs include email addresses and operational identifiers

Severity: Medium

Evidence: `AuthService` logs registration/login email addresses for some events and user IDs for others. Logging middleware logs paths and methods.

Risk: Logs can contain PII. If logs are exported or retained broadly, email addresses and user IDs increase privacy exposure.

Recommended fix: Avoid logging raw email addresses. Use user IDs or hashed identifiers. Define log retention and access controls. Never log OAuth tokens, authorization headers, email body content, or full callback URLs.

### 15. Local runtime artifacts are present in the worktree

Severity: Medium

Evidence: `backend/chromadb/chroma.sqlite3` and `backend/logs/mailmind.log` appear as modified files in git status.

Risk: Local vector data and logs may contain user-derived data or operational details and should not be committed.

Status: Partially fixed. `.gitignore` now ignores future `backend/logs/` and `backend/chromadb/` changes. Existing tracked files, if already committed, still require repository cleanup.

Recommended fix: Remove tracked runtime artifacts from git history/index after confirming with the team. Rotate any exposed credentials or tokens if logs ever contained secrets.

### 16. Render deployment relies on manual secret values

Severity: Medium

Evidence: `render.yaml` marks secrets with `sync: false`, which is correct, but production readiness depends on dashboard-provided values.

Risk: Missing or weak env values can cause insecure fallback behavior or failed runtime startup.

Recommended fix: Verify all Render secrets before deployment. Use strong `SECRET_KEY`, HTTPS `GOOGLE_REDIRECT_URI`, production `DATABASE_URL`, valid `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, and `CHROMA_DB_PATH=/var/data/chromadb`.

### 17. Docker image runs as root

Severity: Low

Evidence: `backend/Dockerfile` does not define a non-root user.

Risk: If container isolation is bypassed, a root process has a larger blast radius.

Recommended fix: Add a non-root application user in Docker-based deployments. Render Python environment may not use this Dockerfile unless explicitly configured.

### 18. Alembic sample URL includes placeholder credentials

Severity: Low

Evidence: `backend/alembic.ini` contains `sqlalchemy.url = driver://user:pass@localhost/dbname`.

Risk: This is a placeholder, not an actual secret. It can still trigger secret scanners or confuse deployers.

Recommended fix: Keep runtime Alembic configuration sourced from `settings.DATABASE_URL`; optionally replace the placeholder with a clearer non-secret example.

## Hardcoded Secret Review

No real hardcoded API keys, database passwords, JWT secrets, or Google client secrets were found in the reviewed files. The hardcoded `test@mailmind.ai` OAuth user is not a secret, but it is a critical authorization flaw.

## Deployment Recommendations

- Set `ENVIRONMENT=production` in Render.
- Set `SECRET_KEY` to a high-entropy production-only value and rotate it if it was ever shared.
- Use HTTPS-only `GOOGLE_REDIRECT_URI` and configure the exact URI in Google Cloud Console.
- Do not deploy Gmail OAuth to production until state validation, authenticated user binding, and PKCE are implemented.
- Use explicit production CORS origins instead of localhost regex.
- Restrict detailed health and documentation endpoints before public launch.
- Keep Render secrets in the dashboard or secret manager only; do not commit `.env` files.
- Keep `CHROMA_DB_PATH=/var/data/chromadb` on the Render persistent disk.
- Remove local logs and Chroma data from tracked git files before release.
- Define retention and access policy for application logs, Render logs, Supabase backups, and Chroma backups.