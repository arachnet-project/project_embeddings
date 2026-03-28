# Phase 0 — Foundation & Shared Infrastructure
## Arachnet Clinical Embeddings — Technical Documentation

**Project:** Arachnet Clinical Embeddings
**Owner:** Jan Mura, Arachnet Project z.s.
**Environment:** OCI Frankfurt, Oracle Linux 9, Oracle Database 23ai
**Document version:** 1.3
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

---

## Implementation Note

Steps are defined in and must be executed in the sequence given in this
document. Each step has explicit dependencies on earlier steps.
Implementing steps out of order will result in modules that must be
retrofitted to comply with conventions defined later.

The sequence below differs from the original logical component list. It
reflects the correct build order:

- Error handling conventions are defined first because every module
  depends on them.
- Logging is implemented second because every subsequent module uses it.
- Configuration loading is third because it depends on both logger and
  exceptions.
- Database connection helper is fourth because it depends on the config
  loader.
- The Bash orchestrator is fifth because it wires all of the above
  together.
- YAML configuration files are treated as Step 0.1 because they were
  completed first and are a prerequisite for all code steps.

---

## Step 0.1 — Configuration Design (YAML File Schemas)

**Status:** Complete

### Purpose

Define the structure, ownership, and validation rules for all YAML
configuration files in scope for Phase 1, following a pattern extensible
to later phases.

### Outputs

- `config/project.yaml` — global, phase-independent project configuration
- `config/database.yaml` — database connection, schema definitions, table registry
- `config/ingestion.yaml` — Phase 1 RF2 ingestion pipeline configuration

### Key design decisions

**OmegaConf** is used for YAML loading and variable interpolation.
Interpolation syntax is `${path.to.key}`.

`active_environment` is a top-level key. The config loader reads it and
indexes into the `environments` block to resolve the active path set.
Switching between `production` and `dev` requires changing only this one
key.

All passwords are referenced via environment variable names only. No
credential values appear in any YAML file.

`database.yaml` includes a table registry (Option C): table name, schema
ownership, RF2 source folder, RF2 filename pattern, and a one-line
description per table. Full DDL lives in `sql/ddl/`. Oracle
`ALL_TAB_COLUMNS` is the runtime authoritative source for column
definitions.

`ingestion.yaml` derives table load sequence from the order of entries
in `database.yaml`. No separate load order list is maintained.

`includes` in `project.yaml` lists the phase-specific config files to be
merged by the config loader. Each included file is merged as a named
sub-tree (`cfg.database`, `cfg.ingestion`) to prevent key collisions.

### Mandatory key convention

Keys essential for the system to function are marked with an inline
`# REQUIRED` comment in the YAML file. This is the single authoritative
source for mandatory key definitions. No separate schema document is
maintained.

The config loader enforces mandatory keys by checking a list defined in
the loader code. If a mandatory key is absent, the loader aborts with
exit code 1 and identifies the file and key by name. Unrecognised keys
produce a warning but do not abort.

### Naming convention for future phase config files

Phase-specific YAML files follow the pattern `<phase_name>.yaml`, for
example `embedding.yaml`, `policy.yaml`, `query.yaml`.

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

Each exception class carries its exit code as a class attribute. The
`detail` parameter is a free-form string — table names, key names, Oracle
error codes. Never contains credential values.

### Fail fast, fail loudly rule

No exception may be caught and suppressed silently anywhere in the
project. A bare `except: pass` is forbidden. A `finally` block for
resource cleanup is permitted as long as the exception still propagates.

### Bash conventions

All Bash scripts must begin with:

```bash
set -euo pipefail
```

### Outputs

- `src/common/exceptions.py` — Python base exception classes. Complete.
- `docs/error_codes.md` — exit code reference with causes and remediation. Complete.

---

## Step 0.3 — Logging Utility

**Status:** In progress

**Depends on:** Step 0.2

### Purpose

Provide structured, consistent logging across all Python and Bash scripts,
suitable for audit and compliance requirements in later phases.

### Bootstrapping note

The logger cannot read `project.yaml` directly — the config loader does
not exist yet. The logger reads configuration from two environment
variables only:

- `SNOMED_LOG_DIR` — log directory. If not set, falls back to `./log/`
  relative to the current working directory. If not writable, falls back
  to stdout only with a warning to stderr.
- `SNOMED_LOG_LEVEL` — verbosity. Default: `INFO`.

Both variables are set in `.bashrc` on each machine. When the config
loader is written (Step 0.4), it exports both variables automatically.
The logger requires no code change at that point.

This gives the logger zero dependencies on the config loader, YAML files,
or OmegaConf.

### Implementation

