# Error Codes — Arachnet Clinical Embeddings

**Project:** Arachnet Clinical Embeddings  
**Owner:** Jan Mura, Arachnet Project z.s.  
**Document version:** 1.0  
**Date:** 2026-03-26

---

## Purpose

This document is the operational reference for exit codes used across all
Python scripts and Bash scripts in the project. When a script terminates
with a non-zero exit code, this document identifies what went wrong and
where to look.

This document and `src/common/exceptions.py` must be kept in sync. If a
new exception class is added to `exceptions.py`, a corresponding entry
must be added here.

---

## General Convention

The project follows a **fail fast, fail loudly** policy. No error is
suppressed silently. Every failure produces:

1. A log entry at ERROR level identifying the phase, step, script, and
   error detail.
2. A non-zero exit code from the script that failed.
3. Propagation of that exit code up through the Bash orchestrator, which
   stops the pipeline immediately and logs the failure.

A script that exits with code 0 guarantees that its work completed
successfully and all outputs are valid. Any doubt — non-zero exit.

---

## Exit Code Reference

### Code 0 — Success

**Meaning:** The script completed all work successfully. All outputs are
valid and can be relied upon by subsequent steps.

**Python class:** None — normal return.  
**When you see it:** Every successful run of every script.

---

### Code 1 — Configuration Error

**Meaning:** A configuration file could not be loaded, parsed, or
validated. The script could not determine how to proceed because its
inputs are invalid or incomplete.

**Python class:** `SnomedConfigError`  
**Raised by:** `config_loader.py`, any script that validates its config
inputs at startup.

**Common causes:**
- A mandatory key is missing from a YAML file. The error message names
  the file and the key.
- A YAML file is syntactically malformed. The error message includes the
  line number from OmegaConf.
- An OmegaConf interpolation references a key that does not exist, for
  example `${environments.production.paths.base}` where `base` is not
  defined.
- `active_environment` is set to a value that does not exist as a key
  under `environments`.
- A value is the wrong type — for example a string where an integer is
  expected.

**What to do:**
1. Read the error message — it names the file and key.
2. Open the named YAML file and check the named key.
3. Verify OmegaConf interpolation paths resolve correctly.
4. Re-run after fixing.

---

### Code 2 — Database Connection Error

**Meaning:** A connection to Oracle 23ai could not be established, or a
required credential could not be resolved.

**Python class:** `SnomedDBConnectionError`  
**Raised by:** `db_connection.py`

**Common causes:**
- The password environment variable is not set or is empty. The required
  variables are `SNOMED_DB_PASSWORD`, `SNOMED_STAGE_DB_PASSWORD`, and
  `SNOMED_ADMIN_DB_PASSWORD` (setup only). Check `.bashrc`.
- `TNS_ADMIN` is not set or does not point to a directory containing
  `tnsnames.ora`.
- The TNS alias in `database.yaml` (`tns_alias`) does not match any
  entry in `tnsnames.ora`.
- The OCI instance or database is not reachable — network, firewall, or
  database not started.
- Authentication failed — wrong password or account locked.

**What to do:**
1. Verify environment variables are set: `echo $SNOMED_DB_PASSWORD`
   (confirms it is set — do not log or share the value).
2. Verify `TNS_ADMIN`: `echo $TNS_ADMIN` and `ls $TNS_ADMIN`.
3. Verify the TNS alias matches `tnsnames.ora`.
4. Test connectivity: `sqlcl snomed@ARADB` from the terminal.
5. Check the Oracle error code in the detail field for specific diagnosis.

**Security note:** Credential values are never written to logs or
included in exception detail strings under any circumstances.

---

### Code 3 — DDL Error

**Meaning:** A DDL statement (CREATE, DROP, ALTER, RENAME) failed during
execution.

**Python class:** `SnomedDDLError`  
**Raised by:** `db_connection.py` (`execute_ddl()`), setup scripts, the
stage-to-production swap step.

**Common causes:**
- Tablespace does not exist. `TBS_SNOMED` and `TBS_SNOMED_STAGE` must be
  created before the first load.
- Schema user does not exist or has insufficient privileges.
- Schema rename fails during the swap — another session may hold an
  object lock.
