# ARC_FILE: docs/phase0_foundation.md
# Phase 0 — Foundation & Shared Infrastructure
## Arachnet Clinical Embeddings — Technical Documentation

**Project:** Arachnet Clinical Embeddings
**Owner:** Jan Mura, Arachnet Project z.s.
**Document version:** 1.9
**Date:** 2026-08-27
**Status:** In progress

---

## Purpose

Phase 0 establishes shared infrastructure used by subsequent project
phases.

Its outputs include configuration files, shared Python modules,
logging and error-handling infrastructure, database-connection
support, bootstrap verification, tests, and technical documentation.

Phase 0 produces no clinical data output. It does not provision Oracle
objects and does not ingest SNOMED CT release files.

The staging-schema pattern is established as an architectural decision
during Phase 0. Creation and use of the Oracle application schemas
belong to Phase 1.

Primary verification platforms are:

- Ubuntu for development.
- Oracle Linux 9 on OCI for production-oriented and real Oracle
  verification.

Machine roles, Git permissions, and operational responsibilities are
defined in `docs/dev_workflow.md`.

Project-wide implementation conventions are defined in
`docs/conventions.md`.

---

## Phase 0 Work Sequence

The Phase 0 work sequence is:

1. Step 0.1 — Configuration design.
2. Step 0.2 — Error handling.
3. Step 0.3 — Logging utility.
4. Step 0.4 — Configuration loader.
5. Step 0.5 — Database connection module.
6. Step 0.6 — Bootstrap script.
7. Step 0.7 — Integration and conformance audit.

This sequence describes the order in which the shared infrastructure
is developed. It is not a strict runtime dependency chain.

The dependencies of each component are described in its own section.

A step marked `Complete` has completed its approved implementation and
step-level verification. Step 0.7 performs integration, regression,
and conformance verification across the completed Phase 0 components.

---

## Step 0.1 — Configuration Design

**Status:** Complete

### Outputs

- `config/project.yaml`
- `config/database.yaml`
- `config/ingestion.yaml`

### Dependencies

None within Phase 0.

### Design

OmegaConf loads YAML configuration and resolves interpolation using:

    ${path.to.key}

`active_environment` is a top-level configuration key. It selects one
of the configuration profiles defined in `project.yaml`.

Currently supported profiles are:

- `development`
- `production`

The meaning, machine assignments, and operational responsibilities
associated with these profiles are defined in
`docs/dev_workflow.md`.

Configuration profiles and bootstrap modes are separate concepts.

Credentials are referenced by environment-variable name only.
Credential values must never be stored in YAML configuration files.

`database.yaml` contains the table registry, including table names,
schema ownership, RF2 folders, filename patterns, and descriptions.

The table registry identifies expected tables and source inputs. It
does not define complete physical table structures.

Existing privileged Oracle setup DDL is stored under:

    sql/ddl/setup/

Application table-definition DDL belongs under:

    sql/ddl/tables/

Oracle provisioning and application-table implementation belong to
Phase 1.

`ingestion.yaml` derives its table load sequence from the ordering in
`database.yaml`.

The `includes` section of `project.yaml` identifies configuration
files loaded as named subtrees, including:

    cfg.database
    cfg.ingestion

Mandatory keys are marked `# REQUIRED` in the configuration files and
are enforced by the configuration loader.

Unrecognized configuration keys produce warnings rather than
immediate failure.

---

## Step 0.2 — Error Handling

**Status:** Complete

### Outputs

- `src/common/exceptions.py`
- `docs/error_codes.md`

### Dependencies

None within Phase 0.

### Exit Codes

    0 — Success
    1 — Configuration error
    2 — Database connection error
    3 — DDL error
    4 — Data load error
    5 — Validation error

### Python Exception Hierarchy

    SnomedBaseError(Exception)
        SnomedConfigError        exit code 1
        SnomedDBConnectionError  exit code 2
        SnomedDDLError           exit code 3
        SnomedLoadError          exit code 4
        SnomedValidationError    exit code 5

Each exception class carries `exit_code` as a class attribute.

The optional `detail` value is a free-form string and must never
contain credentials.

The shared exception hierarchy is available to components whose
approved interfaces use project-specific exceptions. Individual
component specifications may deliberately expose standard Python or
library exceptions instead.

Silent exception suppression is forbidden.

Resource cleanup in `finally` blocks is permitted when the original
exception continues to propagate.

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

### Dependencies

The logging implementation has no required implementation dependency
on another Phase 0 component.

It must nevertheless conform to the error-detail and credential-safety
rules established in Step 0.2.

Logging records failures. It does not define exception types or decide
process exit codes.

### Design

Logging configuration is read from environment variables.

