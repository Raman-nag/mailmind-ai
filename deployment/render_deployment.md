# Render Deployment

This guide deploys the MailMind AI FastAPI backend to Render using the existing backend entrypoint:

```bash
app.main:app
```

## Render Setup

1. Push the repository to GitHub or another Git provider supported by Render.
2. In Render, create a new Blueprint deployment from the repository, or create a Web Service manually.
3. Use the repository root when deploying from `render.yaml`.
4. Confirm the service root directory is `backend`.
5. Confirm the service runtime is Python 3.12.

The service should use:

```bash
pip install --upgrade pip && pip install -r requirements.txt
```

as the build command, and:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

as the start command.

## Environment Variables

Set these variables in the Render service environment. Do not commit real secrets.

```bash
ENVIRONMENT=production
DATABASE_URL=<postgresql-connection-url>
GEMINI_API_KEY=<gemini-api-key>
SECRET_KEY=<jwt-secret>
GOOGLE_CLIENT_ID=<google-oauth-client-id>
GOOGLE_CLIENT_SECRET=<google-oauth-client-secret>
GOOGLE_REDIRECT_URI=<render-or-production-oauth-callback-url>
CORS_ALLOWED_ORIGINS=<production-frontend-origin>[,<additional-origin>]
SUPABASE_URL=<supabase-project-url>
SUPABASE_KEY=<supabase-service-or-anon-key>
CHROMA_DB_PATH=/var/data/chromadb
```

Use the values from `backend/.env.production.example` as the template.

## Persistent Disk

ChromaDB must write to a Render persistent disk, not the service checkout. The
blueprint mounts the disk at:

```bash
/var/data
```

and configures:

```bash
CHROMA_DB_PATH=/var/data/chromadb
```

Only files under the mounted path survive Render restarts and redeploys.

## Deployment Steps

1. Commit and push the deployment files.
2. Open Render and create or update the Blueprint from `render.yaml`.
3. Confirm the `mailmind-chromadb` persistent disk is attached at `/var/data`.
4. Add all secret environment variables in the Render dashboard.
5. Trigger a deploy.
6. Review the build logs and confirm dependencies install successfully.
7. Review the runtime logs and confirm Uvicorn starts on Render's `$PORT`.

## Health Check Verification

Render is configured to check:

```bash
/api/v1/health
```

After deployment, verify manually:

```bash
curl https://<render-service-name>.onrender.com/api/v1/health
```

Expected healthy response:

```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "chromadb": "ok",
    "gemini": "ok"
  }
}
```

If any service returns `failed`, check the corresponding Render environment variable, database network access, ChromaDB path, or Gemini API key configuration.
