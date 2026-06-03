# ARC_FILE: tests/protocols/test_db_connection_py.md
# Test Protocol — db_connection.py
# tests/protocols/test_db_connection_py.md
# ============================================================
# Version: 1.0
# Created: 2026-06-01
# ============================================================

## Purpose

Records what was tested, how, and the results for
src/common/db_connection.py — Step 0.5 of Phase 0.

## Module under test

src/common/db_connection.py v1.6

## Test strategy

All rounds use mocked Oracle connections (unittest.mock).
No real Oracle connection is required for rounds 1–7.
Real DB validation is deferred to Phase 1 integration testing.

Two platforms: Ubuntu (development), OCI Frankfurt (Oracle Linux 9).

## Test files

| File                              | Scope               | Tests |
|-----------------------------------|---------------------|-------|
| test_db_connection_r1_py.py       | _get_credentials    | 10    |
| test_db_connection_r2_py.py       | get_connection      | 10    |
| test_db_connection_r3_py.py       | open_connection     | 9     |
| test_db_connection_r4_py.py       | test_connection     | 9     |
| test_db_connection_r5_py.py       | execute_ddl         | 11    |
| test_db_connection_r6_py.py       | execute_batch       | 10    |
| test_db_connection_r7_py.py       | execute_query       | 12    |
| test_db_connection_py.py          | orchestrator        | 8 rounds + inline |

## Results

### Ubuntu

| Round    | Scope            | Result | Date       |
|----------|------------------|--------|------------|
| Round 1  | _get_credentials | 10/10  | 2026-05-10 |
| Round 2  | get_connection   | 10/10  | 2026-05-18 |
| Round 3  | open_connection  | 9/9    | 2026-05-22 |
| Round 4  | test_connection  | 9/9    | 2026-05-22 |
| Round 5  | execute_ddl      | 11/11  | 2026-05-22 |
| Round 6  | execute_batch    | 10/10  | 2026-05-29 |
| Round 7  | execute_query    | 12/12  | 2026-06-01 |
| Orch.    | all rounds       | 8/8    | 2026-06-01 |

### OCI Frankfurt (Oracle Linux 9)

| Round    | Scope            | Result | Date       |
|----------|------------------|--------|------------|
| Round 1  | _get_credentials | 10/10  | 2026-05-10 |
| Round 2  | get_connection   | 10/10  | 2026-05-18 |
| Round 3  | open_connection  | 9/9    | 2026-05-22 |
| Round 4  | test_connection  | 9/9    | 2026-05-22 |
| Round 5  | execute_ddl      | 11/11  | 2026-05-22 |
| Round 6  | execute_batch    | 10/10  | 2026-05-29 |
| Round 7  | execute_query    | 12/12  | 2026-06-01 |
| Orch.    | all rounds       | 8/8    | 2026-06-01 |

## Coverage summary

### Functions tested

| Function          | Happy paths | Failure paths | Total |
|-------------------|-------------|---------------|-------|
| _get_credentials  | 4           | 6             | 10    |
| get_connection    | 5           | 5             | 10    |
| open_connection   | 3           | 6             | 9     |
| test_connection   | 4           | 5             | 9     |
| execute_ddl       | 4           | 7             | 11    |
| execute_batch     | 5           | 5             | 10    |
| execute_query     | 6           | 6             | 12    |
| get_pool          | 0           | 1             | 1     |
| **Total**         | **31**      | **41**        | **72**|

### Key behaviours verified

- Credentials never logged or stored beyond resolution
- Invalid schema rejected before any connection attempt
- Connection retried once on failure, raises after two failures
- SYSDBA mode applied for sys schema only
- Connection always closed on exit from open_connection
- Connection closed even when exception raised in with block
- test_connection returns None on success, raises on failure
- execute_ddl rejects non-DDL statements (keyword guard)
- execute_ddl cursor closed in finally on success and failure
- execute_batch splits data correctly across batches
- execute_batch returns total rows submitted
- execute_query rejects non-SELECT statements (keyword guard)
- execute_query returns empty list when no rows found
- execute_query cursor closed in finally on success and failure
- get_pool raises NotImplementedError unconditionally

## Known limitations

- All tests are mocked. Real Oracle behaviour not verified in this phase.
- WITH (CTE) queries not supported by execute_query keyword guard.
  Rewrite as inline subqueries if needed.
- Connection pool not implemented. get_pool deferred to Phase 3/4.

## Closing commit

feat: Step 0.5 complete — db_connection.py all functions tested
