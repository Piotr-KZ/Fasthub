# Database Backup & Recovery Guide

This document describes the backup strategy and recovery procedures for FastHub database.

---

## 🔄 Automatic Backups (Render PostgreSQL)

**Render PostgreSQL** provides automatic daily backups:

- **Frequency:** Daily (automatic)
- **Retention:** 
  - Free plan: 7 days
  - Paid plan: 30 days
- **Point-in-time recovery:** Available on paid plans
- **Management:** Fully managed by Render (zero configuration required)

### Accessing Render Backups

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your PostgreSQL database
3. Navigate to **"Backups"** tab
4. Click **"Restore"** on desired backup

---

## 📦 Manual Backups

For critical moments (before major migrations, deployments), use the manual backup script.

### Prerequisites

- `pg_dump` installed (included in PostgreSQL client tools)
- `DATABASE_URL` environment variable set
- (Optional) AWS CLI for S3 upload

### Create Manual Backup

```bash
# Basic usage (saves to ./backups/)
DATABASE_URL="postgresql://..." ./scripts/backup_database.sh

# Custom output directory
DATABASE_URL="postgresql://..." ./scripts/backup_database.sh /path/to/backups

# With S3 upload
DATABASE_URL="postgresql://..." \
AWS_ACCESS_KEY_ID="..." \
AWS_SECRET_ACCESS_KEY="..." \
S3_BACKUP_BUCKET="my-backups" \
./scripts/backup_database.sh
```

### Backup File Format

- **Filename:** `fasthub_backup_YYYYMMDD_HHMMSS.sql.gz`
- **Format:** Compressed SQL dump (gzip)
- **Contents:** Full database schema + data
- **Cleanup:** Automatically removes backups older than 7 days

---

## 🔧 Restore from Backup

### Restore from Render Backup

1. **Render Dashboard → PostgreSQL → Backups**
2. **Click "Restore" on desired backup**
3. **Confirm restoration** (this will overwrite current data!)

### Restore from Manual Backup

```bash
# Decompress and restore
gunzip -c backups/fasthub_backup_20260103_120000.sql.gz | psql $DATABASE_URL

# Or in one command
DATABASE_URL="postgresql://..." \
gunzip -c backups/fasthub_backup_20260103_120000.sql.gz | psql $DATABASE_URL
```

**⚠️ WARNING:** Restoration will **overwrite all current data**. Always verify backup integrity before restoring.

---

## 📅 Backup Schedule Recommendations

### Development

- **Manual backups:** Before major schema changes
- **Render automatic:** Default (7 days)

### Production

- **Render automatic:** Enabled (30 days retention)
- **Manual backups:** 
  - Before major deployments
  - Before database migrations
  - Weekly full backups to S3
- **Testing:** Monthly restore tests to verify backup integrity

---

## 🚨 Disaster Recovery Procedure

### Scenario 1: Data Corruption (Recent)

1. **Stop backend service** (Render Dashboard → Service → Manual Deploy → Suspend)
2. **Restore from Render backup** (most recent clean backup)
3. **Verify data integrity** (check critical tables)
4. **Resume backend service**

### Scenario 2: Data Loss (Older than 7/30 days)

1. **Identify last known good manual backup**
2. **Stop backend service**
3. **Restore from manual backup** (see commands above)
4. **Run migrations** if schema changed since backup
5. **Verify data integrity**
6. **Resume backend service**

### Scenario 3: Complete Database Loss

1. **Create new Render PostgreSQL database**
2. **Update `DATABASE_URL` in backend environment**
3. **Restore from most recent backup** (Render or manual)
4. **Run migrations** to ensure schema is current
5. **Deploy backend**
6. **Verify all services**

---

## 🔍 Backup Verification

### Manual Verification

```bash
# Test restore to temporary database
createdb fasthub_test
gunzip -c backups/fasthub_backup_20260103_120000.sql.gz | psql fasthub_test

# Verify tables exist
psql fasthub_test -c "\dt"

# Check row counts
psql fasthub_test -c "SELECT COUNT(*) FROM users;"
psql fasthub_test -c "SELECT COUNT(*) FROM organizations;"

# Cleanup
dropdb fasthub_test
```

### Automated Verification (TODO)

Create a scheduled job to:
1. Restore backup to test database
2. Run integrity checks
3. Report results to monitoring
4. Cleanup test database

---

## 📊 Backup Monitoring

### Key Metrics

- **Last backup timestamp:** Check Render Dashboard daily
- **Backup size:** Monitor for unexpected growth
- **Restore time:** Test quarterly (should be < 5 minutes for < 1GB)

### Alerts

Set up alerts for:
- ❌ Backup failure (Render email notifications)
- ⚠️ Backup size increase > 50% (indicates data growth or issue)
- ⚠️ No backup in 48 hours (indicates service issue)

---

## 🔐 Security Best Practices

1. **Encrypt backups at rest** (Render does this automatically)
2. **Encrypt backups in transit** (use HTTPS/TLS for S3 uploads)
3. **Restrict access** to backup files (S3 bucket policies)
4. **Rotate credentials** used for backups quarterly
5. **Test restore procedure** monthly
6. **Document recovery time objective (RTO):** < 1 hour
7. **Document recovery point objective (RPO):** < 24 hours

---

## 📝 Backup Checklist

### Before Major Changes

- [ ] Create manual backup
- [ ] Verify backup file exists and is not corrupted
- [ ] Document current database state (row counts, schema version)
- [ ] Test restore procedure in staging environment
- [ ] Notify team of backup completion

### After Incident

- [ ] Document incident details
- [ ] Identify root cause
- [ ] Restore from backup if needed
- [ ] Verify data integrity
- [ ] Update runbooks with lessons learned
- [ ] Review backup strategy

---

## 🆘 Support

For backup/restore issues:

1. **Render Support:** https://render.com/docs/databases#backups
2. **PostgreSQL Documentation:** https://www.postgresql.org/docs/current/backup.html
3. **FastHub Team:** support@fasthub.com

---

## 📚 Additional Resources

- [Render PostgreSQL Backups](https://render.com/docs/databases#backups)
- [PostgreSQL Backup Best Practices](https://www.postgresql.org/docs/current/backup.html)
- [Disaster Recovery Planning](https://www.postgresql.org/docs/current/backup-dump.html)
