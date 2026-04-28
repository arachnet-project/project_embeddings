# Arachnet Clinical Embeddings — Project Summary
# docs/project_summary.md
# =========================================
# Version: 1.1
# Last updated: 2026-04-28
# Purpose: Full project context for session handover and crash recovery.
#          Covers project overview, conventions, Phase 0 progress,
#          and immediate next actions.


## 1. Project overview

Arachnet Clinical Embeddings is a SNOMED CT terminology embedding platform
built on Oracle 23ai (being upgraded to 26ai). It ingests SNOMED CT RF2
release files, loads them into Oracle, validates completeness, swaps stage
to production, and produces clinical embeddings for downstream use.

Owner: Jan Mura.
Licence: BUSL 1.1 (to be added to repository).

### Platforms

Two active machines:

Ubuntu on MacBook Air (hostname: jan-MacBookAir) — primary development
and testing machine. MacBook Air hardware running Ubuntu Linux natively,
no macOS, no virtual machine. Python venv, mocked database tests,
Git origin. All development happens here first.

OCI — Oracle Cloud Infrastructure. Production target. Oracle database
currently at 23ai, being upgraded to 26ai. Real database tests run here
with SNOMED_TEST_REAL_DB=true.

Mac Studio — Phase 3 ML computations only. Not a pipeline or development
machine. Not relevant until Phase 3.

### Infrastructure

Oracle database on OCI (23ai, upgrading to 26ai).
Two application schemas: snomed (production) and snomed_stage (stage).
Tablespaces: TBS_SNOMED and TBS_SNOMED_STAGE.
Profile: NO_EXPIRY_PROFILE — no password expiry for application accounts.
TNS alias: ARADB. TNS_ADMIN must be set in environment before any script runs.

### Project root paths

OCI:    /home/opc/project_embeddings
Ubuntu: /home/jan/project_embeddings


## 2. Technology stack and conventions

### Python
Python 3.10.12 currently installed on Ubuntu — upgrade to 3.12.x pending.
Python venv must be rebuilt after upgrade.
python-oracledb in thin mode only. No Oracle client installation needed.
OmegaConf for configuration management.
PyYAML for YAML parsing.
Standard library only beyond the above. No frameworks.

### Oracle tooling
SQLcl 24.4.1 or later — used by sql_setup.sh for one-time database setup.
Command available as sql on PATH.

### Bash
Bash 4.0 or later required. Ubuntu ships Bash 5.x.
set -euo pipefail and export LC_ALL=C.UTF-8 in all executable scripts.
Sourced library files do not set shell options.

### Conventions
Conventions are documented in docs/conventions.md, currently version 1.5.
Key points:
- 4-space indentation in Python and SQL.
- .format() for all Python string formatting. No f-strings.
- Block markers around every Python function definition.
- Type annotations from _validate_mandatory_keys onward. No retrofitting.
- NumPy-style docstrings in all Python functions.
- Plain Python testing with _report and _summarise pattern. No pytest.
- SQL keywords in uppercase. Schema, table, column names in lowercase.
- Bash logging via scripts/common/logger.sh. No bare echo for log messages.
- Pipeline scripts may use config_loader --export for configuration.
- Infrastructure scripts must be self-contained, no venv dependency.


## 3. Repository structure

