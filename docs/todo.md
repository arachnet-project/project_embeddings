# docs/todo.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — Master Todo
# Version: 1.0 (reconstructed 2026-05-09)
# ============================================================

## IMMEDIATE (before next session)

- [ ] Re-enable automatic backups on OCI (CRITICAL):
      oci db database update --database-id $OCI_DATABASE_OCID \
          --auto-backup-enabled true \
          --auto-backup-window SLOT_TWO \
          --recovery-window-in-days 7

- [ ] Find MUDr. Molinari email address and send draft email
      (draft in docs/uzis_correspondence.md)

- [ ] Send email to Slavomír Seno (Oracle) re: 26ai patch findings

- [ ] Git commit to close Step 0.5:
      git commit -m "chore: Step 0.5 complete — schemas, grants verified"
      git push && ssh ara "cd project_embeddings && git pull"


## PHASE 0 — REMAINING

### Step 0.5 close
- [ ] 26ai patch — resolve with Oracle support or try Jan patch
- [ ] Python 3.12 upgrade on Ubuntu (deferred, low priority)
- [ ] Verify run_sql_setup.sh output: add SET VERIFY OFF to suppress
      password display in substitution output

### Step 0.6 — db_connection.py
- [ ] Write docs/todo_step_0_6.md
- [ ] Implement src/common/db_connection.py
- [ ] Write tests/test_db_connection_py.py
- [ ] Write tests/protocols/test_db_connection_py.md
- [ ] Run mocked tests on Ubuntu
- [ ] Run real DB tests on OCI (SNOMED_TEST_REAL_DB=true)

### Step 0.7 — Bash pipeline orchestrator
- [ ] Implement scripts/run.sh
- [ ] Blocked on Step 0.6


## INFRASTRUCTURE

- [ ] Re-enable auto-backups (see IMMEDIATE above)
- [ ] OCI security hardening:
      - fail2ban installation and configuration
      - cron audit — review all scheduled jobs
      - log rotation verification
      - unattended-upgrades for security patches
- [ ] Add SNOMED release check cron job (Phase 1 concern)
- [ ] Resolve 26ai patch failure with Oracle support
- [ ] Add LICENSE (BUSL 1.1) to repository


## ARC CLI

- [ ] Fix shell detection on Mac (bash vs zsh)
- [ ] Implement outbox cleanup (arc-clean command or --delete option)
- [ ] Test arc-openlink end-to-end on Ubuntu
- [ ] Extract arc to own Git repository after Phase 0
- [ ] Write arc documentation (howto, README)
- [ ] Add arc_install.sh for easier deployment


## DOCS

- [ ] Reconstruct docs/todo.md — DONE (this file)
- [ ] Write docs/todo_step_0_6.md
- [ ] Update docs/conventions.md — Python version when upgraded
- [ ] Verify docs/runbooks/run_sql_setup.md reflects v1.3
- [ ] Add docs/runbooks/patch_26ai.md — DONE 2026-05-09
- [ ] Add docs/contacts.md — DONE 2026-05-09
- [ ] Update docs/uzis_correspondence.md — DONE 2026-05-09


## UZIS / EXTERNAL

- [ ] Send email to MUDr. Molinari requesting development sample
- [ ] Follow up on SNOMED International namespace registration
- [ ] Clarify ModuleId (SCTID) for Czech extension
- [ ] Get complete refset inventory from UZIS


## PHASE 1 (future)

- [ ] RF2 ingestion pipeline
- [ ] SQL table definitions in sql/ddl/tables/
- [ ] Ingestion scripts
- [ ] Validation framework
- [ ] Stage to production swap mechanism