- Attempting to create a table that already exists without a preceding
  DROP — should not occur under the drop/recreate model but check if the
  pipeline was interrupted mid-run.

**What to do:**
1. Read the Oracle error code in the detail field — ORA- codes are
   specific and diagnostic.
2. For ORA-01031 (insufficient privileges): check grants on the affected
   schema user.
3. For ORA-00959 (tablespace does not exist): create the tablespace
   before re-running.
4. For rename failures during swap: check for open sessions on the
   schema objects and retry after they close.

---

### Code 4 — Data Load Error

**Meaning:** A data load operation failed. This covers file reading,
batch insert, and transaction management.

**Python class:** `SnomedLoadError`  
**Raised by:** Ingestion pipeline scripts (Phase 1).

**When this is raised from a batch insert failure, the transaction for
the affected table has already been rolled back before the exception
propagates. The stage schema is left in a partially loaded state —
tables loaded before the failure remain, the failed table is empty.**

**Common causes:**
- RF2 source file not found. Check that the data volume is mounted
  (`/mnt/snomed_data`) and that the `rf2` path contains the release
  files.
- RF2 file encoding error — file is not valid UTF-8.
- Oracle constraint violation during insert — ORA-01400 (NULL into NOT
  NULL column) or ORA-01401 (value too large). Indicates a mismatch
  between the DDL column definition and the RF2 file content.
- Row count mismatch detected during the load itself — distinct from the
  post-load validation check (which raises code 5).

**What to do:**
1. Read the detail field — it names the table, batch number, and Oracle
   error code.
2. For file not found: verify mount point and paths in `project.yaml`.
3. For ORA-01400 or ORA-01401: compare the DDL in `sql/ddl/` against
   the RF2 file specification. A column may be too narrow or defined
   NOT NULL where NULL values exist in the file.
4. The stage schema is safe to inspect — the failed table is empty, all
   earlier tables are loaded and can be queried for diagnosis.
5. Fix the root cause and re-run the full ingestion pipeline. The
   drop/recreate model means a re-run always starts clean.

---

### Code 5 — Validation Error

**Meaning:** A blocking validation check failed after all tables were
loaded but before the stage-to-production swap. The swap has not been
performed. The stage schema is intact and available for inspection.

**Python class:** `SnomedValidationError`  
**Raised by:** Validation step of the ingestion pipeline (Phase 1).

**The production schema is unaffected. The previous production data
remains available. The stage schema contains the failed load and can
be queried for diagnosis.**

**Common causes:**
- RF2-to-table row count mismatch: the number of rows loaded into a
  table does not equal the number of data rows in the source RF2 file.
  This is the primary completeness check. Investigate the load log for
  the specific table and batch.
- Minimum row count floor not met: a table has fewer rows than the
  configured floor in `ingestion.yaml`. Either the floor is stale (update
  it after first load) or the load was genuinely incomplete.
- Unexpected empty table: a table that should contain rows is empty.
- Not all tables loaded: the pipeline did not attempt all tables — check
  `skip_tables` in `ingestion.yaml` is empty for production runs.
- Referential integrity violation (after being promoted to blocking):
  a foreign key value in a child table has no matching row in the parent
  table. Investigate whether the violation is a legitimate SNOMED
  historical reference or a genuine load error.

**What to do:**
1. Read the detail field — it names the check, the table, and the
   expected vs actual values.
2. Query the stage schema directly to inspect the affected table.
3. Compare the load manifest (`log/load_manifest_<date>.json`) with the
   RF2 source file counts.
4. For row count mismatches: re-run the full pipeline. The drop/recreate
   model ensures a clean restart.
5. For referential integrity violations: query the specific child and
   parent tables in the stage schema to characterise the violations
   before deciding whether to promote the check to blocking.

---

## Adding New Exit Codes

If a new error category is needed in a future phase:

1. Add a new subclass to `src/common/exceptions.py` inheriting from
   `SnomedBaseError`. Assign the next available exit code as the
   `exit_code` class attribute.
2. Add a corresponding entry to this document following the same
   structure: meaning, Python class, raised by, common causes, what
   to do.
3. Update `run.sh` if the orchestrator needs to handle the new code
   specifically.
4. Bump the version of this document and `exceptions.py`.

Current highest exit code in use: **5**  
Next available exit code: **6**

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