project_embeddings/
    config/
        project.yaml          — root config, includes database.yaml and ingestion.yaml
        database.yaml         — DB connection, schemas, table registry (version 1.3)
        ingestion.yaml        — Phase 1 RF2 ingestion pipeline config

    src/
        common/
            exceptions.py     — project exception hierarchy
            logger.py         — Python logging utility
            config_loader.py  — YAML config loader (Step 0.4, complete)
            db_connection.py  — Oracle connection helper (Step 0.6, pending)

    scripts/
        common/
            logger.sh         — Bash logging library (version 1.1, complete)
            functions.sh      — shared Bash functions (version 1.1, complete)
            run.sh            — main pipeline orchestrator (Step 0.7, pending)
        run_tests.sh          — run all tests (version 1.1, complete)
        sql_setup.sh          — one-time database schema setup runner

    tests/
        test_exceptions_py.py          — 45 tests, passing
        test_logger_py.py              — 13 tests, passing
        test_logger_sh.sh              — passing
        test_functions_sh.sh           — 10 tests, passing (new, version 1.2)
        test_config_loader_py.py       — orchestrator, 32 tests, passing
        test_config_loader_r1_py.py    — Round 1
        test_config_loader_r2_py.py    — Round 2
        test_config_loader_r3_py.py    — Round 3
        test_config_loader_r4_py.py    — Round 4
        test_db_connection_py.py       — empty placeholder, Step 0.6 pending
        protocols/
            test_logger_sh.md
            test_logger_py.md
            test_exceptions_py.md
            test_config_loader_py.md
            test_db_connection_py.md   — to be written in Step 0.6
        results/                       — not committed to Git

    sql/
        ddl/
            setup/
                00_create_profile.sql       — version 1.1, complete
                01_create_tablespaces.sql   — version 1.1, complete
                02_create_schemas.sql       — version 1.1, complete
                03_grants.sql               — version 1.0, complete
            tables/                         — one file per SNOMED CT table, Phase 1

    docs/
        conventions.md              — version 1.5
        directory_structure.md      — version 1.4
        error_codes.md
        git_workflow.md
        phase0_foundation.md
        project_summary.md          — this file, version 1.1
        todo.md                     — empty, needs reconstruction
        todo_step_0_5.md            — Step 0.5 SQL setup todo
        todo_step_0_6.md            — Step 0.6 db_connection todo, to be written
        runbooks/
            run_sql_setup.md

    log/                            — not committed to Git
    venv/                           — not committed to Git
    requirements.txt
    syn.sh                          — rsync sync script
    .gitignore
    LICENSE                         — BUSL 1.1, to be added


## 4. Phase 0 status

Step 0.1 — YAML configuration files — Complete.
    config/project.yaml, config/database.yaml, config/ingestion.yaml written
    and validated.

Step 0.2 — Error handling — Complete.
    src/common/exceptions.py written and tested.
    Exception hierarchy: SnomedBaseError, SnomedConfigError,
    SnomedDBConnectionError, SnomedDDLError, SnomedLoadError,
    SnomedValidationError.

Step 0.3 — Logging utility — Complete.
    src/common/logger.py written and tested.
    scripts/common/logger.sh written and tested.

Step 0.4 — Configuration loader — Complete.
    src/common/config_loader.py written and tested.
    32 tests passing on Ubuntu.

Step 0.5 — SQL database setup — Complete (scripts written, not yet run on OCI).
    All four SQL setup scripts written and reviewed.
    scripts/sql_setup.sh written.
    docs/conventions.md updated to version 1.5.
    docs/directory_structure.md updated to version 1.4.
    NOTE: SQL scripts have not yet been run on OCI. Schemas snomed and
    snomed_stage do not yet exist in the database.

Step 0.5a — Bash infrastructure corrections — Complete.
    scripts/common/logger.sh corrected and updated to version 1.1.
    scripts/common/functions.sh corrected and updated to version 1.1.
    scripts/run_tests.sh corrected and updated to version 1.1.
    tests/test_functions_sh.sh written, version 1.2, 10 tests passing.
    Full test suite: 6 test scripts, all passing on Ubuntu.

Step 0.6 — Database connection helper — Pending.
    src/common/db_connection.py not yet written.
    tests/test_db_connection_py.py is an empty placeholder.
    Design agreed. Blocked on: Python upgrade, SQL scripts on OCI,
    Oracle upgrade to 26ai.

Step 0.7 — Bash pipeline orchestrator — Pending.
    scripts/common/run.sh not yet written.


## 5. Bash infrastructure scripts

### Current files and versions