The Python logger is a thin wrapper around Python's standard `logging`
module. Log files rotate daily using `TimedRotatingFileHandler` — a new
file starts at midnight, old files retained 30 days. Current log file is
always `snomed.log`. Rotated files are named `snomed.log.YYYY-MM-DD`.

The Bash logger is a sourced library. It does not set shell options or
traps — those are the responsibility of calling scripts. It does set
`LC_ALL=C.UTF-8` to ensure English output from system commands regardless
of shell locale.

Both loggers use the same format for consistent reading of mixed logs:
```
YYYY-MM-DDTHH:MM:SS | LEVEL    | name                                     | message
```

Functions prefixed with `_` are internal by convention. Bash has no true
access control — this is naming convention only.

### Inputs

- `SNOMED_LOG_DIR` environment variable
- `SNOMED_LOG_LEVEL` environment variable

### Outputs

- `src/common/logger.py` — importable Python module
- `scripts/common/logger.sh` — sourceable Bash library

### Testing

- `tests/test_logger.sh` — platform verification test
- `docs/test_logger_protocol.md` — test protocol with three passes and
  pass criteria table

Test must pass on all three platforms (macOS, Ubuntu, OCI) before Step
0.3 is marked Complete.

---

## Step 0.4 — Configuration Loader

**Status:** Pending

**Depends on:** Step 0.2 (raises typed exceptions on config errors),
Step 0.3 (logs warnings on unrecognised keys)

### Purpose

Provide a single, reusable Python utility that reads YAML configuration
files, validates their contents, merges them into a single config object,
and makes values available to both Python modules and Bash scripts.

### Process

1. Accept YAML file paths as command-line arguments.
2. Load `project.yaml` first, then merge files in its `includes` block as
   named sub-trees (`cfg.database`, `cfg.ingestion`).
3. Resolve OmegaConf interpolations.
4. Resolve `active_environment` and expose the active path set as
   `cfg.paths`.
5. Validate mandatory keys. Raise `SnomedConfigError` (exit 1) with file
   and key name if absent.
6. Log a warning on unrecognised keys.
7. As CLI tool: output `export KEY=VALUE` lines for `eval`. Includes
   `SNOMED_LOG_DIR` and `SNOMED_LOG_LEVEL` to close the bootstrapping loop.
8. As Python module: return the resolved OmegaConf config object.

### Environment variable naming convention

`SNOMED_<SECTION>_<KEY>` in uppercase, for example `SNOMED_PROJECT_NAME`,
`SNOMED_DB_TNS_ALIAS`, `SNOMED_PATHS_LOG`.

### Outputs

- `src/common/config_loader.py`

---

## Step 0.5 — Database Connection Helper

**Status:** Pending

**Depends on:** Steps 0.2, 0.3, 0.4

### Purpose

Provide a reusable Python module that establishes and manages Oracle 23ai
database connections, abstracting all connection details from phase scripts.

### Interface

| Method | Purpose |
|--------|---------|
| `get_connection(schema)` | Single direct connection for named schema |
| `get_pool(schema)` | Connection pool — Phase 3 and 4 only |
| `execute_ddl(conn, sql)` | DDL execution with error handling |
| `execute_batch(conn, sql, data, batch_size)` | Bulk DML via `executemany()` |

All connections use `autocommit=False`. Phase 1 uses `get_connection()`
only — the pool is not used until Phase 3.

### Outputs

- `src/common/db_connection.py`

---

## Step 0.6 — Bash Orchestrator Skeleton

**Status:** Pending

**Depends on:** All previous steps

### Purpose

Provide the top-level Bash entry point that sources configuration,
initialises logging, validates the environment, and invokes phase scripts
in sequence with consistent error propagation.

### Deploy and initialisation mode

`run.sh --init` creates missing directories, verifies the virtual
environment, and checks all required environment variables. Does not
invoke any pipeline scripts. Run on every new machine and at the start
of each terminal session if `.bashrc` is not configured.

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

Python packages required for Phase 0:

| Package | Purpose |
|---------|---------|
| `oracledb` | Oracle 23ai thin client |
| `omegaconf` | YAML loading and variable interpolation |

Required environment variables:

| Variable | Purpose |
|----------|---------|
| `TNS_ADMIN` | Path to `tnsnames.ora` and `sqlnet.ora` |
| `SNOMED_LOG_DIR` | Log directory — used by logger before config loader runs |
| `SNOMED_LOG_LEVEL` | Log verbosity — optional, default `INFO` |
| `SNOMED_DB_PASSWORD` | Password for `snomed` schema |
| `SNOMED_STAGE_DB_PASSWORD` | Password for `snomed_stage` schema |
| `SNOMED_ADMIN_DB_PASSWORD` | Password for `system` DBA user — setup only |

See `docs/git_workflow.md` for `.bashrc` setup per machine.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.

Czech national SNOMED CT affiliate licence administered by UZIS.
