# ARC_FILE: docs/todo.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — Master Todo
# Version: 1.3
# Updated: 2026-05-22
# ============================================================
#
# Revision policy: review and update at the start of every
# working session and after every commit.
# ============================================================

## PHASE 0 — STEP 0.5 (db_connection.py) — IN PROGRESS

- [x] database.yaml updated to v1.4 (Oracle usernames as keys)
- [x] config_loader.py MANDATORY_KEYS updated
- [x] conventions.md updated to v1.5
- [x] _get_credentials implemented and tested (Round 1, 10/10 Ubuntu + OCI)
- [x] get_connection implemented and tested (Round 2, 10/10 Ubuntu + OCI)
- [x] open_connection implemented and tested (Round 3, 9/9 Ubuntu)
- [x] test_connection implemented and tested (Round 4, 9/9 Ubuntu)
- [x] execute_ddl implemented and tested (Round 5, 10/10 Ubuntu)
- [x] execute_batch implemented (Round 6 written, not yet run)
- [ ] Run Round 6 tests (execute_batch) on Ubuntu
- [ ] execute_query (returns list[tuple])
- [ ] get_pool (stub, raises NotImplementedError)
- [ ] Write orchestrator tests/test_db_connection_py.py
- [ ] Write tests/protocols/test_db_connection_py.md
- [ ] Run real DB tests on OCI (SNOMED_TEST_REAL_DB=true)
- [ ] Formal closing commit: "feat: Step 0.5 complete"

## PHASE 0 — STEP 0.6 (Bootstrap script)

- [ ] Implement scripts/bootstrap.sh
      Purpose: general prerequisite gate for all phases.
      Checks: dirs, venv, env vars, Oracle reachable (test_connection),
      prints environment summary. Exit 0 = safe to proceed.
      Does NOT invoke pipeline scripts.
- [ ] Write tests/test_bootstrap_sh.sh
- [ ] Write tests/protocols/test_bootstrap_sh.md
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
- [ ] ~/.bashrc on OCI and Mac — rename SNOMED_ADMIN_DB_PASSWORD
      to SNOMED_SYS_DB_PASSWORD (Ubuntu done; verify OCI and Mac)

## TOOLING (extract after Phase 0)

- [ ] Extract workflow aliases and functions to standalone Git repo
      (separate from ACE — personal productivity infrastructure).
      Current functions: xi, xo, xed, xcat, xclear, xcf, xcaf,
      xcom, xpull, xbash, xpy, xrun, xsup, xsd, xdep, xmd
      alias: ace
      See docs/conventions.md workflow section for rationale.
- [ ] Implement xmd in workflow repo (Markdown transformer):
      strips line 1 path comment, passes to pandoc.
      Pandoc: apt install pandoc / brew install pandoc.
- [ ] Extract arc CLI to own Git repository after Phase 0
- [ ] arc-clean command (clear outbox/inbox)
- [ ] arc-commit command (git add/commit/push wrapper)
- [ ] Shell detection fix in arc_setup.sh (bash vs zsh on Mac)
- [ ] arc-init-relay (create transfer dirs on OCI via SSH)
- [ ] Validation layer (check remote reachable before rsync)
- [ ] Write arc documentation (README, howto)

## DOCS

- [ ] Commit docs/road_map.md v1.2
- [ ] Commit docs/phase0_foundation.md v1.7
- [ ] Commit docs/snomed_vocabulary.md v0.4
- [ ] Commit docs/conventions.md v1.5
- [ ] Update docs/runbooks/run_sql_setup.md — verify reflects v1.3
- [ ] Reconstruct docs/directory_structure.md if stale
- [ ] docs/conventions.md — update Python version after 3.12 upgrade

## ACCESSIBILITY

- [ ] Ava American English Voxin voice on order — install when received
- [ ] Investigate Orca crash in Vim at end of lines (Ubuntu)
      — open in general project
- [ ] Magic Keyboard Bluetooth pairing on Ubuntu:
      bluetoothctl → pair → connect → trust
- [ ] Ubuntu power cable replacement — arriving next week

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
