# ARC_FILE: tests/test_db_connection_r7_py.py
# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 7
# tests/test_db_connection_r7_py.py
# =============================================================================
# Purpose:
#   Round 7 tests for execute_query() in src/common/db_connection.py.
#   Tests successful execution, return values, params handling,
#   cursor lifecycle, and input validation.
#   Uses mocked connection and cursor — no Oracle connection needed.
#   Runs on OCI or Ubuntu.
#
# Run with:
#   python tests/test_db_connection_r7_py.py
#
# Preconditions:
#   venv active with oracledb and omegaconf installed.
#   src/common/db_connection.py present.
#   src/common/exceptions.py present.
#   SNOMED_LOG_DIR set in environment.
#
# Author: Jan Mura
# Version: 1.1
# =============================================================================

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import oracledb
from src.common.db_connection import execute_query
from src.common.exceptions import SnomedDBConnectionError

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

def _make_mock_conn(rows=None):
    """Build a mock connection with a cursor returning given rows.

    Parameters
    ----------
    rows : list or None
        Rows fetchall() will return. Defaults to [(1,)].
    """
    if rows is None:
        rows = [(1,)]
    cursor = MagicMock()
    cursor.execute = MagicMock()
    cursor.fetchall = MagicMock(return_value=rows)
    cursor.close = MagicMock()
    conn = MagicMock()
    conn.cursor = MagicMock(return_value=cursor)
    return conn, cursor


_SQL = "SELECT id FROM sct_concept WHERE active = :1"


# =============================================================================
# Round 7 -- execute_query happy paths
# =============================================================================

