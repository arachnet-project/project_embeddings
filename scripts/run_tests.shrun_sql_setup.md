# Arachnet Clinical Embeddings — SQL Setup Runbook
# docs/runbooks/run_sql_setup.md
# =========================================
# Version: 1.0
# Last updated: 2026-04-20
# Applies to: Step 0.5 — Database schema setup

## Purpose

This runbook describes how to run the one-time SQL setup scripts that
prepare a fresh Oracle database instance for the Arachnet Clinical
Embeddings project. These scripts create the tablespaces, schemas,
profile, and grants required before Phase 1 ingestion can begin.

These scripts are run manually by the operator as SYSDBA. They are not
run by the Python pipeline.

## Oracle client

SQLcl version 24.4.1.0 Production Build 24.4.1.042.1221.
Connection method: TNS. TNS alias: ARADB.
TNS_ADMIN must be set in the environment before connecting.

## Scripts in execution order

All scripts are in sql/ddl/setup/. Run them in numeric order.

    00_create_profile.sql     — Create NO_EXPIRY_PROFILE.
                                Skip on OCI where it already exists.
    01_create_tablespaces.sql — Create TBS_SNOMED and TBS_SNOMED_STAGE.
    02_create_schemas.sql     — Create snomed and snomed_stage users.
    03_grants.sql             — Grant privileges to both schemas.

## Automated method (recommended)

Use scripts/sql_setup.sh. It connects as SYSDBA over TNS, runs the
scripts in order, and spools all output to a timestamped log file.

Set required environment variables before running:

    export SNOMED_ADMIN_DB_PASSWORD="your_sysdba_password"
    export DB_TNS_ALIAS="ARADB"
    export TNS_ADMIN="/path/to/tns/directory"

On OCI where NO_EXPIRY_PROFILE already exists, run:

    bash scripts/sql_setup.sh

On a genuinely fresh instance where the profile does not exist, run:

    RUN_00=true bash scripts/sql_setup.sh

Output is spooled to log/sql_setup/sql_setup_YYYYMMDDTHHMMSS.log.
Review the spool file after running to confirm no errors.

## Manual method

If running scripts manually via SQLcl, connect as SYSDBA:

    sql system/"${SNOMED_ADMIN_DB_PASSWORD}"@ARADB as sysdba

Inside SQLcl, spool output before running each script:

    SPOOL /home/opc/project_embeddings/log/sql_setup/sql_setup_manual.log
    SET FEEDBACK ON
    SET ECHO ON
    WHENEVER SQLERROR EXIT FAILURE

    @/home/opc/project_embeddings/sql/ddl/setup/01_create_tablespaces.sql
    @/home/opc/project_embeddings/sql/ddl/setup/02_create_schemas.sql
    @/home/opc/project_embeddings/sql/ddl/setup/03_grants.sql

    SPOOL OFF
    EXIT

## Verification queries

After running all scripts, verify the setup by running these queries
inside SQLcl connected as SYSDBA. All queries should return the expected
rows shown.

### Confirm tablespaces exist

    SELECT tablespace_name, status, contents
    FROM dba_tablespaces
    WHERE tablespace_name IN ('TBS_SNOMED', 'TBS_SNOMED_STAGE')
    ORDER BY tablespace_name;

Expected: two rows, both ONLINE, both PERMANENT.

### Confirm users exist

    SELECT username, default_tablespace, temporary_tablespace, profile
    FROM dba_users
    WHERE username IN ('SNOMED', 'SNOMED_STAGE')
    ORDER BY username;

Expected: two rows.
    SNOMED        TBS_SNOMED        TEMP    NO_EXPIRY_PROFILE
    SNOMED_STAGE  TBS_SNOMED_STAGE  TEMP    NO_EXPIRY_PROFILE

### Confirm profile assignment

    SELECT username, profile
    FROM dba_users
    WHERE profile = 'NO_EXPIRY_PROFILE'
    ORDER BY username;

Expected: at minimum SNOMED, SNOMED_STAGE, SYS, SYSTEM.

### Confirm grants

    SELECT grantee, privilege
    FROM dba_sys_privs
    WHERE grantee IN ('SNOMED', 'SNOMED_STAGE')
    ORDER BY grantee, privilege;

