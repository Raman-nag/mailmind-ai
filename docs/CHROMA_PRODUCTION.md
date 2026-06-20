# ChromaDB Production Persistence

## Storage Architecture

MailMind AI stores semantic email vectors in ChromaDB through
`chromadb.PersistentClient`. The client is created in
`backend/app/rag/vector_store.py` and receives its storage path from
`settings.CHROMA_DB_PATH`.

Configuration is loaded from `backend/app/core/config/base.py`.
`CHROMA_DB_PATH` is accepted directly, with `CHROMA_PATH` retained as a
backward-compatible alias. The email vector collection name is controlled by
`CHROMA_EMAIL_COLLECTION` and defaults to `emails_collection`.

Production storage layout on Render:

```text
/var/data
  /chromadb
    chroma.sqlite3
    <collection/index files>
```

Render service configuration:

```yaml
disk:
  name: mailmind-chromadb
  mountPath: /var/data
  sizeGB: 1

envVars:
  - key: CHROMA_DB_PATH
    value: /var/data/chromadb
```

## Persistence Strategy

Render service files outside a persistent disk are ephemeral. ChromaDB must
therefore write under the mounted disk path.

Use:

```bash
CHROMA_DB_PATH=/var/data/chromadb
```

With this configuration:

- Chroma data survives process restarts.
- Chroma data survives Render redeploys.
- The backend continues to use the existing local persistent Chroma client.
- Vector search logic, embeddings, RAG prompts, and retrieval behavior are unchanged.

The persistent disk is attached to one service instance. Do not scale the web
service horizontally while ChromaDB is stored on a single attached disk. Move
ChromaDB to a dedicated external vector database before running multiple backend
instances.

## Backup Strategy

Create application-level Chroma backups from the Render service shell or SSH.
Back up the full `CHROMA_DB_PATH` directory while the application is stopped or
quiesced to avoid copying partially updated SQLite/index files.

Recommended backup command:

```bash
cd /var/data
tar -czf chromadb-backup-$(date -u +%Y%m%dT%H%M%SZ).tar.gz chromadb
```

Transfer the archive off Render using SCP, Magic Wormhole, or another approved
secure transfer process. Store backups in durable object storage with access
controls and retention aligned with the Supabase/PostgreSQL backup policy.

Render persistent disks also provide platform snapshots. Treat snapshots as an
additional recovery option, not the only backup, because restoring a snapshot
replaces the whole disk state.

## Recovery Strategy

Restore ChromaDB by replacing the contents of `CHROMA_DB_PATH` from a known-good
backup.

High-level recovery flow:

1. Put the backend in maintenance mode or stop the Render service.
2. Preserve the current directory for forensic rollback:

   ```bash
   mv /var/data/chromadb /var/data/chromadb.failed.$(date -u +%Y%m%dT%H%M%SZ)
   ```

3. Extract the backup:

   ```bash
   cd /var/data
   tar -xzf /path/to/chromadb-backup.tar.gz
   ```

4. Confirm the restored path is `/var/data/chromadb`.
5. Start the backend.
6. Verify `/api/v1/health` and run a representative RAG query.

If Chroma cannot be restored, rebuild vectors by re-ingesting or re-vectorizing
email records from Supabase/PostgreSQL using the existing application ingestion
path. This should be treated as slower disaster recovery because it depends on
source email data and embedding API availability.

## Render Disk Setup

For Blueprint deployments, `render.yaml` should include:

```yaml
services:
  - type: web
    name: mailmind-ai-backend
    disk:
      name: mailmind-chromadb
      mountPath: /var/data
      sizeGB: 1
    envVars:
      - key: CHROMA_DB_PATH
        value: /var/data/chromadb
```

For manual dashboard setup:

1. Open the `mailmind-ai-backend` service in Render.
2. Add a persistent disk.
3. Set the disk mount path to `/var/data`.
4. Choose an initial size, starting with `1 GB` unless production vector volume requires more.
5. Set `CHROMA_DB_PATH` to `/var/data/chromadb`.
6. Deploy the service and confirm the health check passes.

Monitor disk usage in Render. Increase disk size before free space becomes low;
Render supports increasing disk size but not decreasing it.
