# ARC_FILE: docs/directory_structure.md
# Directory Structure — Arachnet Clinical Embeddings
# docs/directory_structure.md
#
# Version: 1.4
# Updated: 2026-06-05
# ============================================================

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
│   ├── ingestion.yaml               # Phase 1 RF2 ingestion pipeline config
│   └── templates/                   # File header templates
│       └── python_header.py         # Python file header template
│
├── src/                             # Python source code
│   └── common/                      # Shared utilities — all phases
│       ├── exceptions.py            # Project exception hierarchy
│       ├── logger.py                # Python logging utility
│       ├── config_loader.py         # YAML config loader (Step 0.4)
│       └── db_connection.py         # Oracle connection module (Step 0.5)
│
├── scripts/                         # Bash scripts
│   ├── common/                      # Shared Bash utilities
│   │   └── logger.sh                # Bash logging library (sourced)
│   ├── bootstrap.sh                 # Prerequisite gate (Step 0.6)
│   └── sql_setup.sh                 # One-time DB schema setup runner
│
├── tests/                           # All test material
│   ├── test_logger_sh.sh
│   ├── test_logger_py.py
│   ├── test_exceptions_py.py
│   ├── test_config_loader_py.py
│   ├── test_db_connection_r1_py.py  # Round 1: _get_credentials
│   ├── test_db_connection_r2_py.py  # Round 2: get_connection
│   ├── test_db_connection_r3_py.py  # Round 3: open_connection
│   ├── test_db_connection_r4_py.py  # Round 4: test_connection
│   ├── test_db_connection_r5_py.py  # Round 5: execute_ddl
│   ├── test_db_connection_r6_py.py  # Round 6: execute_batch
│   ├── test_db_connection_r7_py.py  # Round 7: execute_query
│   ├── test_db_connection_py.py     # Orchestrator — full Step 0.5 record
│   ├── test_bootstrap_sh.sh         # Step 0.6 (pending)
│   ├── protocols/                   # Test protocols — one per test script
│   │   ├── test_logger_sh.md
│   │   ├── test_logger_py.md
│   │   ├── test_exceptions_py.md
│   │   ├── test_config_loader_py.md
│   │   └── test_db_connection_py.md
│   └── results/                     # Test results — NOT committed to Git
│       └── .gitkeep
│
├── docs/                            # Project documentation
│   ├── claude_chat_howto.md         # Guide for using Claude in this project
│   ├── contacts.md                  # Project contacts
│   ├── conventions.md               # Coding and documentation conventions
│   ├── dev_workflow.md              # Developer workflow guide
│   ├── directory_structure.md       # This document
│   ├── error_codes.md               # Exit code reference
│   ├── git_workflow.md              # Git workflow for all machines
│   ├── infrastructure.md            # OCI and server infrastructure notes
│   ├── patch_26ai.md                # Oracle 23ai patch tracking
│   ├── phase0_foundation.md         # Phase 0 technical documentation
│   ├── project_summary.md           # Project summary for context restoration
│   ├── road_map.md                  # Project phase roadmap
│   ├── snomed_vocabulary.md         # SNOMED CT reference vocabulary
│   ├── todo.md                      # Master todo list
│   ├── todo_step_0_4.md             # Step 0.4 detailed todo
│   ├── todo_step_0_5.md             # Step 0.5 detailed todo
│   ├── uzis_correspondence.md       # UZIS correspondence log
│   ├── uzis_meeting_prep.md         # UZIS meeting preparation
│   └── runbooks/                    # Operator runbooks — manual procedures
│       └── run_sql_setup.md         # How to run sql/ddl/setup/ scripts
│
├── sql/                             # SQL files
│   └── ddl/                         # DDL scripts
│       ├── setup/                   # One-time database setup — run as SYSDBA
│       │   ├── 00_create_profile.sql
│       │   ├── 01_create_tablespaces.sql
│       │   ├── 02_create_schemas.sql
│       │   └── 03_grants.sql
│       └── tables/                  # One file per SNOMED CT table
│                                    # Populated in Phase 1
│
├── wrk/                             # NOT committed to Git
│                                    # Local scratch area: temp files,
│                                    # clipboard output, test output.
│                                    # commit.sh and pull.sh have moved
│                                    # to ~/arc/ (arc workflow repo).
│
├── log/                             # NOT committed to Git
│   └── snomed.log                   # Current log (rotated daily)
│
├── venv/                            # NOT committed to Git
│
├── requirements.txt
├── .gitignore
└── LICENSE                          # BUSL 1.1 (to be added)
```

---

## File header templates

Templates for file headers live in `config/templates/`. Every new file
must start with the `ARC_FILE:` path marker (line 1) followed by the
appropriate header template content.

Available templates:
- `config/templates/python_header.py` — Python file header

Bash and SQL header templates to be added before Step 0.6.

See `docs/conventions.md` for the ARC_FILE: marker convention and
docstring style rules. Note: `python_header.py` uses Google-style
docstrings; conventions.md mandates NumPy style. NumPy style takes
precedence — the template will be updated to reflect this.

Retrofitting existing Python files to follow the header template is
a pending task tracked in `docs/todo.md`.

---

## Naming conventions

### Test scripts

Pattern: `test_<component>_rN_py.py` for per-round files,
`test_<component>_py.py` for the orchestrator.

| Source file | Orchestrator | Rounds |
|-------------|-------------|--------|
| `src/common/db_connection.py` | `test_db_connection_py.py` | r1–r7 |
| `src/common/config_loader.py` | `test_config_loader_py.py` | — |
| `src/common/logger.py` | `test_logger_py.py` | — |
| `scripts/common/logger.sh` | `test_logger_sh.sh` | — |
| `scripts/bootstrap.sh` | `test_bootstrap_sh.sh` | — |

### Test protocols

Same name as the orchestrator, in `tests/protocols/`, as markdown.

### Test results

Not committed to Git. Stored locally in `tests/results/` if kept at all.
Filename pattern: `<test_name>_<machine>_<YYYY-MM-DD>.md`

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

# Working scratch area
wrk/

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
