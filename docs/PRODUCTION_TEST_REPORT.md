# Production Test Report

Manual validation matrix for MailMind AI Sprint 9 Stage 5 production validation.

## Execution Details

- Environment:
- Backend URL:
- APK/build version:
- Tester:
- Test date:
- Render service:
- Database/Supabase project:
- Chroma path:

## Preconditions

- Production backend is deployed and reachable over HTTPS.
- Required Render environment variables are configured.
- Alembic migrations have been applied.
- Chroma persistent disk is mounted and `CHROMA_DB_PATH` points to the mounted path.
- Google OAuth production redirect URI is configured in Google Cloud Console.
- Test Gmail account has emails suitable for sync, retrieval, action extraction, and RAG validation.
- Test user credentials are available or registration is allowed.

## Validation Matrix

| Feature | Endpoint | Expected Result | Actual Result | PASS/FAIL | Notes |
|---|---|---|---|---|---|
| Authentication - Registration | `POST /api/v1/auth/register` | Creates a new user, returns user profile fields, does not return password or password hash. |  |  |  |
| Authentication - Duplicate Registration | `POST /api/v1/auth/register` | Rejects duplicate email with a controlled 400 response. |  |  |  |
| Authentication - Login | `POST /api/v1/auth/login` | Accepts valid credentials and returns bearer `access_token` plus `token_type`. |  |  |  |
| Authentication - Invalid Login | `POST /api/v1/auth/login` | Rejects invalid credentials with 401 and no token. |  |  |  |
| Authentication - JWT Validation | `GET /api/v1/auth/me` | Valid bearer token returns the authenticated user profile. |  |  |  |
| Authentication - Missing JWT | `GET /api/v1/auth/me` | Missing bearer token is rejected with 403 or 401. |  |  |  |
| Authentication - Invalid JWT | `GET /api/v1/auth/me` | Invalid or expired bearer token is rejected with 401. |  |  |  |
| Gmail - OAuth Connect | `GET /api/v1/gmail/connect` | Authenticated user receives a Google authorization URL and OAuth `state`. |  |  |  |
| Gmail - OAuth Connect Without JWT | `GET /api/v1/gmail/connect` | Request without bearer token is rejected. |  |  |  |
| Gmail - OAuth Callback | `GET /api/v1/gmail/callback?code=<code>&state=<state>` | Valid callback exchanges token, saves Gmail token for the state-bound user, and returns success message. |  |  |  |
| Gmail - OAuth Callback Missing State | `GET /api/v1/gmail/callback?code=<code>` | Missing state is rejected with controlled 400 response. |  |  |  |
| Gmail - OAuth Callback Invalid State | `GET /api/v1/gmail/callback?code=<code>&state=<invalid>` | Invalid, expired, or reused state is rejected with controlled 400 response. |  |  |  |
| Gmail - Gmail Sync | `GET /api/v1/gmail/sync` | Connected user syncs Gmail messages, imports new emails, summarizes where applicable, vectorizes emails, and returns import/summarize counts. |  |  |  |
| Gmail - Gmail Sync Without Connected Account | `GET /api/v1/gmail/sync` | User without Gmail token receives controlled `No Gmail account connected` response. |  |  |  |
| Gmail - Email Retrieval List | `GET /api/v1/emails/` | Authenticated user receives only their own emails. |  |  |  |
| Gmail - Email Retrieval Detail | `GET /api/v1/emails/{email_id}` | Owner can retrieve a specific email with expected metadata and summary fields. |  |  |  |
| Gmail - Email Search | `GET /api/v1/emails/search?q=<query>` | Returns matching emails for authenticated user only. |  |  |  |
| Gmail - Cross-User Email Access | `GET /api/v1/emails/{other_user_email_id}` | Access to another user's email is rejected with 403 or 404. |  |  |  |
| Dashboard - Stats Loading | `GET /api/v1/dashboard/stats` | Returns dashboard counts/statistics for authenticated user. |  |  |  |
| Dashboard - Today Tasks | `GET /api/v1/dashboard/today-tasks` | Returns count and actions due today for authenticated user. |  |  |  |
| Dashboard - Upcoming Deadlines | `GET /api/v1/dashboard/upcoming-deadlines` | Returns count and deadline/reminder actions due soon. |  |  |  |
| Dashboard - Urgent Emails | `GET /api/v1/dashboard/urgent-emails` | Returns count and urgent emails from priority scoring. |  |  |  |
| Dashboard - Pending Replies | `GET /api/v1/dashboard/pending-replies` | Returns count and pending reply actions. |  |  |  |
| Dashboard - Agent Recommendations | `GET /api/v1/dashboard/recommended-actions` | Returns recommendations and answer generated from action, reminder, and recommendation agents. |  |  |  |
| Memory - Create Memory | `POST /api/v1/memories` | Creates memory for authenticated user and returns memory response. |  |  |  |
| Memory - List Memories | `GET /api/v1/memories` | Returns memories belonging to authenticated user. |  |  |  |
| Memory - Search Memory By Query | `GET /api/v1/memories/search?query=<query>` | Returns matching memories for authenticated user. |  |  |  |
| Memory - Search Memory By Type | `GET /api/v1/memories/search?memory_type=<type>` | Returns memories filtered by memory type. |  |  |  |
| Memory - Delete Memory | `DELETE /api/v1/memories/{memory_id}` | Deletes owned memory and returns 204. |  |  |  |
| Memory - Delete Missing Memory | `DELETE /api/v1/memories/{missing_memory_id}` | Missing or unauthorized memory deletion returns controlled 404. |  |  |  |
| Chat - RAG Chat | `POST /api/v1/chat` | Returns answer plus `memories_used` and `emails_used` for authenticated user. |  |  |  |
| Chat - RAG Chat Empty/Invalid Query | `POST /api/v1/chat` | Invalid request is rejected with controlled validation or 400 response. |  |  |  |
| Chat - Retrieval Quality | `POST /api/v1/chat` | Answer references relevant synced email or memory content and avoids unrelated user data. |  |  |  |
| RAG - Vector Search | `POST /rag/search` | Returns top matching email vector results for authenticated user and requested `top_k`. |  |  |  |
| Actions - Action Extraction During Sync | `GET /api/v1/gmail/sync` | Sync processes actionable email content and creates/updates/completes/rejects actions as appropriate. |  |  |  |
| Actions - Today Action Retrieval | `GET /api/v1/dashboard/today-tasks` | Extracted actions due today appear in dashboard task response. |  |  |  |
| Actions - Priority Scoring | `GET /api/v1/dashboard/urgent-emails` | High-priority emails are identified and returned in urgent email response. |  |  |  |
| Actions - Reminder Generation | `GET /api/v1/dashboard/upcoming-deadlines` | Reminder/deadline agent returns upcoming deadline actions. |  |  |  |
| Actions - Recommended Actions | `GET /api/v1/dashboard/recommended-actions` | Recommendation agent returns actionable recommendations from current user data. |  |  |  |
| Feedback - Submit Feedback | `POST /api/v1/feedback` | Authenticated user submits feedback and receives created feedback response. |  |  |  |
| Feedback - Get My Feedback | `GET /api/v1/feedback/me` | Returns current user's submitted feedback. |  |  |  |
| Feedback - Duplicate Feedback | `POST /api/v1/feedback` | Duplicate feedback submission is rejected with controlled 400 response if only one submission is allowed. |  |  |  |
| Demo Lifecycle - User Expiry Enforcement | Protected endpoint after demo expiry | Expired demo user is blocked from protected endpoints with controlled 403 response. |  |  |  |
| Demo Lifecycle - Feedback Allowed After Expiry | `POST /api/v1/feedback` after expiry | Expired demo user can still submit feedback if lifecycle rules allow feedback route. |  |  |  |
| Demo Lifecycle - Cleanup Scheduler | Scheduler runtime behavior | Scheduler marks expired users, honors cleanup grace period, and cleans eligible users without affecting active users. |  |  |  |
| Demo Lifecycle - Cleanup Data Removal | Post-cleanup database/vector inspection | Cleaned user data and Chroma vectors are removed according to cleanup policy. |  |  |  |
| Health Monitoring - Overall Health | `GET /api/v1/health` | Returns `healthy` when database, ChromaDB, and Gemini checks are ok; returns `unhealthy` when any dependency fails. |  |  |  |
| Health Monitoring - Database Detail | `GET /api/v1/health/db` | Returns controlled database connectivity response without exposing credentials or sensitive data. |  |  |  |
| Health Monitoring - Unauthorized Data Leakage Check | `GET /api/v1/health` | Health response does not expose secrets, tokens, connection strings, internal stack traces, or user data. |  |  |  |

## Manual Evidence Links

- Registration/login evidence:
- Gmail OAuth evidence:
- Gmail sync evidence:
- Dashboard evidence:
- Memory evidence:
- Chat/RAG evidence:
- Actions evidence:
- Feedback evidence:
- Demo lifecycle evidence:
- Health monitoring evidence:

## Final Sign-Off

- Overall result:
- Blocking issues:
- Non-blocking issues:
- Release approver:
- Approval date: