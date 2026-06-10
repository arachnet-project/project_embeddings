# ARC_FILE: tests/test_db_connection_r4_py.py
# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 4
# tests/test_db_connection_r4_py.py
# =============================================================================
# Purpose:
#   Round 4 tests for test_connection() in src/common/db_connection.py.
#   Tests successful execution, query execution, failure propagation,
#   and invalid schema handling.
#   Uses mocked open_connection and cursor — no Oracle connection needed.
#   Runs on OCI or Ubuntu.
#
# Run with:
#   python tests/test_db_connection_r4_py.py
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

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf
from src.common.db_connection import test_connection
from src.common.exceptions import SnomedConfigError, SnomedDBConnectionError

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

def _make_cfg():
    """Build a minimal OmegaConf DictConfig for testing test_connection.

    Mirrors the structure of config/database.yaml v1.4.
    """
    return OmegaConf.create({
        "database": {
            "tns_alias": "ARADB",
            "snomed": {
                "user": "snomed",
                "password_env_var": "SNOMED_DB_PASSWORD",
            },
            "snomed_stage": {
                "user": "snomed_stage",
                "password_env_var": "SNOMED_STAGE_DB_PASSWORD",
            },
            "sys": {
                "user": "sys",
                "password_env_var": "SNOMED_SYS_DB_PASSWORD",
            },
        }
    })


def _make_mock_conn():
    """Build a mock connection with a usable cursor."""
    cursor = MagicMock()
    cursor.fetchone = MagicMock(return_value=(1,))
    cursor.execute = MagicMock()
    cursor.close = MagicMock()
    conn = MagicMock()
    conn.cursor = MagicMock(return_value=cursor)
    conn.close = MagicMock()
    return conn, cursor


# =============================================================================
# Round 4 -- test_connection happy paths
# =============================================================================