# --- test_execute_query_returns_list_of_tuples ---
def test_execute_query_returns_list_of_tuples():
    """execute_query returns a list of tuples on success."""
    rows = [(1,), (2,), (3,)]
    conn, _ = _make_mock_conn(rows=rows)
    try:
        result = execute_query(conn, _SQL)
        if not isinstance(result, list):
            _report("execute_query: returns list of tuples",
                    _FAIL, "result type={!r}".format(type(result).__name__))
            return
        if result != rows:
            _report("execute_query: returns list of tuples",
                    _FAIL, "result={!r} expected={!r}".format(result, rows))
            return
        _report("execute_query: returns list of tuples", _PASS)
    except Exception as exc:
        _report("execute_query: returns list of tuples",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_returns_list_of_tuples ---


# --- test_execute_query_returns_empty_list_when_no_rows ---
def test_execute_query_returns_empty_list_when_no_rows():
    """execute_query returns an empty list when the query finds no rows."""
    conn, _ = _make_mock_conn(rows=[])
    try:
        result = execute_query(conn, _SQL)
        if result != []:
            _report("execute_query: returns empty list when no rows",
                    _FAIL, "result={!r}".format(result))
            return
        _report("execute_query: returns empty list when no rows", _PASS)
    except Exception as exc:
        _report("execute_query: returns empty list when no rows",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_returns_empty_list_when_no_rows ---


# --- test_execute_query_calls_execute_with_params ---
def test_execute_query_calls_execute_with_params():
    """execute_query passes params to cursor.execute when provided."""
    conn, cursor = _make_mock_conn()
    params = [1]
    try:
        execute_query(conn, _SQL, params=params)
        call_args = cursor.execute.call_args
        if call_args[0][0] != _SQL:
            _report("execute_query: calls execute with params",
                    _FAIL, "sql mismatch")
            return
        if len(call_args[0]) < 2 or call_args[0][1] != params:
            _report("execute_query: calls execute with params",
                    _FAIL, "params not passed: call_args={}".format(call_args))
            return
        _report("execute_query: calls execute with params", _PASS)
    except Exception as exc:
        _report("execute_query: calls execute with params",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_calls_execute_with_params ---


# --- test_execute_query_calls_execute_without_params_when_none ---
def test_execute_query_calls_execute_without_params_when_none():
    """execute_query calls cursor.execute without params when params=None."""
    conn, cursor = _make_mock_conn()
    try:
        execute_query(conn, _SQL, params=None)
        call_args = cursor.execute.call_args
        if len(call_args[0]) != 1:
            _report(
                "execute_query: calls execute without params when None",
                _FAIL,
                "expected 1 positional arg got {}".format(len(call_args[0])))
            return
        _report("execute_query: calls execute without params when None", _PASS)
    except Exception as exc:
        _report("execute_query: calls execute without params when None",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_calls_execute_without_params_when_none ---


# --- test_execute_query_calls_execute_without_params_when_empty_list ---
def test_execute_query_calls_execute_without_params_when_empty_list():
    """execute_query calls cursor.execute without params when params=[]."""
    conn, cursor = _make_mock_conn()
    try:
        execute_query(conn, _SQL, params=[])
        call_args = cursor.execute.call_args
        if len(call_args[0]) != 1:
            _report(
                "execute_query: calls execute without params when empty list",
                _FAIL,
                "expected 1 positional arg got {}".format(len(call_args[0])))
            return
        _report(
            "execute_query: calls execute without params when empty list",
            _PASS)
    except Exception as exc:
        _report(
            "execute_query: calls execute without params when empty list",
            _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_calls_execute_without_params_when_empty_list ---


# --- test_execute_query_closes_cursor_on_success ---
def test_execute_query_closes_cursor_on_success():
    """execute_query closes the cursor after successful execution."""
    conn, cursor = _make_mock_conn()
    try:
        execute_query(conn, _SQL)
        if not cursor.close.called:
            _report("execute_query: closes cursor on success",
                    _FAIL, "cursor.close was not called")
            return
        _report("execute_query: closes cursor on success", _PASS)
    except Exception as exc:
        _report("execute_query: closes cursor on success",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_closes_cursor_on_success ---


# =============================================================================
# Round 7 -- execute_query failure paths
# =============================================================================

# --- test_execute_query_wraps_database_error ---
def test_execute_query_wraps_database_error():
    """execute_query wraps oracledb.DatabaseError in SnomedDBConnectionError."""
    conn, cursor = _make_mock_conn()
    cursor.execute.side_effect = oracledb.DatabaseError("ORA-00942")
    raised = False
    try:
        try:
            execute_query(conn, _SQL)
        except SnomedDBConnectionError:
            raised = True
        if not raised:
            _report(
                "execute_query: wraps DatabaseError in SnomedDBConnectionError",
                _FAIL, "SnomedDBConnectionError was not raised")
            return
        _report(
            "execute_query: wraps DatabaseError in SnomedDBConnectionError",
            _PASS)
    except Exception as exc:
        _report(
            "execute_query: wraps DatabaseError in SnomedDBConnectionError",
            _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_wraps_database_error ---


# --- test_execute_query_closes_cursor_on_failure ---
def test_execute_query_closes_cursor_on_failure():
    """execute_query closes the cursor even when execution raises."""
    conn, cursor = _make_mock_conn()
    cursor.execute.side_effect = oracledb.DatabaseError("ORA-00942")
    try:
        try:
            execute_query(conn, _SQL)
        except SnomedDBConnectionError:
            pass
        if not cursor.close.called:
            _report("execute_query: closes cursor on failure",
                    _FAIL, "cursor.close was not called")
            return
        _report("execute_query: closes cursor on failure", _PASS)
    except Exception as exc:
        _report("execute_query: closes cursor on failure",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_closes_cursor_on_failure ---


# --- test_execute_query_empty_sql_raises ---
def test_execute_query_empty_sql_raises():
    """execute_query raises SnomedDBConnectionError when sql is empty."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_query(conn, "")
        except SnomedDBConnectionError:
            raised = True
        if not raised:
            _report("execute_query: empty sql raises SnomedDBConnectionError",
                    _FAIL, "SnomedDBConnectionError was not raised")
            return
        _report("execute_query: empty sql raises SnomedDBConnectionError",
                _PASS)
    except Exception as exc:
        _report("execute_query: empty sql raises SnomedDBConnectionError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_empty_sql_raises ---


# --- test_execute_query_non_string_sql_raises ---
def test_execute_query_non_string_sql_raises():
    """execute_query raises SnomedDBConnectionError when sql is not a string."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_query(conn, 42)
        except SnomedDBConnectionError:
            raised = True
        if not raised:
            _report(
                "execute_query: non-string sql raises SnomedDBConnectionError",
                _FAIL, "SnomedDBConnectionError was not raised")
            return
        _report(
            "execute_query: non-string sql raises SnomedDBConnectionError",
            _PASS)
    except Exception as exc:
        _report(
            "execute_query: non-string sql raises SnomedDBConnectionError",
            _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_non_string_sql_raises ---


# --- test_execute_query_non_list_params_raises ---
def test_execute_query_non_list_params_raises():
    """execute_query raises SnomedDBConnectionError when params is not a list."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_query(conn, _SQL, params="bad")
        except SnomedDBConnectionError:
            raised = True
        if not raised:
            _report(
                "execute_query: non-list params raises SnomedDBConnectionError",
                _FAIL, "SnomedDBConnectionError was not raised")
            return
        _report(
            "execute_query: non-list params raises SnomedDBConnectionError",
            _PASS)
    except Exception as exc:
        _report(
            "execute_query: non-list params raises SnomedDBConnectionError",
            _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_non_list_params_raises ---


# --- test_execute_query_non_select_statement_raises ---
def test_execute_query_non_select_statement_raises():
    """execute_query raises SnomedDBConnectionError when sql is not a SELECT."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_query(conn, "INSERT INTO sct_concept VALUES (1)")
        except SnomedDBConnectionError:
            raised = True
        if not raised:
            _report(
                "execute_query: non-SELECT statement raises SnomedDBConnectionError",
                _FAIL, "SnomedDBConnectionError was not raised")
            return
        _report(
            "execute_query: non-SELECT statement raises SnomedDBConnectionError",
            _PASS)
    except Exception as exc:
        _report(
            "execute_query: non-SELECT statement raises SnomedDBConnectionError",
            _FAIL, "raised: {}".format(exc))
# --- end test_execute_query_non_select_statement_raises ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 7 test functions and print a summary."""
    print("=== test_db_connection_r7_py.py -- Round 7 ===")
    print("")

    print("-- execute_query: happy paths --")
    test_execute_query_returns_list_of_tuples()
    test_execute_query_returns_empty_list_when_no_rows()
    test_execute_query_calls_execute_with_params()
    test_execute_query_calls_execute_without_params_when_none()
    test_execute_query_calls_execute_without_params_when_empty_list()
    test_execute_query_closes_cursor_on_success()
    print("")

    print("-- execute_query: failure paths --")
    test_execute_query_wraps_database_error()
    test_execute_query_closes_cursor_on_failure()
    test_execute_query_empty_sql_raises()
    test_execute_query_non_string_sql_raises()
    test_execute_query_non_list_params_raises()
    test_execute_query_non_select_statement_raises()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
