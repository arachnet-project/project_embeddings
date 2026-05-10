# docs/todo_step_0_6.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — Step 0.6 Todo
# Version: 1.0
# Created: 2026-05-10
# ============================================================

## Purpose

Implement src/common/db_connection.py — the sole Oracle communication
module. No other module imports oracledb directly.


## Design decisions (agreed 2026-05-10)

### Schema naming
Schema names in code match Oracle usernames exactly. No mapping layer.
    snomed       — production schema
    snomed_stage — stage schema
    sys          — SYSDBA, setup only

### database.yaml changes (v1.4)
Keys renamed from production_schema/stage_schema/admin to
snomed/snomed_stage/sys. Oracle usernames are the single source of truth.

### Environment variables
    SNOMED_DB_PASSWORD          — snomed schema password
    SNOMED_STAGE_DB_PASSWORD    — snomed_stage schema password
    SNOMED_SYS_DB_PASSWORD      — sys (SYSDBA) password
Note: SNOMED_ADMIN_DB_PASSWORD renamed to SNOMED_SYS_DB_PASSWORD.
Must update ~/.bashrc on all three machines.

### SYSDBA connection
When schema == "sys", db_connection.py adds:
    mode=oracledb.AUTH_MODE_SYSDBA
to the oracledb.connect() call. Callers do not need to know this.

### Transaction ownership
The caller owns commit/rollback. execute_batch() does NOT commit.
execute_ddl() does not need commit (DDL implicitly commits in Oracle).

### Connection retry
get_connection() retries once after _RETRY_WAIT_SECONDS on failure.
Raises SnomedDBConnectionError after two failures.

### No connection pool in Phase 1
get_pool() is a stub that raises NotImplementedError.
Pooling deferred to Phase 3/4.


## Functions to implement (in order)

- [x] _get_credentials(cfg, schema) -> tuple
      Done 2026-05-10. Returns (username, password, tns_alias).

- [ ] get_connection(cfg, schema) -> oracledb.Connection
      Direct connection, thin mode, autocommit=False.
      Adds AUTH_MODE_SYSDBA when schema == "sys".
      Retries once on failure.

- [ ] open_connection(cfg, schema) -> context manager
      Wraps get_connection. Closes connection on exit even on exception.
      No commit on exception — caller handles.
      Implemented with @contextmanager decorator.

- [ ] execute_ddl(conn, sql) -> None
      Single DDL statement. Logs SQL at DEBUG truncated to
      _DDL_LOG_MAX_LENGTH. Raises SnomedDDLError on failure.

- [ ] execute_batch(conn, sql, data, batch_size) -> tuple
      Bulk INSERT via executemany in batches of batch_size.
      Returns (rows_loaded, batches_processed).
      Does NOT commit. Rolls back and raises SnomedLoadError on failure.

- [ ] execute_query(conn, sql, params=None) -> list
      SELECT query. Returns list of tuples.
      Used for validation — row counts, data checks.
      Raises SnomedDBConnectionError on failure.

- [ ] test_connection(cfg, schema="snomed") -> True
      Executes SELECT 1 FROM DUAL.
      Returns True on success.
      Raises SnomedDBConnectionError on failure — never returns False.

- [ ] get_pool(cfg, schema) -> raises NotImplementedError
      Stub. Pooling deferred to Phase 3/4.


## Files to create/update

- [ ] src/common/db_connection.py — implement all functions above
- [ ] tests/test_db_connection_py.py — plain _report/_summarise pattern
- [ ] tests/protocols/test_db_connection_py.md — test protocol
- [x] config/database.yaml — updated to v1.4 (schema key rename)
- [x] src/common/config_loader.py — MANDATORY_KEYS updated
- [ ] ~/.bashrc on Ubuntu, OCI, Mac — rename SNOMED_ADMIN_DB_PASSWORD
      to SNOMED_SYS_DB_PASSWORD


## Testing strategy

### Ubuntu (mocked — no OCI needed)
Use unittest.mock to mock oracledb.connect.
Test _get_credentials, error paths, retry logic, context manager.
Run: bash scripts/run_tests.sh

### OCI (real DB)
Set SNOMED_TEST_REAL_DB=true before running tests.
Tests connect to real snomed and snomed_stage schemas.
Verify test_connection, execute_ddl, execute_batch end-to-end.


## Blocking dependencies

None. Can be developed entirely on Ubuntu with mocked tests.
OCI schemas snomed and snomed_stage are in place (created 2026-05-09).


## Open questions

- execute_query: should it return list of tuples or list of dicts?
  Tuples are simpler and consistent with oracledb defaults.
  Dicts are more readable in calling code. Decide before implementing.
