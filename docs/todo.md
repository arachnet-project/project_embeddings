# docs/todo.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — Master Todo
# Version: 1.1
# Updated: 2026-05-13
# ============================================================

## IMMEDIATE — next Ubuntu session

- [ ] Run Round 1 tests on Ubuntu:
      python tests/test_db_connection_r1_py.py

- [ ] Commit pending files from Ubuntu:
      src/common/db_connection.py
      docs/conventions.md
      docs/project_summary.md
      docs/todo.md
      tests/test_db_connection_r1_py.py
      git commit -m "feat: db_connection.py v1.0 in progress, conventions v1.5"
      git push
      Then git pull on OCI and Mac.

- [ ] Update ~/.bashrc on Ubuntu:
      Rename SNOMED_ADMIN_DB_PASSWORD to SNOMED_SYS_DB_PASSWORD

- [ ] Deploy clean .bashrc and .bash_profile to OCI:
      Files produced 2026-05-10, in downloads.
      Fill in real passwords before copying.
      Backup first: cp ~/.bash_profile ~/.bash_profile.bak

- [ ] Install Voxin voices on Ubuntu for better Orca experience.


## PHASE 0 — STEP 0.6 (db_connection.py)

- [x] database.yaml updated to v1.4 (Oracle usernames as keys)
- [x] config_loader.py MANDATORY_KEYS updated
- [x] conventions.md updated to v1.5 (import section labels)
- [x] _get_credentials implemented
- [x] get_connection implemented
- [x] test_db_connection_r1_py.py written (10 tests)
- [ ] Run Round 1 tests — NEXT
- [ ] Write Round 2 tests (get_connection mocked error paths)
- [ ] Implement open_connection (context manager)
- [ ] Implement execute_ddl
- [ ] Implement execute_batch
- [ ] Implement execute_query (returns list[dict], keys lowercased)
- [ ] Implement test_connection
- [ ] Implement get_pool (stub, raises NotImplementedError)
- [ ] Write orchestrator test_db_connection_py.py
- [ ] Write tests/protocols/test_db_connection_py.md
- [ ] Run real DB tests on OCI (SNOMED_TEST_REAL_DB=true)


## PHASE 0 — STEP 0.5 CLOSE

- [ ] Resolve 26ai patch — waiting for Oracle support (Slavomír Seno)
- [ ] Python 3.12 upgrade on Ubuntu — deferred, low priority
- [ ] Fix SET VERIFY OFF in run_sql_setup.sh heredoc (passwords shown)
- [ ] Formal closing commit for Step 0.5


## PHASE 0 — STEP 0.7

- [ ] Implement scripts/run.sh (pipeline orchestrator)
- [ ] Blocked on Step 0.6 completion


## INFRASTRUCTURE

- [ ] OCI security hardening:
      - fail2ban installation and configuration
      - cron audit — review all scheduled jobs
      - log rotation verification
      - unattended-upgrades for security patches
- [ ] Add SNOMED release check cron job (Phase 1 concern)
- [ ] Add LICENSE (BUSL 1.1) to repository
- [ ] Resolve 26ai patch with Oracle support


## ARC CLI

- [ ] Extract arc to own Git repository after Phase 0
      New Claude project already started with arc_project_summary.md
- [ ] arc-clean command (clear outbox/inbox)
- [ ] arc-commit command (git add/commit/push wrapper)
- [ ] Shell detection fix in arc_setup.sh (bash vs zsh on Mac)
- [ ] arc-init-relay (create transfer dirs on OCI via SSH)
- [ ] Validation layer (check remote reachable before rsync)
- [ ] Write arc documentation (README, howto)


## DOCS

- [ ] Update docs/runbooks/run_sql_setup.md — verify reflects v1.3
- [ ] Reconstruct docs/directory_structure.md if stale
- [ ] docs/conventions.md — update Python version after 3.12 upgrade


## ACCESSIBILITY

- [ ] Install Voxin voices on Ubuntu
- [ ] Magic Keyboard Bluetooth pairing on Ubuntu:
      bluetoothctl → pair → connect → trust
- [ ] Get MagSafe 2 replacement cable for MacBook Air


## UZIS / EXTERNAL

- [ ] Await response from MUDr. Molinari re: development sample
- [ ] Follow up on SNOMED International namespace registration
- [ ] Confirm ModuleId (SCTID) for Czech extension
- [ ] Get complete refset inventory from UZIS


## PHASE 1 (future — after Phase 0 complete)

- [ ] SQL table DDL files in sql/ddl/tables/
- [ ] RF2 ingestion pipeline
- [ ] Validation framework
- [ ] Stage to production swap mechanism
- [ ] SQLcl MCP Server setup for development QA
