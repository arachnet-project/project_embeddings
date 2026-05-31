# ARC_FILE: docs/todo_step_0_5.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — Step 0.5 Todo
# Version: 1.2
# Created: 2026-05-10
# Updated: 2026-05-22
# ============================================================
#
# Revision policy: review and update at the start of every
# working session and after every commit.
# ============================================================

## Purpose

Implement src/common/db_connection.py — the sole Oracle communication
module. No other module imports oracledb directly.

Note: this file was previously named todo_step_0_6.md due to a step
numbering error. Correct number is 0.5 per phase0_foundation.md.


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
Must update ~/.bashrc on OCI and Mac (Ubuntu done).

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

### execute_query return type (decided 2026-05-21)
Returns list[tuple] — simpler, consistent with oracledb defaults.
Used only for validation (row counts, data checks), not application logic.

### test_connection return type (decided 2026-05-22)
Returns None on success. Raises on any failure.
Never returns False — failures always raise.

### execute_batch return type (decided 2026-05-22)
Returns int — total rows submitted across all batches.
Does NOT commit. Caller owns commit/rollback.

### No connection pool in Phase 1
get_pool() is a stub that raises NotImplementedError.
Pooling deferred to Phase 3/4.

### Ingestion strategy (decided 2026-05-22)
execute_batch is retained. RF2 ingestion will go via Parquet as
intermediate format (Oracle authoritative, Parquet for Phase 3 ML).
Even in that path, Python pushes data from Parquet into Oracle via
executemany — execute_batch is the controlled primitive for that push.


## Functions to implement (in order)

- [x] _get_credentials(cfg, schema) -> tuple
      Done 2026-05-10. Round 1 tests: 10/10 Ubuntu + OCI.

- [x] get_connection(cfg, schema) -> oracledb.Connection
      Done 2026-05-18. Round 2 tests: 10/10 Ubuntu + OCI (v1.1).
      Direct connection, thin mode, autocommit=False.
      Adds AUTH_MODE_SYSDBA when schema == "sys".
      Retries once on failure.

- [x] open_connection(cfg, schema) -> Generator[oracledb.Connection]
      Done 2026-05-22. Round 3 tests: 9/9 Ubuntu.
      @contextmanager wrapper around get_connection.
      Closes connection on exit even on exception.

- [x] test_connection(cfg, schema) -> None
      Done 2026-05-22. Round 4 tests: 9/9 Ubuntu.
      Executes SELECT 1 FROM DUAL.
      Returns None on success. Raises on failure.
      Used by bootstrap script.

- [x] execute_ddl(conn, sql) -> None
      Done 2026-05-22. Round 5 tests: 10/10 Ubuntu.
      Single DDL statement. Logs truncated to _DDL_LOG_MAX_LENGTH.
      Raises SnomedDDLError on failure.
      Cursor closed in finally.

- [x] execute_batch(conn, sql, data, batch_size) -> int
      Done 2026-05-22. Round 6 tests written, not yet run.
      Bulk INSERT via executemany in batches of batch_size.
      Returns total rows submitted.
      Does NOT commit. Raises SnomedLoadError on failure.
      Cursor closed in finally.

- [ ] execute_query(conn, sql, params=None) -> list[tuple]
      SELECT query. Returns list of tuples.
      Used for validation — row counts, data checks.
      Raises SnomedDBConnectionError on failure.

- [ ] get_pool(cfg, schema) -> raises NotImplementedError
      Stub. Pooling deferred to Phase 3/4.


## Files to create/update

- [x] src/common/db_connection.py v1.4 — through execute_batch
- [ ] src/common/db_connection.py — execute_query + get_pool remaining
- [ ] tests/test_db_connection_r6_py.py — Round 6 written, not yet run
- [ ] tests/test_db_connection_r7_py.py — Round 7: execute_query
- [ ] tests/test_db_connection_py.py — orchestrator (after all rounds pass)
- [ ] tests/protocols/test_db_connection_py.md — test protocol
- [x] config/database.yaml — updated to v1.4 (schema key rename)
- [x] src/common/config_loader.py — MANDATORY_KEYS updated
- [ ] ~/.bashrc on OCI and Mac — rename SNOMED_ADMIN_DB_PASSWORD
      to SNOMED_SYS_DB_PASSWORD (Ubuntu done)


## Testing rounds

### Round 1 — _get_credentials (mocked)
tests/test_db_connection_r1_py.py
10/10 Ubuntu, 10/10 OCI. Committed.

### Round 2 — get_connection (mocked)
tests/test_db_connection_r2_py.py v1.1
10/10 Ubuntu, 10/10 OCI. Committed as 9650b88.

### Round 3 — open_connection (mocked)
tests/test_db_connection_r3_py.py
9/9 Ubuntu. OCI pending.

### Round 4 — test_connection (mocked)
tests/test_db_connection_r4_py.py
9/9 Ubuntu. OCI pending.

### Round 5 — execute_ddl (mocked)
tests/test_db_connection_r5_py.py
10/10 Ubuntu. OCI pending.

### Round 6 — execute_batch (mocked)
tests/test_db_connection_r6_py.py
Written 2026-05-22. Not yet run.

### Round 7 — execute_query (mocked)
Pending — to be written after Round 6 passes.


## Testing strategy (remaining)

### Ubuntu (mocked — no OCI needed)
Use unittest.mock to mock oracledb.connect.
Test execute_query, get_pool, orchestrator.

### OCI (real DB)
Set SNOMED_TEST_REAL_DB=true before running tests.
Tests connect to real snomed and snomed_stage schemas.
Verify test_connection, execute_ddl, execute_batch end-to-end.


## Blocking dependencies

None. Can be developed entirely on Ubuntu with mocked tests.
OCI schemas snomed and snomed_stage are in place (created 2026-05-09).