The logger does not depend on the configuration loader or OmegaConf.

Supported variables are:

- `SNOMED_LOG_DIR` — log directory; defaults to `./log/`.
- `SNOMED_LOG_LEVEL` — logging verbosity; defaults to `INFO`.

If the log directory is not writable, logging falls back as documented
by the implementation and reports a warning to standard error.

The Python implementation is a thin wrapper around standard-library
`logging`.

`TimedRotatingFileHandler` rotates the log at midnight and retains
30 days of log files.

The current log filename is:

    snomed.log

The Bash implementation is a sourced library.

The shared log format is:

    YYYY-MM-DDTHH:MM:SS | LEVEL | name | message

The configuration loader can expose logging-related configuration as
shell-variable assignments for use by Bash scripts.

---

## Step 0.4 — Configuration Loader

**Status:** Complete

### Outputs

- `src/common/config_loader.py`
- `tests/test_config_loader_py.py`
- `tests/test_config_loader_r1_py.py`
- `tests/test_config_loader_r2_py.py`
- `tests/test_config_loader_r3_py.py`
- `tests/test_config_loader_r4_py.py`
- `tests/protocols/test_config_loader_py.md`

### Dependencies

The configuration loader depends on the configuration design defined
in Step 0.1.

It has no implementation dependency on the shared Python exception
hierarchy or logging utility.

### Process

1. Load `config/project.yaml` using OmegaConf.
2. Read the configured `includes` list.
3. Load included configuration files as named subtrees.
4. Resolve `active_environment`.
5. Expose active environment paths through `cfg.paths`.
6. Resolve configuration interpolation.
7. Validate mandatory configuration keys.
8. Return a resolved configuration object or produce shell-variable
   assignments.

Module mode returns the resolved OmegaConf configuration object.

CLI mode prints assignments following this pattern:

    SNOMED_<SECTION>_<KEY>=VALUE

The emitted lines are bare shell-variable assignments; the loader does
not add the shell `export` keyword. A calling script is responsible for
exporting values when they must be inherited by child processes.
List values are not emitted through the CLI interface.

### Error Behavior

Module mode exposes the documented standard Python and OmegaConf
exceptions to its caller. These include `FileNotFoundError`,
`ValueError`, and `KeyError`.

This behavior is intentional and is verified by the Step 0.4 tests
and protocol. The configuration loader does not translate these
exceptions into `SnomedConfigError`.

CLI mode reports failures to standard error and exits with
configuration exit code 1.

---

## Step 0.5 — Database Connection Module

**Status:** Complete

### Outputs

- `src/common/db_connection.py`
- `tests/test_db_connection_r1_py.py`
- `tests/test_db_connection_r2_py.py`
- `tests/test_db_connection_r3_py.py`
- `tests/test_db_connection_r4_py.py`
- `tests/test_db_connection_r5_py.py`
- `tests/test_db_connection_r6_py.py`
- `tests/test_db_connection_r7_py.py`
- `tests/test_db_connection_py.py`
- `tests/protocols/test_db_connection_py.md`

### Dependencies

The database connection module uses the configuration infrastructure
from Steps 0.1 and 0.4.

It must conform to the shared error-handling and logging designs from
Steps 0.2 and 0.3 according to its approved implementation.

### Purpose

The database connection module is implemented in Phase 0 as shared
infrastructure.

Its presence does not mean that Phase 0 provisions Oracle schemas,
creates application tables, or loads data.

Subsequent phases may use the module whenever application-level Oracle
access is required.

Privileged Oracle provisioning may use dedicated SQL scripts and
runners defined for Phase 1. This document does not require every
Oracle operation to pass through `db_connection.py`.

### Interface

- `_get_credentials(cfg, schema)` resolves schema credentials.
- `get_connection(cfg, schema)` creates a direct Oracle connection.
- `open_connection(cfg, schema)` manages connection cleanup.
- `test_connection(cfg, schema)` verifies connectivity.
- `execute_ddl(conn, sql)` executes one DDL statement.
- `execute_batch(conn, sql, data, batch_size)` executes batched DML.
- `execute_query(conn, sql, params=None)` executes a query.
- `get_pool(cfg, schema)` is an unimplemented placeholder.

Connection pooling is outside the approved Phase 0 scope.

Connections use:

    autocommit=False

The caller owns transaction commit and rollback.

### Schema Identifiers

Application schema identifiers are:

    snomed
    snomed_stage

The database connection module also recognizes:

    sys

`sys` is reserved exclusively for privileged Oracle provisioning. It
is not an application schema and must not be used by normal
application code, local bootstrap, or real-database bootstrap.