Expected: multiple rows for each grantee including CREATE SESSION,
CREATE TABLE, CREATE VIEW, CREATE SEQUENCE, CREATE PROCEDURE,
UNLIMITED TABLESPACE.

## After verification

Change the placeholder passwords immediately:

    ALTER USER snomed IDENTIFIED BY your_chosen_password;
    ALTER USER snomed_stage IDENTIFIED BY your_chosen_password;

Set the runtime environment variables on OCI:

    export SNOMED_DB_PASSWORD="your_chosen_password"
    export SNOMED_STAGE_DB_PASSWORD="your_chosen_password"

These should be set in your shell profile or a sourced env file that
is not committed to Git. See .gitignore — env_setup.sh is excluded.

## Spool log location

    log/sql_setup/sql_setup_YYYYMMDDTHHMMSS.log

Log directory is created automatically by scripts/sql_setup.sh.
Log files are not committed to Git.
=== BEGIN FILE: docs/directory_structure.md ===
# Directory Structure — Arachnet Clinical Embeddings

**Document version:** 1.3
**Date:** 2026-04-20

---

## Overview

All project files live under a single root directory `project_embeddings/`.

| Machine | Project root |
|---------|-------------|
| OCI (production) | `/home/opc/project_embeddings` |
| Ubuntu (dev primary) | `/home/jan/project_embeddings` |

Mac Studio: Phase 3 ML computations only — not a pipeline or dev machine.

---

## Full structure

```
project_embeddings/
│
├── config/                          # YAML configuration files
│   ├── project.yaml                 # Global, phase-independent config
│   ├── database.yaml                # DB connection, schemas, table registry
│   └── ingestion.yaml               # Phase 1 RF2 ingestion pipeline config
│
├── src/                             # Python source code
│   └── common/                      # Shared utilities — all phases
│       ├── exceptions.py            # Project exception hierarchy
│       ├── logger.py                # Python logging utility
│       ├── config_loader.py         # YAML config loader (Step 0.4)
│       └── db_connection.py         # Oracle connection helper (Step 0.6)
│
├── scripts/                         # Bash scripts
│   ├── common/                      # Shared Bash utilities
│   │   ├── logger.sh                # Bash logging library (sourced)
│   │   └── run.sh                   # Main orchestrator / init (Step 0.7)
│   └── sql_setup.sh                 # One-time DB schema setup runner
│                                    # Runs sql/ddl/setup/ scripts as SYSDBA
│
├── tests/                           # All test material
│   ├── test_logger_sh.sh            # Test for scripts/common/logger.sh
│   ├── test_logger_py.py            # Test for src/common/logger.py
│   ├── test_exceptions_py.py        # Test for src/common/exceptions.py
│   ├── test_config_loader_py.py     # Test for src/common/config_loader.py (Step 0.4)
│   ├── test_db_connection_py.py     # Test for src/common/db_connection.py (Step 0.6)
│   ├── protocols/                   # Test protocols — one per test script
│   │   ├── test_logger_sh.md
│   │   ├── test_logger_py.md
│   │   ├── test_exceptions_py.md
│   │   ├── test_config_loader_py.md # Step 0.4
│   │   └── test_db_connection_py.md # Step 0.6
│   └── results/                     # Test results — NOT committed to Git
│       └── .gitkeep
│
├── docs/                            # Architecture and reference documentation
│   ├── conventions.md               # Coding and documentation conventions
│   ├── directory_structure.md       # This document
│   ├── error_codes.md               # Exit code reference
│   ├── git_workflow.md              # Git workflow for all machines
│   ├── phase0_foundation.md         # Phase 0 technical documentation
│   ├── todo.md                      # Master todo list
│   ├── todo_step_0_5.md             # Step 0.5 detailed todo (SQL setup)
│   ├── todo_step_0_6.md             # Step 0.6 detailed todo (db_connection)
│   └── runbooks/                    # Operator runbooks — manual procedures
│       └── run_sql_setup.md         # How to run sql/ddl/setup/ scripts
│
├── sql/                             # SQL files
│   └── ddl/                         # DDL scripts
│       ├── setup/                   # One-time database setup — run as SYSDBA
│       │   │                        # in numeric order before Phase 1
│       │   ├── 00_create_profile.sql    # Create NO_EXPIRY_PROFILE
│       │   │                            # Skip if profile already exists
│       │   ├── 01_create_tablespaces.sql # Create TBS_SNOMED and
│       │   │                            # TBS_SNOMED_STAGE
│       │   ├── 02_create_schemas.sql    # Create snomed and snomed_stage
│       │   │                            # users with profile and tablespaces
│       │   └── 03_grants.sql            # Grant privileges to both schemas
│       └── tables/                  # One file per SNOMED CT table
│                                    # Populated in Phase 1
│                                    # 17 tables defined in database.yaml
│
├── log/                             # NOT committed to Git
│   └── snomed.log                   # Current log (rotated daily)
│
├── venv/                            # NOT committed to Git
│
├── requirements.txt
├── syn.sh                           # rsync sync script
├── .gitignore
└── LICENSE                          # BUSL 1.1 (to be added)
```

