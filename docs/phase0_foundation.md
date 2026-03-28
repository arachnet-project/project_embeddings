# Phase 0 — Foundation & Shared Infrastructure
## Arachnet Clinical Embeddings — Technical Documentation

**Project:** Arachnet Clinical Embeddings
**Owner:** Jan Mura, Arachnet Project z.s.
**Environment:** OCI Frankfurt, Oracle Linux 9, Oracle Database 23ai
**Document version:** 1.4
**Date:** 2026-03-28
**Status:** In progress

---

## Purpose

This document describes the foundation layer of the Arachnet Clinical
Embeddings platform. Phase 0 establishes the shared utilities,
configuration design, and conventions that all subsequent phases (1–5)
depend on. No phase script executes without these components in place.

Phase 0 produces no clinical data output. Its outputs are infrastructure:
configuration files, shared Python modules, Bash utilities, and documented
conventions.

**Target platforms:** Oracle Linux 9 (OCI, production), Ubuntu (primary
development). Unix/Linux only. Mac Studio is reserved for Phase 3
ML/embedding computations and is not a pipeline or development platform.

---

## Implementation Note

Steps are defined in and must be executed in the sequence given in this
document. Each step has explicit dependencies on earlier steps.
Implementing steps out of order will result in modules that must be
retrofitted to comply with conventions defined later.

Correct build order:

- Error handling conventions first — every module depends on them.
- Logging second — every subsequent module uses it.
- Configuration loading third — depends on logger and exceptions.
- Database connection helper fourth — depends on config loader.
- Bash orchestrator fifth — wires everything together.
- YAML configuration files are Step 0.1 — completed first, prerequisite
  for all code steps.

---

## Step 0.1 — Configuration Design (YAML File Schemas)

**Status:** Complete

### Outputs

- `config/project.yaml` — global, phase-independent project configuration
- `config/database.yaml` — database connection, schema definitions, table registry
- `config/ingestion.yaml` — Phase 1 RF2 ingestion pipeline configuration

### Key design decisions

**OmegaConf** used for YAML loading and variable interpolation.
Syntax: `${path.to.key}`.

`active_environment` is a top-level key. Switching environments requires
changing only this one key.

All passwords referenced via environment variable names only. No
credential values in any YAML file.

`database.yaml` table registry (Option C): table name, schema ownership,
RF2 source folder, RF2 filename pattern, description. Full DDL in
`sql/ddl/`. Oracle `ALL_TAB_COLUMNS` is authoritative for column
definitions at runtime.

`ingestion.yaml` derives table load sequence from `database.yaml` order.
No separate load order list.

`includes` in `project.yaml` lists phase-specific config files merged as
named sub-trees (`cfg.database`, `cfg.ingestion`).

### Mandatory key convention

Keys marked with `# REQUIRED` inline in YAML. Single authoritative
source — no separate schema document. Config loader enforces mandatory
keys and aborts with exit code 1 identifying file and key if absent.
Unrecognised keys produce a warning only.

### Future phase config naming

Pattern: `<phase_name>.yaml` — e.g. `embedding.yaml`, `policy.yaml`.

---

## Step 0.2 — Error Handling Conventions

**Status:** Complete

**Depends on:** Step 0.1

### Standard exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Configuration error |
| 2 | Database connection error |
| 3 | DDL error |
| 4 | Data load error |
| 5 | Validation error |

### Python exception hierarchy

```
SnomedBaseError(Exception)
├── SnomedConfigError        — exit code 1
├── SnomedDBConnectionError  — exit code 2
├── SnomedDDLError           — exit code 3
├── SnomedLoadError          — exit code 4
└── SnomedValidationError    — exit code 5
```

Each class carries `exit_code` as a class attribute. `detail` parameter
is a free-form string — never contains credential values.

### Fail fast, fail loudly

No silent exception suppression anywhere. `except: pass` is forbidden.
`finally` for resource cleanup is permitted — exception must still
propagate.

### Bash conventions

All executable Bash scripts must begin with:

```bash
set -euo pipefail
export LC_ALL=C.UTF-8
```

`LC_ALL=C.UTF-8` is set in executable scripts, not in sourced libraries.
It forces English output from system commands while preserving UTF-8
encoding for data. `C.UTF-8` is supported on Oracle Linux 9 and Ubuntu.

### Outputs

- `src/common/exceptions.py` — Complete
- `docs/error_codes.md` — Complete

---

## Step 0.3 — Logging Utility

**Status:** In progress

**Depends on:** Step 0.2

### Purpose

Provide structured, consistent logging across all Python and Bash scripts,
suitable for audit and compliance requirements in later phases.

### Bootstrapping note

The logger cannot read `project.yaml` directly — the config loader does
not exist yet. The logger reads configuration from environment variables
only:

- `SNOMED_LOG_DIR` — log directory. Falls back to `./log/` if not set.
  Falls back to stdout only if not writable, with a warning to stderr.
- `SNOMED_LOG_LEVEL` — verbosity. Default: `INFO`.

Both variables are set in `.bashrc` on each machine. When the config
loader is written (Step 0.4), it exports both variables automatically —
no change to the logger required.

The logger has zero dependencies on the config loader, YAML files, or
OmegaConf.

### Implementation

