# Phase 0 — Foundation & Shared Infrastructure
## Arachnet Clinical Embeddings — Technical Documentation

**Project:** Arachnet Clinical Embeddings
**Owner:** Jan Mura, Arachnet Project z.s.
**Document version:** 1.5
**Date:** 2026-04-06
**Status:** In progress

---

## Purpose

Phase 0 establishes shared utilities, configuration, and conventions that
all subsequent phases depend on. It produces no clinical data output.
Outputs are infrastructure: configuration files, shared Python modules,
Bash utilities, and documented conventions.

Target platforms: Oracle Linux 9 (OCI, production), Ubuntu (development).
Unix/Linux only. Mac Studio reserved for Phase 3 ML computations.

---

## Build order

Steps must be executed in sequence. Each step depends on all prior steps.

1. Step 0.1 — YAML configuration files
2. Step 0.2 — Error handling conventions
3. Step 0.3 — Logging utility
4. Step 0.4 — Configuration loader
5. Step 0.5 — Database connection helper
6. Step 0.6 — Bash orchestrator

---

## Step 0.1 — Configuration Design

**Status:** Complete

### Outputs

- `config/project.yaml`
- `config/database.yaml`
- `config/ingestion.yaml`

### Key decisions

OmegaConf for YAML loading and interpolation. Syntax: `${path.to.key}`.

`active_environment` is a top-level key. Switching environments requires
changing only this one key. Valid values: `production`, `development`.

Passwords referenced by environment variable name only. No credential
values in any YAML file.

`database.yaml` table registry: table name, schema ownership, RF2 folder,
RF2 filename pattern, description. Full DDL in `sql/ddl/`.

`ingestion.yaml` derives table load sequence from `database.yaml` order.

`includes` in `project.yaml` lists files merged as named sub-trees
(`cfg.database`, `cfg.ingestion`).

Mandatory keys marked `# REQUIRED` inline. Config loader enforces them
and aborts with exit code 1 if absent. Unrecognised keys produce a
warning only.

---

## Step 0.2 — Error Handling

**Status:** Complete

### Outputs

- `src/common/exceptions.py`
- `docs/error_codes.md`

### Exit codes

0 — Success
1 — Configuration error
2 — Database connection error
3 — DDL error
4 — Data load error
5 — Validation error

### Python exception hierarchy

SnomedBaseError(Exception)
  SnomedConfigError        exit code 1
  SnomedDBConnectionError  exit code 2
  SnomedDDLError           exit code 3
  SnomedLoadError          exit code 4
  SnomedValidationError    exit code 5

Each class carries `exit_code` as a class attribute. `detail` parameter
is free-form string, never contains credentials.

No silent exception suppression. `except: pass` is forbidden.
`finally` for resource cleanup is permitted — exception must propagate.

### Bash conventions

All executable scripts begin with:

    set -euo pipefail
    export LC_ALL=C.UTF-8

`LC_ALL=C.UTF-8` is set in executable scripts, not sourced libraries.

---

## Step 0.3 — Logging Utility

**Status:** Complete

### Outputs

- `src/common/logger.py`
- `scripts/common/logger.sh`
- `tests/test_logger_py.py`
- `tests/test_logger_sh.sh`
- `tests/protocols/test_logger_py.md`
- `tests/protocols/test_logger_sh.md`

### Design

Logger reads from environment variables only. No dependency on config
loader or OmegaConf.

- `SNOMED_LOG_DIR` — log directory. Falls back to `./log/` if unset,
  stdout only if not writable (warning to stderr).
- `SNOMED_LOG_LEVEL` — verbosity. Default: `INFO`.

Python: thin wrapper around standard `logging`. `TimedRotatingFileHandler`
rotates at midnight, retains 30 days. Current file: `snomed.log`.

Bash: sourced library. Does not set shell options or locale.

Log format (both):

    YYYY-MM-DDTHH:MM:SS | LEVEL    | name                                     | message

When Step 0.4 is complete, config loader exports `SNOMED_LOG_DIR` and
`SNOMED_LOG_LEVEL` automatically, closing the bootstrapping loop.

---

## Step 0.4 — Configuration Loader

**Status:** In progress

### Outputs

- `src/common/config_loader.py`
- `tests/test_config_loader_py.py`
- `tests/protocols/test_config_loader_py.md`

### Process

1. Load `project.yaml` with OmegaConf.
2. Read `includes` list, load each file, merge as named sub-trees.
3. Resolve `active_environment`, expose active paths as `cfg.paths`.
4. Walk tree once to force interpolation resolution.
5. Validate mandatory keys — raise `SnomedConfigError` (exit 1) if absent.
6. CLI mode: print `export KEY=VALUE` lines for eval in Bash.
   Module mode: return resolved OmegaConf config object.

Mandatory key list hardcoded in loader (Option A).
Lists silently skipped in CLI export.
Env var naming: `SNOMED_<SECTION>_<KEY>` uppercase.

---

## Step 0.5 — Database Connection Helper

**Status:** Pending

**Depends on:** Steps 0.2, 0.3, 0.4

### Outputs

- `src/common/db_connection.py`
- `tests/test_db_connection_py.py`
- `tests/protocols/test_db_connection_py.md`

### Interface

- `get_connection(schema)` — direct connection for named schema
- `get_pool(schema)` — connection pool, Phase 3 and 4 only
- `execute_ddl(conn, sql)` — DDL with error handling
- `execute_batch(conn, sql, data, batch_size)` — bulk DML via executemany

`autocommit=False` on all connections. Phase 1 uses `get_connection()` only.

---

## Step 0.6 — Bash Orchestrator

**Status:** Pending

**Depends on:** All previous steps

### Outputs

- `scripts/run.sh`
- `tests/test_run_sh.sh`
- `tests/protocols/test_run_sh.md`

### Purpose

Top-level Bash entry point. Sources config, initialises logging,
validates environment, invokes phase scripts with error propagation.

`run.sh --init` creates missing directories, verifies venv, checks all
required environment variables. Does not invoke pipeline scripts.

---

## Dependencies

Python packages: `oracledb`, `omegaconf`

Environment variables:

- `SNOMED_LOG_DIR` — all machines
- `SNOMED_LOG_LEVEL` — all machines, default INFO
- `LC_ALL` — C.UTF-8, all machines
- `TNS_ADMIN` — OCI only
- `SNOMED_DB_PASSWORD` — OCI only
- `SNOMED_STAGE_DB_PASSWORD` — OCI only
- `SNOMED_ADMIN_DB_PASSWORD` — OCI only, setup only
- `ANTHROPIC_API_KEY` — all machines

---

## Attribution

This material includes SNOMED Clinical Terms (SN

