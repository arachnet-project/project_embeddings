# Directory Structure — Arachnet Clinical Embeddings

**Document version:** 1.1
**Date:** 2026-03-28

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
│       └── db_connection.py         # Oracle connection helper (Step 0.5)
│
├── scripts/                         # Bash scripts
│   └── common/                      # Shared Bash utilities
│       ├── logger.sh                # Bash logging library (sourced)
│       └── run.sh                   # Main orchestrator / init (Step 0.6)
│
├── tests/                           # All test material
│   ├── test_logger_sh.sh            # Test for scripts/common/logger.sh
│   ├── test_logger_py.py            # Test for src/common/logger.py
│   ├── test_exceptions_py.py        # Test for src/common/exceptions.py
│   ├── test_config_loader_py.py     # Test for src/common/config_loader.py (Step 0.4)
│   ├── test_db_connection_py.py     # Test for src/common/db_connection.py (Step 0.5)
│   ├── protocols/                   # Test protocols — one per test script
│   │   ├── test_logger_sh.md
│   │   ├── test_logger_py.md
│   │   ├── test_exceptions_py.md
│   │   ├── test_config_loader_py.md # Step 0.4
│   │   └── test_db_
connection_py.md # Step 0.5
│   └── results/                     # Test results — NOT committed to Git
│       └── .gitkeep
│
├── docs/                            # Architecture and reference documentation
│   ├── phase0_foundation.md         # Phase 0 technical documentation
│   ├── error_codes.md               # Exit code reference
│   ├── directory_structure.md       # This document
│   └── git_workflow.md              # Git workflow for all machines
│
├── sql/                             # SQL files
│   └── ddl/                         # Table and schema DDL (Phase 1)
│
├── log/                             ← NOT committed to Git
│   └── snomed.log                   # Current log (rotated daily)
│
├── venv/                            ← NOT committed to Git
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

### `docs/`

Architecture, design, and operational reference documents only. No test
protocols or results. Updated in place — Git history preserves previous
versions. No parallel versioned copies.

### `tests/`

All test material: executable scripts, protocols, and local results.
Test scripts are always executed directly — never sourced. Results in
`tests/results/` are machine-local and not committed.

### `scripts/common/logger.sh`

Sourced library — not executed directly. Does not set shell options,
traps, or locale variables. Those belong in the calling script.

### `log/`

Machine-local. Never committed. Created automatically on first log write.
Rotated daily by Python's `TimedRotatingFileHandler`.

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
