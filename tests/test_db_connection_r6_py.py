# ARC_FILE: tests/test_db_connection_r6_py.py
# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 6
# tests/test_db_connection_r6_py.py
# =============================================================================
# Purpose:
#   Round 6 tests for execute_batch() in src/common/db_connection.py.
#   Tests successful batch execution, row counting, batching logic,
#   cursor lifecycle, and input validation.
#   Uses mocked connection and cursor — no Oracle connection needed.
#   Runs on OCI or Ubuntu.
#
# Run with:
#   python tests/test_db_connection_r6_py.py
#
# Preconditions:
#   venv active with oracledb and omegaconf installed.
#   src/common/db_connection.py present.
#   src/common/exceptions.py present.
#   SNOMED_LOG_DIR set in environment.
#
# Author: Jan Mura
# Version: 1.0
# =============================================================================

import sys
from pathlib import Path
from unittest.mock import MagicMock, call

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import oracledb
from src.common.db_connection import execute_batch
from src.common.exceptions import SnomedLoadError

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_results = []


# --- _report ---
def _report(test_name: str, result: str, detail: str = "") -> None:
    """Print and record a single test result.

    Parameters
    ----------
    test_name : str
        Short descriptive name for the test case.
    result : str
        _PASS or _FAIL.
    detail : str
        Optional explanation, required on failure.
    """
    if detail:
        line = "{}: {} -- {}".format(result, test_name, detail)
    else:
        line = "{}: {}".format(result, test_name)
    print(line)
    _results.append((result, test_name))
# --- end _report ---


# --- _summarise ---
def _summarise() -> int:
    """Print pass and fail counts and return exit code.

    Returns
    -------
    int
        0 if all tests passed, 1 if any test failed.
    """
    total = len(_results)
    failed = sum(1 for r, _ in _results if r == _FAIL)
    passed = total - failed
    print("")
    print("Results: {} passed, {} failed, {} total.".format(
        passed, failed, total))
    return 0 if failed == 0 else 1
# --- end _summarise ---


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_conn():
    """Build a mock connection with a trackable cursor."""
    cursor = MagicMock()
    cursor.executemany = MagicMock()
    cursor.close = MagicMock()
    conn = MagicMock()
    conn.cursor = MagicMock(return_value=cursor)
    return conn, cursor


_SQL = "INSERT INTO sct_concept (id, effective_time, active) VALUES (:1, :2, :3)"
_ROW = (100000001, "20230901", 1)


# =============================================================================
# Round 6 -- execute_batch happy paths
# =============================================================================