scripts/common/logger.sh — version 1.1
    Bash logging library. Provides log_debug, log_info, log_warn, log_error.
    Reads SNOMED_LOG_DIR and SNOMED_LOG_LEVEL from environment.
    Log level locked at source time.
    Sourced library — does not set shell options.

scripts/common/functions.sh — version 1.1
    Shared Bash functions library.
    Provides require_var, require_command, run_test, summarise_tests.
    Initialises _pass, _fail, _failed_labels with safe defaults at source time.
    Sourced library — does not set shell options.

scripts/run_tests.sh — version 1.1
    Runs all unit and integration tests in sequence.
    Sets SNOMED_LOG_DIR before sourcing logger.sh.
    Handles both Ubuntu (mocked) and OCI (real DB via SNOMED_TEST_REAL_DB).
    Can be run from any directory.

scripts/sql_setup.sh — version 1.1
    One-time database schema setup runner.
    Runs the four SQL files in sql/ddl/setup/ in order via SQLcl as SYSDBA.
    RUN_00=true to include 00_create_profile.sql on a fresh instance.

tests/test_functions_sh.sh — version 1.2
    10 tests covering require_var, require_command, run_test, summarise_tests,
    and counter defaults. All passing on Ubuntu.


## 6. SQL setup work

All four SQL files are complete and follow conventions.md SQL conventions.
Run as SYSDBA via scripts/sql_setup.sh.
Status: not yet run on OCI.

sql/ddl/setup/00_create_profile.sql — version 1.1
    Creates NO_EXPIRY_PROFILE. Skip on OCI where it already exists.
    Use RUN_00=true to include on a fresh instance.

sql/ddl/setup/01_create_tablespaces.sql — version 1.1
    Creates TBS_SNOMED and TBS_SNOMED_STAGE.
    Each starts at 1G, autoextends by 512M, no maximum size.

sql/ddl/setup/02_create_schemas.sql — version 1.1
    Creates snomed and snomed_stage users.
    Passwords set to CHANGEME_BEFORE_USE — must be changed immediately
    after running. Never commit real passwords to version control.

sql/ddl/setup/03_grants.sql — version 1.0
    Grants CONNECT, RESOURCE, CREATE SESSION, UNLIMITED TABLESPACE,
    CREATE TABLE, CREATE VIEW, CREATE SEQUENCE, CREATE PROCEDURE
    to both snomed and snomed_stage.


## 7. claude_chat.py

Information about this file was not available at the time this summary
was written. To be documented in a future session.


## 8. What comes immediately next

In order:

1. Upgrade Python to 3.12.x on Ubuntu (jan-MacBookAir).
   Rebuild venv after upgrade.
   Rerun bash scripts/run_tests.sh to confirm all tests still pass.

2. Run SQL setup scripts on OCI.
   Follow runbook in docs/runbooks/run_sql_setup.md.
   Confirm snomed and snomed_stage schemas are created successfully.
   Change passwords immediately after running 02_create_schemas.sql.

3. Upgrade Oracle on OCI from 23ai to 26ai.
   Expected to be a straightforward upgrade.
   Confirm database is healthy after upgrade.

4. After steps 1 through 3 are complete, discuss next steps with Jan
   before beginning Step 0.6.


## 9. Open questions and pending decisions

- claude_chat.py — what is this file and what is its current version?
  Needs to be documented in the project summary.

- docs/todo.md is empty after the crash. Needs to be reconstructed.
  To be done after the Python upgrade and OCI work is complete.

- docs/todo_step_0_6.md needs to be written before Step 0.6 begins.

- After Oracle upgrade to 26ai, confirm whether any connection parameters
  or oracledb thin mode settings need to change.

- OCI test run: once SQL scripts are run and Oracle is upgraded, run
  bash scripts/run_tests.sh with SNOMED_TEST_REAL_DB=false on OCI to
  confirm the Bash infrastructure works correctly there too.