Supporting the `sys` identifier does not make SYSDBA credentials a
Phase 0 runtime prerequisite. The authoritative Phase 1 setup
procedure determines when and how privileged access is used.

### Verification

The database connection implementation, test suite, orchestrator, and
test protocol are complete.

If existing records do not establish whether real Oracle verification
was explicitly run with:

    SNOMED_TEST_REAL_DB=true

the applicable verification must be repeated during Phase 0 close-out.

Repeating that verification does not reopen the completed Step 0.5
implementation.

---

## Step 0.6 — Bootstrap Script

**Status:** In progress

### Current Outputs

- `scripts/bootstrap.sh`
- `tests/test_bootstrap_r1_sh.sh`
- `tests/test_bootstrap_r2_sh.sh`
- `tests/test_bootstrap_r3_sh.sh`
- `tests/test_bootstrap_r4_py.py`
- `tests/test_bootstrap_r_py3_sh.sh`

### Approved Outputs in Progress

- `config/required_modules.json`
- `src/common/read_required_modules.py`
- Revised or additional isolated bootstrap tests required by the
  approved behavior.
- A bootstrap verification protocol.

### Relationship to Earlier Steps

Bootstrap verifies prerequisites and outputs established by earlier
Phase 0 work.

Default bootstrap must remain capable of reporting a missing or broken
prerequisite without requiring that prerequisite to operate
successfully.

The optional real-database mode may invoke the configuration loader and
database connection module after its local prerequisites have passed.

Bootstrap therefore verifies earlier components, but it does not have
an unconditional runtime dependency on all of them.

### Purpose

Bootstrap is a shared prerequisite gate for developers and operators.

It supports:

- Local prerequisite verification without Oracle connectivity.
- Optional application-schema verification after Oracle provisioning.

Configuration profiles and bootstrap modes are separate:

    Configuration profiles: development, production
    Bootstrap modes: local, real-db

### Local Mode

Default invocation:

    bash scripts/bootstrap.sh

Local mode verifies applicable shared prerequisites, including:

- Required project configuration.
- Required project and runtime paths.
- The configured Python virtual environment.
- Required Python modules.
- A concise environment summary.

If bootstrap creates directories, creation must be restricted to
explicitly approved runtime directories.

Local mode must not require:

- Oracle connectivity.
- Existing Oracle application schemas.
- Application-schema passwords.
- SYSDBA credentials.

Local mode does not create Oracle objects.

### Python Dependency Registry

Required Python modules are defined in:

    config/required_modules.json

The approved registry maps import names to distribution names:

    oracledb  -> oracledb
    omegaconf -> omegaconf
    yaml      -> PyYAML

JSON is used because the registry must be readable before PyYAML has
been verified.

The helper:

    src/common/read_required_modules.py

must validate the registry structure and reject malformed or
incomplete input with a clear diagnostic.

Dependency checks must clearly identify available and missing modules.

Tests for missing, malformed, or invalid dependency configuration must
use isolated fixtures.

Bootstrap tests must not rename, overwrite, delete, or otherwise
modify actual repository configuration files.

### Real-Database Mode

Approved interface:

    bash scripts/bootstrap.sh --real-db

This interface is approved but is not yet confirmed as implemented.

Real-database mode is intended for use after the Phase 1 Oracle setup
procedure has created the application schemas.

It verifies connectivity to both:

    snomed
    snomed_stage

It requires the Oracle connection configuration and application-schema
credentials relevant to those checks.

It must not require SYSDBA credentials.

If either application schema has not yet been provisioned, bootstrap
must explain that the Phase 1 Oracle setup procedure must run before
real-database verification.

Real-database mode does not:

- Create profiles.
- Create tablespaces.
- Create schemas.
- Grant privileges.
- Create application tables.
- Load RF2 files.
- Modify Oracle objects.

### Environment Summary

After successful verification, bootstrap prints a concise summary
containing applicable information such as:

- Active configuration profile.
- Python version.
- Virtual-environment location.
- Log directory.
- Oracle connection identifier when real-database mode is used.

The summary must never display passwords or other credential values.

### Logging and Failure Handling

Bootstrap may report prerequisite failures directly to standard error.

This is intentional because bootstrap must be able to report failures
before the shared logging infrastructure has been verified.

Exit behavior is:

    0 — All checks requested by the selected mode passed.
    1 — One or more requested checks failed.

Diagnostics must identify the failing prerequisite without exposing
credentials.

---

## Step 0.7 — Integration and Conformance Audit

**Status:** Pending

### Dependencies

Step 0.7 begins after the approved Step 0.6 behavior has been
implemented.

It verifies all Phase 0 components together.

### Purpose

