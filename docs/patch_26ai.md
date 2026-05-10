# docs/runbooks/patch_26ai.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — 26ai Patch Runbook
# Version: 1.0
# Last updated: 2026-05-09
# ============================================================

## Overview

This runbook documents the process for applying the Oracle 26ai
release update (patch) to the ArachDB database on OCI Base DB System.

### Terminology
- This is a PATCH (Release Update), not a full database upgrade.
- Internal version remains 23.0.0.0.0.
- Only VERSION_FULL changes to 23.26.x.0.0.
- No application re-certification required.
- All objects, grants, profiles carry over unchanged.

### Database details
- DB name: ArachDB
- DB unique name: ArachDB_b7d_fra
- DB system OCID: $OCI_DB_SYSTEM_OCID
- Database OCID: $OCI_DATABASE_OCID
- DB home OCID: ocid1.dbhome.oc1.eu-frankfurt-1.antheljstczdrqqah3g5axykqucm4mntpxcmrhkgeyrnzawjngrq2h7w6mha
- Current version: 23.7.0.25.01 (23ai)

---

## Prerequisites

- OCI CLI 3.79.0 or later on Mac
- Environment variables set: OCI_DATABASE_OCID, OCI_DB_SYSTEM_OCID
- Active SSH access to OCI bastion (ara)
- No active SQLcl sessions on the database

---

## Step 1 — List available patches

```bash
oci db patch list by-database \
    --database-id $OCI_DATABASE_OCID
```

Note the patch OCID and version for the patch you want to apply.

### Known patches (as of 2026-05-09)
| Description | Version | Patch OCID |
|-------------|---------|-----------|
| Apr 2026 26ai Database Patch | 23.26.2.0.0 | ocid1.dbpatch.oc1.eu-frankfurt-1.antheljst5t4sqqabelmk3kdkuxkago6zyz3sudktistudqmb36athsm6riq |
| Jan 2026 26ai Database Patch | 23.26.1.0.0 | ocid1.dbpatch.oc1.eu-frankfurt-1.antheljst5t4sqqaodvjrq7elwzjhfksrdf5nc4baj2jhmtxnvdkcrppbpfq |
| Oct 2025 26ai Database Patch | 23.26.0.0.0 | ocid1.dbpatch.oc1.eu-frankfurt-1.antheljst5t4sqqa7jiy7zt72olsj5flrabbyknf6sns6xexm6moq6occe3q |

---

## Step 2 — Disable automatic backups

```bash
oci db database update \
    --database-id $OCI_DATABASE_OCID \
    --auto-backup-enabled false
```

Verify:
```bash
oci db database get --database-id $OCI_DATABASE_OCID \
    | grep '"auto-backup-enabled"'
```

---

## Step 3 — Take manual backup

```bash
oci db backup create \
    --database-id $OCI_DATABASE_OCID \
    --display-name "pre-26ai-patch-manual-backup"
```

Monitor until ACTIVE:
```bash
oci db backup get --backup-id <backup-ocid> \
    | grep '"lifecycle-state"'
```

---

## Step 4 — Run precheck

```bash
oci db database patch \
    --database-id $OCI_DATABASE_OCID \
    --patch-id <patch-ocid> \
    --patch-action PRECHECK
```

Monitor until AVAILABLE:
```bash
oci db database get --database-id $OCI_DATABASE_OCID \
    | grep -E '"lifecycle-state"|"patch-version"'
```

Verify precheck succeeded:
```bash
oci db patch-history list by-database \
    --database-id $OCI_DATABASE_OCID
```

---

## Step 5 — Apply patch

```bash
oci db database patch \
    --database-id $OCI_DATABASE_OCID \
    --patch-id <patch-ocid> \
    --patch-action APPLY
```

Monitor every 10 minutes until AVAILABLE:
```bash
oci db database get --database-id $OCI_DATABASE_OCID \
    | grep -E '"lifecycle-state"|"patch-version"'
```

Expected duration: 45-90 minutes.

---

## Step 6 — Verify patch applied

```bash
oci db db-home get \
    --db-home-id ocid1.dbhome.oc1.eu-frankfurt-1.antheljstczdrqqah3g5axykqucm4mntpxcmrhkgeyrnzawjngrq2h7w6mha \
    | grep '"db-version"'
```

Should show 23.26.x.0.0.

Also verify via SQLcl on OCI:
```sql
SELECT version, version_full FROM v$instance;
```

Verify TNS_ADMIN and tnsnames.ora unchanged:
```bash
echo $TNS_ADMIN
ls $TNS_ADMIN/tnsnames.ora
sql sys/$ORACLE_SYS_PASSWORD@ARADB as sysdba
```

---

## Step 7 — Re-enable automatic backups

```bash
oci db database update \
    --database-id $OCI_DATABASE_OCID \
    --auto-backup-enabled true \
    --auto-backup-window SLOT_TWO \
    --recovery-window-in-days 7
```

---

## Patch history

| Date | Action | Version | Result | Notes |
|------|--------|---------|--------|-------|
| 2026-05-09 | PRECHECK | 23.26.2.0.0 | SUCCEEDED | |
| 2026-05-09 | APPLY | 23.26.2.0.0 | FAILED | Fast failure ~2min, DB unaffected, reason unknown |

### On the APPLY failure (2026-05-09)
- Precheck succeeded
- APPLY failed after approximately 2 minutes
- Database returned to AVAILABLE on 23.7.0.25.01 — no corruption
- OCI API returns only generic error message
- Alert log not accessible from bastion host
- Oracle support (Slavomír Seno) informed
- January patch (23.26.1.0.0) not yet tried — option if April patch
  continues to fail

### Important CLI note
The command `oci db database upgrade-with-db-version` does NOT work
for Base DB System patch updates. The correct mechanism is:
`oci db database patch` with a patch OCID from
`oci db patch list by-database`.
