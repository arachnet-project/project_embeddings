# Phase 0 — Foundation & Shared Infrastructure
## Arachnet Clinical Embeddings — Technical Documentation

**Project:** Arachnet Clinical Embeddings  
**Owner:** Jan Mura, Arachnet Project z.s.  
**Environment:** OCI Frankfurt, Oracle Linux 9, Oracle Database 23ai  
**Document version:** 1.1  
**Date:** 2026-03-26  
**Status:** In progress

---

## Purpose

This document describes the foundation layer of the Arachnet Clinical Embeddings platform. Phase 0 establishes the shared utilities, configuration design, and conventions that all subsequent phases (1–5) depend on. No phase script executes without these components in place.

Phase 0 produces no clinical data output. Its outputs are infrastructure: configuration files, shared Python modules, Bash utilities, and documented conventions.

---

## Implementation Note

Steps are defined in and must be executed in the sequence given in this document. Each step has explicit dependencies on earlier steps. Implementing steps out of order will result in modules that must be retrofitted to comply with conventions defined later.

The sequence below differs from the original logical component list. It reflects the correct build order:

- Error handling conventions are defined first because every module depends on them.
- Logging is implemented second because every subsequent module uses it.
- Configuration loading is third because it depends on both logger and exceptions.
- Database connection helper is fourth because it depends on the config loader.
- The Bash orchestrator is fifth because it wires all of the above together.
- YAML configuration files are treated as Step 0.1 because they were completed first and are a prerequisite for all code steps.

---

## Step 0.1 — Configuration Design (YAML File Schemas)

**Status:** Complete

### Purpose

Define the structure, ownership, and validation rules for all YAML configuration files in scope for Phase 1, following a pattern extensible to later phases.

### Inputs

- Requirements gathered from Phase 1 steps: schema names, connection parameters, file paths, release version
- Architectural decision: global config files shared across all phases vs phase-specific config files

### Outputs

Three YAML configuration files with full inline documentation:

- `config/project.yaml` — global, phase-independent project configuration
- `config/database.yaml` — database connection, schema definitions, table registry
- `config/ingestion.yaml` — Phase 1 RF2 ingestion pipeline configuration

### Key design decisions

**OmegaConf** is used for YAML loading and variable interpolation. Interpolation syntax is `${path.to.key}`.

`active_environment` is a top-level key. The config loader reads it and indexes into the `environments` block to resolve the active path set. Switching between `production` and `dev` requires changing only this one key.

All passwords are referenced via environment variable names only. No credential values appear in any YAML file. The environment variables must be set in `.bashrc` or equivalent before any script runs. The deploy script checks for their presence and aborts with a clear message if any are missing.

`database.yaml` includes a table registry (Option C): table name, schema ownership, RF2 source folder, RF2 filename pattern, and a one-line description per table. Full DDL lives in `sql/ddl/`. Oracle `ALL_TAB_COLUMNS` is the runtime authoritative source for column definitions.

`ingestion.yaml` derives table load sequence from the order of entries in `database.yaml`. No separate load order list is maintained. To skip a table during development or debugging, add its name to `skip_tables` in `ingestion.yaml`. In production `skip_tables` must always be empty.

`includes` in `project.yaml` lists the phase-specific config files to be merged by the config loader. Each included file is merged as a named sub-tree (`cfg.database`, `cfg.ingestion`) to prevent key collisions.

### Mandatory key convention

Keys that are essential for the system to function are marked with an inline `# REQUIRED` comment directly on the same line as the key in the YAML file. This is the single authoritative source for mandatory key definitions. No separate schema document is maintained — a separate document would create a second place to update and risk drift with the YAML files themselves.

The config loader enforces mandatory keys by checking a list defined in the loader code, derived from the `# REQUIRED` annotations. If a mandatory key is absent, the loader aborts with exit code 1 and identifies the file and key by name. Unrecognised keys produce a warning but do not abort, allowing forward compatibility as new keys are added in later phases.

### Naming convention for future phase config files

Phase-specific YAML files follow the pattern `<phase_name>.yaml`, for example `embedding.yaml`, `policy.yaml`, `query.yaml`. They are listed in the `includes` block of `project.yaml` and merged as named sub-trees by the config loader.

---

## Step 0.2 — Error Handling Conventions

**Status:** Pending

**Depends on:** Step 0.1 — error messages reference config file names and keys defined there

### Purpose

Define and document the error handling contract that all scripts across all phases must follow. This step produces the conventions and base exception classes that every subsequent module imports. It is implemented before any other code so that nothing needs to be retrofitted.

### Inputs

- Review of Step 0.1 outputs — config file names, mandatory keys
- High-level compliance requirements from Phase 5

### Process