---

## Naming conventions

### Test scripts

Pattern: `test_<component>_<language>.sh` or `test_<component>_<language>.py`

The language suffix (`_sh`, `_py`) is used consistently for all test
scripts, even when only one language test exists for a component. This
ensures a uniform naming pattern that scales cleanly when both Bash and
Python tests exist for the same component.

| Source file | Test script |
|-------------|-------------|
| `scripts/common/logger.sh` | `tests/test_logger_sh.sh` |
| `src/common/logger.py` | `tests/test_logger_py.py` |
| `src/common/exceptions.py` | `tests/test_exceptions_py.py` |
| `src/common/config_loader.py` | `tests/test_config_loader_py.py` |
| `src/common/db_connection.py` | `tests/test_db_connection_py.py` |
| `scripts/common/run.sh` | `tests/test_run_sh.sh` |

### Test protocols

Same name as the test script, in `tests/protocols/`, as markdown:

| Test script | Protocol |
|-------------|----------|
| `tests/test_logger_sh.sh` | `tests/protocols/test_logger_sh.md` |
| `tests/test_logger_py.py` | `tests/protocols/test_logger_py.md` |

### Test results

Not committed to Git. Stored locally in `tests/results/` if kept at all.
Filename pattern: `<test_name>_<machine>_<YYYY-MM-DD>.md`

Example: `tests/results/test_logger_sh_oci_2026-03-28.md`

---

## Notes on key directories

### `docs/runbooks/`

Operator runbooks for manual procedures that are not part of the automated
pipeline. Each runbook covers one procedure end to end: prerequisites,
steps, verification queries, and follow-up actions. Runbooks are committed
to Git and kept up to date.

### `docs/`

Architecture, design, and operational reference documents only. No test
protocols or results. Updated in place — Git history preserves previous
versions. No parallel versioned copies.

### `sql/ddl/setup/`

One-time setup scripts run as SYSDBA on a fresh Oracle instance. Numbered
to make execution order unambiguous. On the OCI production instance
NO_EXPIRY_PROFILE already exists — skip 00_create_profile.sql there.
These scripts are not run by the Python pipeline. They are run via
scripts/sql_setup.sh or manually following docs/runbooks/run_sql_setup.md.

### `sql/ddl/tables/`

One SQL file per SNOMED CT table, named to match the table name, for
example sct_concept.sql. Populated in Phase 1. Each file creates the
table in the production schema. The stage schema mirrors all tables
identically during ingestion.

### `tests/`

All test material: executable scripts, protocols, and local results.
Test scripts are always executed directly — never sourced. Results in
`tests/results/` are machine-local and not committed.

### `scripts/common/logger.sh`

Sourced library — not executed directly. Does not set shell options,
traps, or locale variables. Those belong in the calling script.

### `log/`

Machine-local. Never committed. Created automatically on first log write.
Rotated daily by Python's `TimedRotatingFileHandler`. The subdirectory
log/sql_setup/ is created by scripts/sql_setup.sh when first run.

---

## `.gitignore`

```
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Logs
log/
*.log

# Test results — local only
tests/results/*
!tests/results/.gitkeep

# Environment and credentials
.env
env_setup.sh

# OS
.DS_Store
```

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
=== END FILE: docs/directory_structure.md ===