Step 0.7 verifies that Phase 0 components work together and conform to
the approved Phase 0 specification.

It is a Phase 0 integration and close-out activity. It is not the
full-pipeline testing and compliance certification assigned to
Phases 5 and 6.

### Verification Scope

Confirm that:

- Configuration resolves correctly for the supported profiles.
- Configuration profile definitions agree with
  `docs/dev_workflow.md`.
- Required Python modules agree with the dependency registry.
- Error handling and logging behave according to their approved
  contracts.
- Configuration-loader exception and CLI behavior agree with the
  verified Step 0.4 contract.
- Database connection tests and their protocol are present and pass.
- Default bootstrap works without Oracle credentials or connectivity.
- Real-database bootstrap checks both application schemas when run in
  an appropriately provisioned environment.
- Bootstrap never requires SYSDBA credentials.
- Bootstrap tests preserve actual repository configuration.
- Phase 0 documentation agrees with the approved implementation.
- Phase 0 and the project roadmap agree on the boundary between shared
  infrastructure and Phase 1 provisioning.

Where real Oracle verification is required, it must use OCI or another
explicitly approved Oracle environment.

### Test Execution and Evidence

Existing test protocols describe how their corresponding tests are
performed. A protocol is not, by itself, evidence of a particular test
execution.

Step 0.7 reruns the approved test orchestrators or complete test
commands to detect regressions and provide current close-out evidence.

Completed development rounds do not need to be repeated individually
unless a failing test requires diagnosis.

The form and location of the final Phase 0 test record must be agreed
before Phase 0 is declared complete.

---

## Phase 0 Exit Criteria

Phase 0 is complete when:

1. Required outputs of Steps 0.1 through 0.5 are present.

2. Step 0.6 implements the approved local bootstrap behavior.

3. Step 0.6 implements the approved `--real-db` behavior.

4. The dependency registry and its helper reject invalid input and
   report missing dependencies correctly.

5. Bootstrap tests use isolated fixtures and preserve repository
   configuration.

6. Step 0.7 integration and conformance verification passes.

7. Real Oracle verification is supported by current evidence,
   including explicit use of `SNOMED_TEST_REAL_DB=true` where
   applicable.

8. Phase 0 documentation matches the approved implementation.

9. `docs/phase0_foundation.md` and `docs/road_map.md` agree on the
   boundary between Phase 0 infrastructure and Phase 1 Oracle
   provisioning.

10. Remaining discrepancies are corrected within the approved scope
    or explicitly documented and accepted.

11. Jan approves Phase 0 completion.

---

## Runtime Order on a Fresh Installation

The intended runtime order is:

1. Verify local prerequisites:

       bash scripts/bootstrap.sh

2. Run the approved Phase 1 Oracle setup procedure.

3. Verify the provisioned application schemas:

       bash scripts/bootstrap.sh --real-db

4. Run the approved Phase 1 RF2 ingestion procedure.

The authoritative Phase 1 setup command must be determined from the
existing setup scripts and documentation before it is specified.

Privileged SYSDBA access belongs to the Phase 1 Oracle setup procedure,
not to bootstrap.

Development phase numbering and runtime command order are related but
are not identical.

No unified top-level orchestrator is introduced in Phase 0 without
separate approval.

---

## Dependencies and Runtime Configuration

### Required Python Distributions

- `oracledb`
- `omegaconf`
- `PyYAML`

The dependency registry maps these distribution names to their Python
import names.

### Logging Configuration

- `SNOMED_LOG_DIR` — optional; defaults to `./log/`.
- `SNOMED_LOG_LEVEL` — optional; defaults to `INFO`.

### Oracle Application Credentials

Used only when an Oracle operation requires them:

- `SNOMED_DB_PASSWORD`
- `SNOMED_STAGE_DB_PASSWORD`

Additional Oracle connectivity configuration, including `TNS_ADMIN`
where applicable, is checked by real-database mode or the relevant
Phase 1 procedure.

### Privileged Oracle Credentials

Privileged credentials are required only by the approved Phase 1
Oracle setup procedure.

Existing privileged credential-name inconsistencies must be recorded
and resolved separately.

SYSDBA credentials are not Phase 0 bootstrap prerequisites.

### Third-Party Service Credentials

Third-party API keys are not universal Phase 0 prerequisites unless an
approved Phase 0 component explicitly requires them.

---

## Excluded Phase 0 Work

Unless a scope change is separately approved, Phase 0 does not include:

- RF2 ingestion features.
- New Oracle provisioning implementation.
- Application table-definition implementation.
- Environment-variable YAML migration.
- A new top-level orchestrator.
- Connection-pool implementation.
- Unrelated refactoring.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT), which is
used by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