1. Define standard exit codes for the project.
2. Define the fail fast, fail loudly rule — no silent error suppression anywhere.
3. Define `set -euo pipefail` as mandatory in all Bash scripts.
4. Define the Python exception hierarchy for project-specific exceptions.
5. Document how errors propagate from Python to Bash via exit codes and from Bash to the orchestrator.

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

All project exceptions inherit from `SnomedBaseError`. Each exception class carries its exit code as a class attribute so that Bash wrappers can retrieve it without hardcoding the mapping in two places.

### Fail fast, fail loudly rule

No exception may be caught and suppressed silently anywhere in the project. Every caught exception must either be re-raised, logged and re-raised, or logged and converted to a non-zero exit. A bare `except: pass` is forbidden. A `finally` block that cleans up resources is permitted as long as the exception still propagates.

### Bash conventions

All Bash scripts must begin with:

```bash
set -euo pipefail
```

`-e` aborts on any non-zero exit code. `-u` aborts on reference to an unset variable. `-o pipefail` propagates failures through pipes. These three flags together implement fail fast at the shell level without requiring explicit exit code checks after every command.

### Outputs

- `src/common/exceptions.py` — Python base exception classes
- `docs/error_codes.md` — exit code reference document

---

## Step 0.3 — Logging Utility

**Status:** Pending

**Depends on:** Step 0.2 — logging failure paths raise `SnomedBaseError` subclasses, not generic exceptions

### Purpose

Provide structured, consistent logging across all Python and Bash scripts in the project, suitable for audit and compliance requirements in later phases.

### Inputs

- `config/project.yaml` — log directory path, environment name
- Log level from environment variable `SNOMED_LOG_LEVEL`, default `INFO`

### Process

1. Initialise a Python `logging` handler writing to both stdout and a rotating log file.
2. Log format includes: timestamp (ISO 8601), log level, phase, step, script name, message.
3. Expose a `get_logger(name)` function importable by all Python modules.
4. Provide Bash logging functions (`log_info`, `log_warn`, `log_error`) sourced by all Bash scripts, writing to the same log directory in the same format.
5. Log file naming convention: `snomed_<phase>_<step>_<YYYYMMDD_HHMMSS>.log`

### Error handling

- Log directory not writable — fall back to stdout only, emit a warning via stderr. Do not raise an exception — a logging failure must never suppress the original operation.
- Never catch and suppress exceptions to protect log integrity.

### Outputs

- `src/common/logger.py` — importable Python module
- `scripts/common/logger.sh` — sourceable Bash script

---

## Step 0.4 — Configuration Loader

**Status:** Pending

**Depends on:** Step 0.2 (raises typed exceptions on config errors), Step 0.3 (logs warnings on unrecognised keys)

### Purpose

Provide a single, reusable Python utility that reads one or more YAML configuration files, validates their contents, merges them into a single config object, and makes values available to both Python modules and Bash scripts.

### Inputs

- YAML file paths resolved from project root by convention
- Mandatory key list derived from `# REQUIRED` annotations in YAML files

### Process

1. Accept one or more YAML file paths as command-line arguments.
2. Load `project.yaml` first, then merge files listed in its `includes` block as named sub-trees (`cfg.database`, `cfg.ingestion`).
3. Resolve OmegaConf interpolations.
4. Resolve `active_environment` and expose the active path set directly as `cfg.paths`.
5. Validate mandatory keys are present. Raise `SnomedConfigError` (exit code 1) with file name and key name if any mandatory key is absent.
6. Log a warning on unrecognised keys — not an error, allows forward compatibility.
7. When called as a CLI tool from Bash: output `export KEY=VALUE` lines suitable for `eval`.
8. When imported as a Python module: return the resolved OmegaConf config object.

### Environment variable naming convention

Config values exported to Bash follow the convention `SNOMED_<SECTION>_<KEY>` in uppercase, for example `SNOMED_PROJECT_NAME`, `SNOMED_DB_TNS_ALIAS`, `SNOMED_PATHS_LOG`.

### Error handling

- Missing mandatory key — `SnomedConfigError`, exit code 1, message identifies file and key
- YAML parse error — `SnomedConfigError`, exit code 1, includes line reference from OmegaConf
- Type mismatch — `SnomedConfigError`, exit code 1
- Interpolation resolution failure — `SnomedConfigError`, exit code 1

### Outputs

- `src/common/config_loader.py` — usable as CLI tool and importable Python module

---

## Step 0.5 — Database Connection Helper

**Status:** Pending

**Depends on:** Step 0.2 (raises typed DB exceptions), Step 0.3 (logs connection events), Step 0.4 (reads connection parameters from config)

### Purpose

Provide a reusable Python module that establishes and manages Oracle 23ai database connections, abstracting all connection details from phase scripts.

### Inputs

- Config object from `config_loader.py` — TNS alias, schema names, pool parameters
- Passwords from environment variables only — never from the config object

