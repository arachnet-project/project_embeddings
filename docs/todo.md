# ============================================================
# Arachnet Clinical Terminology Embeddings — Master Todo
# Version: 1.2
# Updated: 2026-05-21
# ============================================================


## PHASE 0 — STEP 0.5 (db_connection.py) — IN PROGRESS

- [x] database.yaml updated to v1.4 (Oracle usernames as keys)
- [x] config_loader.py MANDATORY_KEYS updated
- [x] conventions.md updated to v1.5 (import section labels)
- [x] _get_credentials implemented and tested (Round 1, 10/10 Ubuntu + OCI)
- [x] get_connection implemented and tested (Round 2, 10/10 Ubuntu + OCI)
- [ ] open_connection — context manager wrapping get_connection — NEXT
- [ ] execute_ddl
- [ ] execute_batch
- [ ] execute_query (returns list[tuple])
- [ ] test_connection
- [ ] get_pool (stub, raises NotImplementedError)
- [ ] Write orchestrator tests/test_db_connection_py.py
- [ ] Write tests/protocols/test_db_connection_py.md
- [ ] Run real DB tests on OCI (SNOMED_TEST_REAL_DB=true)
- [ ] Formal closing commit: "feat: Step 0.5 complete"


## PHASE 0 — STEP 0.6 (Bash orchestrator)

- [ ] Implement scripts/run.sh (pipeline orchestrator)
- [ ] Blocked on Step 0.5 completion


## PHASE 0 — STEP 0.4 CLOSE

- [ ] Resolve 26ai patch — waiting for Oracle support (Slavomír Seno)
- [ ] Python 3.12 upgrade on Ubuntu — deferred, low priority
- [ ] Fix SET VERIFY OFF in run_sql_setup.sh heredoc (passwords shown)
- [ ] Formal closing commit for Step 0.4


## INFRASTRUCTURE

- [ ] OCI security hardening:
      - fail2ban installation and configuration
      - cron audit — review all scheduled jobs
      - log rotation verification
      - unattended-upgrades for security patches
- [ ] Add SNOMED release check cron job (Phase 1 concern)
- [ ] Add LICENSE (BUSL 1.1) to repository
- [ ] Resolve 26ai patch with Oracle support


## TOOLING (extract after Phase 0)

- [ ] Extract .bashrc aliases and functions to own repository
      after Phase 0 — same pattern as arc CLI extraction.
      Current functions: xi, xo, xed, xcat, xclear, xcf, xcaf,
      xcom, xpull, xbash, xpy, xrun, xsup, xsd
      alias: ace


## ARC CLI (extract after Phase 0)

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