# --- test_execute_batch_returns_total_rows ---
def test_execute_batch_returns_total_rows():
    """execute_batch returns the total number of rows submitted."""
    conn, _ = _make_mock_conn()
    data = [_ROW] * 10
    try:
        result = execute_batch(conn, _SQL, data, batch_size=5)
        if result != 10:
            _report("execute_batch: returns total rows",
                    _FAIL, "returned {} expected 10".format(result))
            return
        _report("execute_batch: returns total rows", _PASS)
    except Exception as exc:
        _report("execute_batch: returns total rows",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_returns_total_rows ---


# --- test_execute_batch_calls_executemany_correct_times ---
def test_execute_batch_calls_executemany_correct_times():
    """execute_batch calls executemany once per batch."""
    conn, cursor = _make_mock_conn()
    data = [_ROW] * 10
    try:
        execute_batch(conn, _SQL, data, batch_size=5)
        if cursor.executemany.call_count != 2:
            _report("execute_batch: calls executemany correct times",
                    _FAIL, "call_count={} expected 2".format(
                        cursor.executemany.call_count))
            return
        _report("execute_batch: calls executemany correct times", _PASS)
    except Exception as exc:
        _report("execute_batch: calls executemany correct times",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_calls_executemany_correct_times ---


# --- test_execute_batch_correct_batch_contents ---
def test_execute_batch_correct_batch_contents():
    """execute_batch passes correctly sliced batches to executemany."""
    conn, cursor = _make_mock_conn()
    data = [(i,) for i in range(7)]
    try:
        execute_batch(conn, _SQL, data, batch_size=3)
        calls = cursor.executemany.call_args_list
        # Expected: batch 0-2, batch 3-5, batch 6
        expected = [
            call(_SQL, [(0,), (1,), (2,)]),
            call(_SQL, [(3,), (4,), (5,)]),
            call(_SQL, [(6,)]),
        ]
        if calls != expected:
            _report("execute_batch: correct batch contents",
                    _FAIL, "calls={} expected={}".format(calls, expected))
            return
        _report("execute_batch: correct batch contents", _PASS)
    except Exception as exc:
        _report("execute_batch: correct batch contents",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_correct_batch_contents ---


# --- test_execute_batch_single_batch_when_data_smaller_than_batch_size ---
def test_execute_batch_single_batch_when_data_smaller_than_batch_size():
    """execute_batch calls executemany once when data fits in one batch."""
    conn, cursor = _make_mock_conn()
    data = [_ROW] * 3
    try:
        execute_batch(conn, _SQL, data, batch_size=100)
        if cursor.executemany.call_count != 1:
            _report(
                "execute_batch: single batch when data smaller than batch_size",
                _FAIL, "call_count={} expected 1".format(
                    cursor.executemany.call_count))
            return
        _report(
            "execute_batch: single batch when data smaller than batch_size",
            _PASS)
    except Exception as exc:
        _report(
            "execute_batch: single batch when data smaller than batch_size",
            _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_single_batch_when_data_smaller_than_batch_size ---


# --- test_execute_batch_closes_cursor_on_success ---
def test_execute_batch_closes_cursor_on_success():
    """execute_batch closes the cursor after successful execution."""
    conn, cursor = _make_mock_conn()
    data = [_ROW] * 5
    try:
        execute_batch(conn, _SQL, data, batch_size=5)
        if not cursor.close.called:
            _report("execute_batch: closes cursor on success",
                    _FAIL, "cursor.close was not called")
            return
        _report("execute_batch: closes cursor on success", _PASS)
    except Exception as exc:
        _report("execute_batch: closes cursor on success",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_closes_cursor_on_success ---


# =============================================================================
# Round 6 -- execute_batch failure paths
# =============================================================================

# --- test_execute_batch_wraps_database_error ---
def test_execute_batch_wraps_database_error():
    """execute_batch wraps oracledb.DatabaseError in SnomedLoadError."""
    conn, cursor = _make_mock_conn()
    cursor.executemany.side_effect = oracledb.DatabaseError("ORA-00001")
    raised = False
    try:
        try:
            execute_batch(conn, _SQL, [_ROW], batch_size=1)
        except SnomedLoadError:
            raised = True
        if not raised:
            _report("execute_batch: wraps DatabaseError in SnomedLoadError",
                    _FAIL, "SnomedLoadError was not raised")
            return
        _report("execute_batch: wraps DatabaseError in SnomedLoadError", _PASS)
    except Exception as exc:
        _report("execute_batch: wraps DatabaseError in SnomedLoadError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_wraps_database_error ---


# --- test_execute_batch_closes_cursor_on_failure ---
def test_execute_batch_closes_cursor_on_failure():
    """execute_batch closes the cursor even when executemany raises."""
    conn, cursor = _make_mock_conn()
    cursor.executemany.side_effect = oracledb.DatabaseError("ORA-00001")
    try:
        try:
            execute_batch(conn, _SQL, [_ROW], batch_size=1)
        except SnomedLoadError:
            pass
        if not cursor.close.called:
            _report("execute_batch: closes cursor on failure",
                    _FAIL, "cursor.close was not called")
            return
        _report("execute_batch: closes cursor on failure", _PASS)
    except Exception as exc:
        _report("execute_batch: closes cursor on failure",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_closes_cursor_on_failure ---


# --- test_execute_batch_empty_data_raises ---
def test_execute_batch_empty_data_raises():
    """execute_batch raises SnomedLoadError when data is an empty list."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_batch(conn, _SQL, [], batch_size=100)
        except SnomedLoadError:
            raised = True
        if not raised:
            _report("execute_batch: empty data raises SnomedLoadError",
                    _FAIL, "SnomedLoadError was not raised")
            return
        _report("execute_batch: empty data raises SnomedLoadError", _PASS)
    except Exception as exc:
        _report("execute_batch: empty data raises SnomedLoadError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_empty_data_raises ---


# --- test_execute_batch_invalid_batch_size_raises ---
def test_execute_batch_invalid_batch_size_raises():
    """execute_batch raises SnomedLoadError when batch_size is zero or negative."""
    conn, _ = _make_mock_conn()
    for bad_size in (0, -1, -100):
        raised = False
        try:
            try:
                execute_batch(conn, _SQL, [_ROW], batch_size=bad_size)
            except SnomedLoadError:
                raised = True
            if not raised:
                _report(
                    "execute_batch: invalid batch_size raises SnomedLoadError",
                    _FAIL,
                    "SnomedLoadError not raised for batch_size={}".format(
                        bad_size))
                return
        except Exception as exc:
            _report(
                "execute_batch: invalid batch_size raises SnomedLoadError",
                _FAIL, "raised: {}".format(exc))
            return
    _report("execute_batch: invalid batch_size raises SnomedLoadError", _PASS)
# --- end test_execute_batch_invalid_batch_size_raises ---


# --- test_execute_batch_non_string_sql_raises ---
def test_execute_batch_non_string_sql_raises():
    """execute_batch raises SnomedLoadError when sql is not a string."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_batch(conn, 42, [_ROW], batch_size=1)
        except SnomedLoadError:
            raised = True
        if not raised:
            _report("execute_batch: non-string sql raises SnomedLoadError",
                    _FAIL, "SnomedLoadError was not raised")
            return
        _report("execute_batch: non-string sql raises SnomedLoadError", _PASS)
    except Exception as exc:
        _report("execute_batch: non-string sql raises SnomedLoadError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_batch_non_string_sql_raises ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 6 test functions and print a summary."""
    print("=== test_db_connection_r6_py.py -- Round 6 ===")
    print("")

    print("-- execute_batch: happy paths --")
    test_execute_batch_returns_total_rows()
    test_execute_batch_calls_executemany_correct_times()
    test_execute_batch_correct_batch_contents()
    test_execute_batch_single_batch_when_data_smaller_than_batch_size()
    test_execute_batch_closes_cursor_on_success()
    print("")

    print("-- execute_batch: failure paths --")
    test_execute_batch_wraps_database_error()
    test_execute_batch_closes_cursor_on_failure()
    test_execute_batch_empty_data_raises()
    test_execute_batch_invalid_batch_size_raises()
    test_execute_batch_non_string_sql_raises()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
