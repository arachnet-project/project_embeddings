# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 5
# tests/test_db_connection_r5_py.py
# =============================================================================
# Purpose:
#   Round 5 tests for execute_ddl() in src/common/db_connection.py.
#   Tests successful execution, truncated logging, error wrapping,
#   cursor lifecycle, and input validation.
#   Uses mocked connection and cursor — no Oracle connection needed.
#   Runs on OCI or Ubuntu.
#
# Run with:
#   python tests/test_db_connection_r5_py.py
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
from unittest.mock import patch, MagicMock, call

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import oracledb
from src.common.db_connection import execute_ddl, _DDL_LOG_MAX_LENGTH
from src.common.exceptions import SnomedDDLError

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
    """Build a mock connection with a usable cursor."""
    cursor = MagicMock()
    cursor.execute = MagicMock()
    cursor.close = MagicMock()
    conn = MagicMock()
    conn.cursor = MagicMock(return_value=cursor)
    return conn, cursor


# =============================================================================
# Round 5 -- execute_ddl happy paths
# =============================================================================

# --- test_execute_ddl_returns_none_on_success ---
def test_execute_ddl_returns_none_on_success():
    """execute_ddl returns None when DDL executes without error."""
    conn, _ = _make_mock_conn()
    try:
        result = execute_ddl(conn, "CREATE TABLE test (id NUMBER)")
        if result is not None:
            _report("execute_ddl: returns None on success",
                    _FAIL, "returned {!r} expected None".format(result))
            return
        _report("execute_ddl: returns None on success", _PASS)
    except Exception as exc:
        _report("execute_ddl: returns None on success",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_returns_none_on_success ---


# --- test_execute_ddl_calls_cursor_execute ---
def test_execute_ddl_calls_cursor_execute():
    """execute_ddl calls cursor.execute with the full DDL statement."""
    conn, cursor = _make_mock_conn()
    sql = "CREATE TABLE test (id NUMBER)"
    try:
        execute_ddl(conn, sql)
        if not cursor.execute.called:
            _report("execute_ddl: calls cursor.execute",
                    _FAIL, "cursor.execute was not called")
            return
        actual = cursor.execute.call_args[0][0]
        if actual != sql:
            _report("execute_ddl: calls cursor.execute",
                    _FAIL, "execute called with {!r} expected {!r}".format(
                        actual, sql))
            return
        _report("execute_ddl: calls cursor.execute", _PASS)
    except Exception as exc:
        _report("execute_ddl: calls cursor.execute",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_calls_cursor_execute ---


# --- test_execute_ddl_closes_cursor_on_success ---
def test_execute_ddl_closes_cursor_on_success():
    """execute_ddl closes the cursor after successful execution."""
    conn, cursor = _make_mock_conn()
    try:
        execute_ddl(conn, "CREATE TABLE test (id NUMBER)")
        if not cursor.close.called:
            _report("execute_ddl: closes cursor on success",
                    _FAIL, "cursor.close was not called")
            return
        _report("execute_ddl: closes cursor on success", _PASS)
    except Exception as exc:
        _report("execute_ddl: closes cursor on success",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_closes_cursor_on_success ---


# --- test_execute_ddl_long_statement_not_rejected ---
def test_execute_ddl_long_statement_not_rejected():
    """execute_ddl accepts statements longer than _DDL_LOG_MAX_LENGTH."""
    conn, cursor = _make_mock_conn()
    sql = "CREATE TABLE test ({})".format(
        ", ".join("col{} NUMBER".format(i) for i in range(50))
    )
    try:
        execute_ddl(conn, sql)
        if not cursor.execute.called:
            _report("execute_ddl: long statement not rejected",
                    _FAIL, "cursor.execute was not called")
            return
        _report("execute_ddl: long statement not rejected", _PASS)
    except SnomedDDLError as exc:
        _report("execute_ddl: long statement not rejected",
                _FAIL, "raised SnomedDDLError: {}".format(exc))
    except Exception as exc:
        _report("execute_ddl: long statement not rejected",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_long_statement_not_rejected ---


# =============================================================================
# Round 5 -- execute_ddl failure paths
# =============================================================================

# --- test_execute_ddl_wraps_database_error ---
def test_execute_ddl_wraps_database_error():
    """execute_ddl wraps oracledb.DatabaseError in SnomedDDLError."""
    conn, cursor = _make_mock_conn()
    cursor.execute.side_effect = oracledb.DatabaseError("ORA-00955: name already used")
    raised = False
    try:
        try:
            execute_ddl(conn, "CREATE TABLE test (id NUMBER)")
        except SnomedDDLError:
            raised = True
        if not raised:
            _report("execute_ddl: wraps DatabaseError in SnomedDDLError",
                    _FAIL, "SnomedDDLError was not raised")
            return
        _report("execute_ddl: wraps DatabaseError in SnomedDDLError", _PASS)
    except Exception as exc:
        _report("execute_ddl: wraps DatabaseError in SnomedDDLError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_wraps_database_error ---


# --- test_execute_ddl_error_contains_truncated_statement ---
def test_execute_ddl_error_contains_truncated_statement():
    """SnomedDDLError raised by execute_ddl contains the truncated statement."""
    conn, cursor = _make_mock_conn()
    cursor.execute.side_effect = oracledb.DatabaseError("ORA-00942: table not found")
    sql = "DROP TABLE sct_concept"
    try:
        try:
            execute_ddl(conn, sql)
        except SnomedDDLError as exc:
            if "DROP TABLE sct_concept" not in str(exc):
                _report(
                    "execute_ddl: error contains truncated statement",
                    _FAIL,
                    "statement not found in error: {}".format(exc))
                return
            _report("execute_ddl: error contains truncated statement", _PASS)
            return
        _report("execute_ddl: error contains truncated statement",
                _FAIL, "SnomedDDLError was not raised")
    except Exception as exc:
        _report("execute_ddl: error contains truncated statement",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_error_contains_truncated_statement ---


# --- test_execute_ddl_closes_cursor_on_failure ---
def test_execute_ddl_closes_cursor_on_failure():
    """execute_ddl closes the cursor even when execution raises."""
    conn, cursor = _make_mock_conn()
    cursor.execute.side_effect = oracledb.DatabaseError("ORA-00955")
    try:
        try:
            execute_ddl(conn, "CREATE TABLE test (id NUMBER)")
        except SnomedDDLError:
            pass
        if not cursor.close.called:
            _report("execute_ddl: closes cursor on failure",
                    _FAIL, "cursor.close was not called")
            return
        _report("execute_ddl: closes cursor on failure", _PASS)
    except Exception as exc:
        _report("execute_ddl: closes cursor on failure",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_closes_cursor_on_failure ---


# --- test_execute_ddl_empty_string_raises ---
def test_execute_ddl_empty_string_raises():
    """execute_ddl raises SnomedDDLError when sql is an empty string."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_ddl(conn, "")
        except SnomedDDLError:
            raised = True
        if not raised:
            _report("execute_ddl: empty string raises SnomedDDLError",
                    _FAIL, "SnomedDDLError was not raised")
            return
        _report("execute_ddl: empty string raises SnomedDDLError", _PASS)
    except Exception as exc:
        _report("execute_ddl: empty string raises SnomedDDLError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_empty_string_raises ---


# --- test_execute_ddl_whitespace_only_raises ---
def test_execute_ddl_whitespace_only_raises():
    """execute_ddl raises SnomedDDLError when sql is whitespace only."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_ddl(conn, "   ")
        except SnomedDDLError:
            raised = True
        if not raised:
            _report("execute_ddl: whitespace-only raises SnomedDDLError",
                    _FAIL, "SnomedDDLError was not raised")
            return
        _report("execute_ddl: whitespace-only raises SnomedDDLError", _PASS)
    except Exception as exc:
        _report("execute_ddl: whitespace-only raises SnomedDDLError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_whitespace_only_raises ---


# --- test_execute_ddl_non_string_raises ---
def test_execute_ddl_non_string_raises():
    """execute_ddl raises SnomedDDLError when sql is not a string."""
    conn, _ = _make_mock_conn()
    raised = False
    try:
        try:
            execute_ddl(conn, 42)
        except SnomedDDLError:
            raised = True
        if not raised:
            _report("execute_ddl: non-string raises SnomedDDLError",
                    _FAIL, "SnomedDDLError was not raised")
            return
        _report("execute_ddl: non-string raises SnomedDDLError", _PASS)
    except Exception as exc:
        _report("execute_ddl: non-string raises SnomedDDLError",
                _FAIL, "raised: {}".format(exc))
# --- end test_execute_ddl_non_string_raises ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 5 test functions and print a summary."""
    print("=== test_db_connection_r5_py.py -- Round 5 ===")
    print("")

    print("-- execute_ddl: happy paths --")
    test_execute_ddl_returns_none_on_success()
    test_execute_ddl_calls_cursor_execute()
    test_execute_ddl_closes_cursor_on_success()
    test_execute_ddl_long_statement_not_rejected()
    print("")

    print("-- execute_ddl: failure paths --")
    test_execute_ddl_wraps_database_error()
    test_execute_ddl_error_contains_truncated_statement()
    test_execute_ddl_closes_cursor_on_failure()
    test_execute_ddl_empty_string_raises()
    test_execute_ddl_whitespace_only_raises()
    test_execute_ddl_non_string_raises()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