### Process

1. Read connection parameters from the config object and passwords from environment variables — never hardcoded.
2. Establish connections using `oracledb` thin client. No Oracle Client installation required.
3. Expose the following interface:

| Method | Purpose |
|--------|---------|
| `get_connection(schema)` | Returns a single direct connection for the named schema |
| `get_pool(schema)` | Returns a connection pool — Phase 3 and 4 use only |
| `execute_ddl(conn, sql)` | Executes DDL with error handling |
| `execute_batch(conn, sql, data, batch_size)` | Bulk DML via `executemany()` |

4. All connections use `autocommit=False` — explicit commit required everywhere.
5. Phase 1 ingestion uses `get_connection()` only. Direct dedicated connections are correct for bulk load. The pool is not used in Phase 1.

### Error handling

- Connection failure — retry once, then raise `SnomedDBConnectionError`, exit code 2. Full error detail logged. Credential values are never logged under any circumstances.
- Credential resolution failure — raise `SnomedDBConnectionError`, exit code 2.
- DDL failure — raise `SnomedDDLError`, exit code 3. SQL statement and Oracle error code included in exception.
- Batch insert failure — rollback transaction, raise `SnomedLoadError`, exit code 4. Affected table and batch number logged.

### Outputs

- `src/common/db_connection.py` — importable Python module

---

## Step 0.6 — Bash Orchestrator Skeleton

**Status:** Pending

**Depends on:** All previous steps (0.1 through 0.5)

### Purpose

Provide the top-level Bash entry point that sources configuration, initialises logging, validates the environment, and invokes phase scripts in sequence with consistent error propagation.

### Inputs

- YAML file paths resolved from project root by convention
- Phase and step selection parameters: run all, run specific phase, run specific step

### Process

1. Set `set -euo pipefail`.
2. Source `scripts/common/logger.sh`.
3. Call `src/common/config_loader.py` with required YAML files and `eval` the output to populate environment variables.
4. Validate all mandatory environment variables are set before invoking any phase script. Abort with explicit variable name in error message if any are missing.
5. Invoke phase scripts in order, checking exit codes after each.
6. On non-zero exit code from any step: log failure with phase identity, step identity, and exit code, then abort. Do not proceed to the next step.
7. On full success: log completion with timestamp and data release version.

### Deploy and initialisation mode

`run.sh` also serves as the deploy and initialisation entry point when invoked with `--init`. In init mode it:

- Creates any directories defined in `project.yaml` that do not yet exist
- Verifies the virtual environment exists at the path defined in `project.yaml`
- Checks all required environment variables are set and reports clearly on any that are missing
- Does not invoke any phase pipeline scripts

A new terminal session or a fresh machine is initialised by running `run.sh --init` before any pipeline run.

### Error handling

- Any step returning non-zero exit code — abort pipeline, log phase, step, and exit code
- Missing environment variable after config load — abort with explicit variable name

### Outputs

- `scripts/run.sh` — main project entry point and init script

---

## Directory Structure (Phase 0 outputs)

```
project_embeddings/
├── config/
│   ├── project.yaml
│   ├── database.yaml
│   └── ingestion.yaml
├── src/
│   └── common/
│       ├── exceptions.py
│       ├── logger.py
│       ├── config_loader.py
│       └── db_connection.py
├── scripts/
│   └── common/
│       ├── logger.sh
│       └── run.sh
├── docs/
│   ├── phase0_foundation.md     ← this document
│   └── error_codes.md
└── sql/
    └── ddl/                     ← populated in Phase 1
```

---

## Dependencies and Environment Requirements

All Phase 0 code runs inside the project virtual environment located at `{paths.venv}` as defined in `project.yaml`.

Python packages required for Phase 0:

| Package | Purpose |
|---------|---------|
| `oracledb` | Oracle 23ai thin client — no Oracle Client installation required |
| `omegaconf` | YAML loading and variable interpolation |

The following environment variables must be set before any script runs. The `run.sh --init` command checks for all of them and reports clearly on any that are missing.

| Variable | Purpose |
|----------|---------|
| `TNS_ADMIN` | Path to directory containing `tnsnames.ora` and `sqlnet.ora` |
| `SNOMED_DB_PASSWORD` | Password for the `snomed` production schema |
| `SNOMED_STAGE_DB_PASSWORD` | Password for the `snomed_stage` schema |
| `SNOMED_ADMIN_DB_PASSWORD` | Password for the `system` DBA user — initial setup only |
| `SNOMED_LOG_LEVEL` | Log verbosity — optional, defaults to `INFO` |

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used by permission of SNOMED International. SNOMED and SNOMED CT are registered trademarks of SNOMED International.

Czech national SNOMED CT affiliate licence administered by UZIS.
