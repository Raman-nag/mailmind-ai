# Backup and Recovery

## Chroma Backup Process

ChromaDB stores MailMind vector data on the Render persistent disk at:

```bash
/var/data/chromadb
```

Use application-level backups in addition to Render disk snapshots.

Recommended process:

1. Schedule a maintenance window or temporarily stop write-heavy ingestion.
2. Open the Render service shell or connect with SSH.
3. Create a compressed archive:

   ```bash
   cd /var/data
   tar -czf chromadb-backup-$(date -u +%Y%m%dT%H%M%SZ).tar.gz chromadb
   ```

4. Transfer the archive off Render using SCP, Magic Wormhole, or approved object storage tooling.
5. Verify the archive can be listed:

   ```bash
   tar -tzf chromadb-backup-YYYYMMDDTHHMMSSZ.tar.gz
   ```

6. Store the backup with restricted access and documented retention.

Back up the entire directory, not only `chroma.sqlite3`, because Chroma uses
SQLite plus collection and index files.

## Chroma Restore Process

Restore from a known-good archive:

1. Stop the backend or enable maintenance mode.
2. Keep the current Chroma directory until recovery is verified:

   ```bash
   mv /var/data/chromadb /var/data/chromadb.restore-source.$(date -u +%Y%m%dT%H%M%SZ)
   ```

3. Copy the backup archive to the Render service.
4. Extract it under `/var/data`:

   ```bash
   cd /var/data
   tar -xzf /path/to/chromadb-backup-YYYYMMDDTHHMMSSZ.tar.gz
   ```

5. Confirm files exist under `/var/data/chromadb`.
6. Start the backend.
7. Verify `/api/v1/health`.
8. Run a representative search/RAG request for a user with known email data.

If restore fails, stop the backend and move the preserved directory back into
place or restore a different backup.

Render disk snapshots can recover the whole disk to an earlier point in time.
Use them only when a whole-disk rollback is acceptable, because newer Chroma
backups or other files on the disk can be overwritten.

## Supabase Backup Considerations

Supabase/PostgreSQL is the system of record for users, Gmail accounts, emails,
memories, actions, and feedback. ChromaDB is a derived vector index that must
remain logically aligned with the email rows and user cleanup state in
PostgreSQL.

Production considerations:

- Enable Supabase automated backups or point-in-time recovery according to the project plan.
- Keep Supabase and Chroma backup retention windows aligned.
- Take a Chroma backup near the same time as major database migrations or bulk email reprocessing.
- Document which Supabase backup timestamp corresponds to each Chroma archive.
- Test restore in a non-production environment before relying on a backup plan.

Recovery order for a full production incident:

1. Restore Supabase/PostgreSQL first.
2. Restore the Chroma backup taken closest to the database recovery point.
3. Start the backend.
4. Verify health checks, user login, email listing, and a representative RAG query.
5. Re-vectorize affected users only if Chroma and PostgreSQL are out of sync.
