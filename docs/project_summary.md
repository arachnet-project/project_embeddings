# =============================================================================
# Arachnet Clinical Terminology Embeddings — Project Summary
# docs/project_summary.md
# =============================================================================
# Purpose:
#   Current project state, completed work, pending tasks, and conventions.
#   Read this at the start of every new session to restore context.
#
# Author:  Jan Mura
# Version: 1.5
# Updated: 2026-05-20
# =============================================================================

## Project overview

Vector search system for SNOMED CT clinical terminology.
Oracle database backend (thin mode, oracledb).
Three schemas: snomed (production), snomed_stage (ingestion), sys (DBA).
Runs on OCI (ARM, production/test DB) and Ubuntu (development, no DB).
macOS used occasionally for lightweight editing.

## Repository

github.com:arachnet-project/project_embeddings.git
Branch: main
OCI remote alias: ara

## Directory layout

project_embeddings/
    src/common/
        db_connection.py        — Oracle connection module (see below)
        exceptions.py           — SnomedConfigError, SnomedDBConnectionError, etc.
        logger.py               — get_logger(), structured log format
    tests/
        test_db_connection_r1_py.py   — Round 1: _get_credentials, 10/10
        test_db_connection_r2_py.py   — Round 2: get_connection, 10/10 (v1.1)
    docs/
        conventions.md          — v1.4, coding and naming conventions
        git_workflow.md         — commit message format and rules
        project_summary.md      — this file
        todo.md                 — task list
    config/
        database.yaml           — tns_alias, schema user/password_env_var entries
    wrk/
        commit.sh               — git stage/commit/push helper
        pull.sh                 — git pull + status helper
    requirements.txt            — oracledb==4.0.0 (plus transitive deps)
    .gitignore                  — includes venv/, wenv/

## Completed steps

### Step 0.6 — db_connection foundation
- _get_credentials implemented and tested (Round 1, 10/10 Ubuntu and OCI)
- get_connection implemented with retry logic and SYSDBA support
- Round 2 tests written (v1.0), one assertion fixed (v1.1), 10/10 Ubuntu and OCI
- All committed and pushed to GitHub

### Tooling and environment
- Ubuntu: venv active, oracledb installed, .bashrc with clipboard functions applied
- OCI: venv active, oracledb+deps installed (ARM wheel), .bashrc status — TBD (verify)
- bashrc functions: xi, xo, xed, xcat, xclear, xcf, xcaf, xcom, xpull, xbash, xpy, xrun, xsup, xsd
- alias ace="cd /home/jan/project_embeddings && source venv/bin/activate"
- wrk/commit.sh — stage/commit/push; needs msg= and files=() updated before each use
- wrk/pull.sh — pull + git status; run from project root

### Pending small task
- Add git status to end of wrk/commit.sh (before final echo "Done.")

## Current state — GitHub

All clean. Last commit: 9650b88
test: update test_db_connection_r2_py.py fix autocommit assertion v1.1

## Next step — Step 0.7: open_connection

Implement open_connection() in src/common/db_connection.py.
This is a @contextmanager wrapper around get_connection() that ensures
the connection is always closed, even on exception.

Signature:
    @contextmanager
    def open_connection(cfg: DictConfig, schema: str):
        ...

Usage pattern (from module docstring):
    with open_connection(cfg, "snomed") as conn:
        execute_batch(conn, sql, data, batch_size)
        conn.commit()

After open_connection, remaining functions to implement:
    execute_ddl       — run DDL statements (CREATE TABLE etc.)
    execute_batch     — bulk insert/update via executemany
    execute_query     — SELECT returning rows
    test_connection   — lightweight connectivity check
    get_pool          — connection pool stub (later)

Each function follows the same pattern:
    implement → write Round N tests → run on Ubuntu → commit → pull OCI → run on OCI

## Log level difference between machines

OCI logs at DEBUG level (shows Credentials resolved, Connecting to Oracle lines).
Ubuntu logs at INFO level only.
Not a bug — logger config differs between environments. Note for later investigation.

## Key conventions

- Commit messages: type: short description (feat/fix/test/docs/chore)
- No passwords in cfg — only env var names. Passwords from os.environ only.
- autocommit always False — caller manages commit/rollback
- oracledb thin mode only — no Oracle client installation
- All DB access through db_connection.py — no direct oracledb imports elsewhere
- Test files named test_<module>_r<N>_py.py (not .py extension in name, just suffix)
- Block markers: # --- function_name --- / # --- end function_name ---