**Python logger** — thin wrapper around Python's standard `logging`
module. `TimedRotatingFileHandler` rotates at midnight, retains 30 days.
Current log file: `snomed.log`. Rotated files: `snomed.log.YYYY-MM-DD`.

**Bash logger** — sourced library (`scripts/common/logger.sh`). Does not
set shell options, traps, or locale variables — those are the
responsibility of calling scripts. Functions prefixed with `_` are
internal by naming convention only (Bash has no access control).

Both use the same log format:
```
YYYY-MM-DDTHH:MM:SS | LEVEL    | name                                     | message
```

### Locale handling

`LC_ALL=C.UTF-8` is set by each executable script that sources
`logger.sh`, not by `logger.sh` itself. Setting locale in a sourced
library would unexpectedly affect the parent shell's environment.

### Inputs

- `SNOMED_LOG_DIR` environment variable
- `SNOMED_LOG_LEVEL` environment variable

### Outputs

- `src/common/logger.py` — importable Python module
- `scripts/common/logger.sh` — sourceable Bash library

### Testing

- `tests/test_logger.sh` — platform verification test
- `docs/test_logger_protocol.md` — three-pass test protocol

Must pass on both platforms (Ubuntu, OCI Oracle Linux 9) before Step 0.3
is marked Complete.

---

## Step 0.4 — Configuration Loader

**Status:** Pending

**Depends on:** Steps 0.2, 0.3

### Purpose

Single reusable Python utility that reads YAML files, validates contents,
merges into a config object, and exports values to Bash and Python.

### Process

1. Accept YAML file paths as CLI arguments.
2. Load `project.yaml` first, merge `includes` as named sub-trees.
3. Resolve OmegaConf interpolations.
4. Resolve `active_environment`, expose active paths as `cfg.paths`.
5. Validate mandatory keys. Raise `SnomedConfigError` (exit 1) if absent.
6. Log warning on unrecognised keys.
7. As CLI: output `export KEY=VALUE` lines for `eval` — includes
   `SNOMED_LOG_DIR` and `SNOMED_LOG_LEVEL` to close bootstrapping loop.
8. As Python module: return resolved OmegaConf config object.

### Environment variable naming

`SNOMED_<SECTION>_<KEY>` uppercase — e.g. `SNOMED_PROJECT_NAME`,
`SNOMED_DB_TNS_ALIAS`, `SNOMED_PATHS_LOG`.

### Outputs

- `src/common/config_loader.py`

---

## Step 0.5 — Database Connection Helper

**Status:** Pending

**Depends on:** Steps 0.2, 0.3, 0.4

### Interface

| Method | Purpose |
|--------|---------|
| `get_connection(schema)` | Single direct connection for named schema |
| `get_pool(schema)` | Connection pool — Phase 3 and 4 only |
| `execute_ddl(conn, sql)` | DDL execution with error handling |
| `execute_batch(conn, sql, data, batch_size)` | Bulk DML via `executemany()` |

`autocommit=False` on all connections. Phase 1 uses `get_connection()`
only.

### Outputs

- `src/common/db_connection.py`

---

## Step 0.6 — Bash Orchestrator Skeleton

**Status:** Pending

**Depends on:** All previous steps

### Purpose

Top-level Bash entry point. Sources config, initialises logging,
validates environment, invokes phase scripts with error propagation.

`run.sh --init` creates missing directories, verifies venv, checks all
required environment variables. Does not invoke pipeline scripts.

### Outputs

- `scripts/run.sh`

---

## Directory Structure

```
project_embeddings/
│
├── config/
│   ├── project.yaml
│   ├── database.yaml
│   └── ingestion.yaml
│
├── src/
│   └── common/
│       ├── exceptions.py
│       ├── logger.py
│       ├── config_loader.py         ← Step 0.4
│       └── db_connection.py         ← Step 0.5
│
├── scripts/
│   └── common/
│       ├── logger.sh
│       └── run.sh                   ← Step 0.6
│
├── tests/
│   └── test_logger.sh
│
├── docs/
│   ├── phase0_foundation.md         ← this document
│   ├── error_codes.md
│   ├── test_logger_protocol.md
│   ├── directory_structure.md
│   └── git_workflow.md
│
├── sql/
│   └── ddl/                         ← populated in Phase 1
│
├── log/                             ← not committed to Git
├── venv/                            ← not committed to Git
├── requirements.txt
├── syn.sh
└── .gitignore
```

---

## Dependencies and Environment Requirements

| Package | Purpose |
|---------|---------|
| `oracledb` | Oracle 23ai thin client |
| `omegaconf` | YAML loading and variable interpolation |

| Variable | Purpose |
|----------|---------|
| `TNS_ADMIN` | Path to `tnsnames.ora` and `sqlnet.ora` (OCI only) |
| `SNOMED_LOG_DIR` | Log directory |
| `SNOMED_LOG_LEVEL` | Log verbosity — optional, default `INFO` |
| `SNOMED_DB_PASSWORD` | Password for `snomed` schema |
| `SNOMED_STAGE_DB_PASSWORD` | Password for `snomed_stage` schema |
| `SNOMED_ADMIN_DB_PASSWORD` | Password for `system` DBA user — setup only |
| `LC_ALL` | Set to `C.UTF-8` in `.bashrc` on all machines |

See `docs/git_workflow.md` for full `.bashrc` setup per machine.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.

Czech national SNOMED CT affiliate licence administered by UZIS.