# --- test_test_connection_returns_none_on_success ---
def test_test_connection_returns_none_on_success():
    """test_connection returns None on successful query execution."""
    cfg = _make_cfg()
    mock_conn, _ = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.open_connection",
        ) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(
                return_value=mock_conn)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            result = test_connection(cfg, "snomed")
        if result is not None:
            _report("test_connection: returns None on success",
                    _FAIL, "returned {!r} expected None".format(result))
            return
        _report("test_connection: returns None on success", _PASS)
    except Exception as exc:
        _report("test_connection: returns None on success",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_returns_none_on_success ---


# --- test_test_connection_executes_test_query ---
def test_test_connection_executes_test_query():
    """test_connection executes SELECT 1 FROM DUAL against the schema."""
    cfg = _make_cfg()
    mock_conn, mock_cursor = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.open_connection",
        ) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(
                return_value=mock_conn)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            test_connection(cfg, "snomed")
        if not mock_cursor.execute.called:
            _report("test_connection: executes test query",
                    _FAIL, "cursor.execute was not called")
            return
        actual_query = mock_cursor.execute.call_args[0][0]
        if "DUAL" not in actual_query:
            _report("test_connection: executes test query",
                    _FAIL, "query={!r} does not reference DUAL".format(
                        actual_query))
            return
        _report("test_connection: executes test query", _PASS)
    except Exception as exc:
        _report("test_connection: executes test query",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_executes_test_query ---


# --- test_test_connection_calls_fetchone ---
def test_test_connection_calls_fetchone():
    """test_connection calls fetchone() to consume the query result."""
    cfg = _make_cfg()
    mock_conn, mock_cursor = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.open_connection",
        ) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(
                return_value=mock_conn)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            test_connection(cfg, "snomed")
        if not mock_cursor.fetchone.called:
            _report("test_connection: calls fetchone",
                    _FAIL, "cursor.fetchone was not called")
            return
        _report("test_connection: calls fetchone", _PASS)
    except Exception as exc:
        _report("test_connection: calls fetchone",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_calls_fetchone ---


# --- test_test_connection_closes_cursor ---
def test_test_connection_closes_cursor():
    """test_connection closes the cursor after the query."""
    cfg = _make_cfg()
    mock_conn, mock_cursor = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.open_connection",
        ) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(
                return_value=mock_conn)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            test_connection(cfg, "snomed")
        if not mock_cursor.close.called:
            _report("test_connection: closes cursor",
                    _FAIL, "cursor.close was not called")
            return
        _report("test_connection: closes cursor", _PASS)
    except Exception as exc:
        _report("test_connection: closes cursor",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_closes_cursor ---


# =============================================================================
# Round 4 -- test_connection failure paths
# =============================================================================

# --- test_test_connection_propagates_db_connection_error ---
def test_test_connection_propagates_db_connection_error():
    """test_connection propagates SnomedDBConnectionError from open_connection."""
    cfg = _make_cfg()
    raised = False
    try:
        with patch(
            "src.common.db_connection.open_connection",
            side_effect=SnomedDBConnectionError(
                "Failed to connect.", "schema=snomed"
            ),
        ):
            try:
                test_connection(cfg, "snomed")
            except SnomedDBConnectionError:
                raised = True
        if not raised:
            _report(
                "test_connection: propagates SnomedDBConnectionError",
                _FAIL, "exception did not propagate")
            return
        _report("test_connection: propagates SnomedDBConnectionError", _PASS)
    except Exception as exc:
        _report("test_connection: propagates SnomedDBConnectionError",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_propagates_db_connection_error ---


# --- test_test_connection_propagates_config_error ---
def test_test_connection_propagates_config_error():
    """test_connection propagates SnomedConfigError from open_connection."""
    cfg = _make_cfg()
    raised = False
    try:
        with patch(
            "src.common.db_connection.open_connection",
            side_effect=SnomedConfigError(
                "Missing config.", "cfg_path=database.snomed"
            ),
        ):
            try:
                test_connection(cfg, "snomed")
            except SnomedConfigError:
                raised = True
        if not raised:
            _report("test_connection: propagates SnomedConfigError",
                    _FAIL, "exception did not propagate")
            return
        _report("test_connection: propagates SnomedConfigError", _PASS)
    except Exception as exc:
        _report("test_connection: propagates SnomedConfigError",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_propagates_config_error ---


# --- test_test_connection_wraps_query_error ---
def test_test_connection_wraps_query_error():
    """test_connection wraps unexpected query errors in SnomedDBConnectionError."""
    cfg = _make_cfg()
    mock_conn, mock_cursor = _make_mock_conn()
    mock_cursor.execute.side_effect = Exception("ORA-00942: table not found")
    raised_correct = False
    try:
        with patch(
            "src.common.db_connection.open_connection",
        ) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(
                return_value=mock_conn)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            try:
                test_connection(cfg, "snomed")
            except SnomedDBConnectionError:
                raised_correct = True
        if not raised_correct:
            _report("test_connection: wraps query error in SnomedDBConnectionError",
                    _FAIL, "SnomedDBConnectionError was not raised")
            return
        _report("test_connection: wraps query error in SnomedDBConnectionError",
                _PASS)
    except Exception as exc:
        _report("test_connection: wraps query error in SnomedDBConnectionError",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_wraps_query_error ---


# --- test_test_connection_invalid_schema_raises_config_error ---
def test_test_connection_invalid_schema_raises_config_error():
    """test_connection raises SnomedConfigError for an invalid schema name."""
    cfg = _make_cfg()
    raised = False
    try:
        try:
            test_connection(cfg, "invalid_schema")
        except SnomedConfigError:
            raised = True
        if not raised:
            _report(
                "test_connection: invalid schema raises SnomedConfigError",
                _FAIL, "SnomedConfigError was not raised")
            return
        _report("test_connection: invalid schema raises SnomedConfigError",
                _PASS)
    except Exception as exc:
        _report("test_connection: invalid schema raises SnomedConfigError",
                _FAIL, "wrong exception: {}".format(type(exc).__name__))
# --- end test_test_connection_invalid_schema_raises_config_error ---


# --- test_test_connection_snomed_stage_schema ---
def test_test_connection_snomed_stage_schema():
    """test_connection works correctly for snomed_stage schema."""
    cfg = _make_cfg()
    mock_conn, _ = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.open_connection",
        ) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(
                return_value=mock_conn)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            result = test_connection(cfg, "snomed_stage")
        if result is not None:
            _report("test_connection: works for snomed_stage",
                    _FAIL, "returned {!r} expected None".format(result))
            return
        _report("test_connection: works for snomed_stage", _PASS)
    except Exception as exc:
        _report("test_connection: works for snomed_stage",
                _FAIL, "raised: {}".format(exc))
# --- end test_test_connection_snomed_stage_schema ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 4 test functions and print a summary."""
    print("=== test_db_connection_r4_py.py -- Round 4 ===")
    print("")

    print("-- test_connection: happy paths --")
    test_test_connection_returns_none_on_success()
    test_test_connection_executes_test_query()
    test_test_connection_calls_fetchone()
    test_test_connection_closes_cursor()
    print("")

    print("-- test_connection: failure paths --")
    test_test_connection_propagates_db_connection_error()
    test_test_connection_propagates_config_error()
    test_test_connection_wraps_query_error()
    test_test_connection_invalid_schema_raises_config_error()
    test_test_connection_snomed_stage_schema()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
