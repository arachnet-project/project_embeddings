# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 3
# tests/test_db_connection_r3_py.py
# =============================================================================
# Purpose:
#   Round 3 tests for open_connection.
#   Tests happy path, guaranteed close on exit, exception propagation,
#   and get_connection failure paths.
#   Uses mocked get_connection and connection object — no Oracle needed.
#   Runs on OCI or Ubuntu.
#
# Run with:
#   python tests/test_db_connection_r3_py.py
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
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf
from src.common.db_connection import open_connection
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
    """Build a minimal OmegaConf DictConfig for testing open_connection.

    Mirrors the structure of config/database.yaml v1.4.
    Schema keys match Oracle usernames: snomed, snomed_stage, sys.
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
    """Build a mock connection object with a trackable close method."""
    conn = MagicMock()
    conn.close = MagicMock()
    return conn


# =============================================================================
# Round 3 -- open_connection happy paths
# =============================================================================

# --- test_open_connection_yields_connection ---
def test_open_connection_yields_connection():
    """open_connection yields the connection returned by get_connection."""
    cfg = _make_cfg()
    mock_conn = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.get_connection",
            return_value=mock_conn,
        ):
            with open_connection(cfg, "snomed") as conn:
                if conn is not mock_conn:
                    _report("open_connection: yields connection",
                            _FAIL, "yielded object is not the mock connection")
                    return
        _report("open_connection: yields connection", _PASS)
    except Exception as exc:
        _report("open_connection: yields connection",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_yields_connection ---


# --- test_open_connection_closes_on_clean_exit ---
def test_open_connection_closes_on_clean_exit():
    """open_connection calls conn.close() after the with block exits normally."""
    cfg = _make_cfg()
    mock_conn = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.get_connection",
            return_value=mock_conn,
        ):
            with open_connection(cfg, "snomed"):
                pass
        if not mock_conn.close.called:
            _report("open_connection: closes on clean exit",
                    _FAIL, "conn.close() was not called")
            return
        _report("open_connection: closes on clean exit", _PASS)
    except Exception as exc:
        _report("open_connection: closes on clean exit",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_closes_on_clean_exit ---


# --- test_open_connection_close_called_exactly_once_on_clean_exit ---
def test_open_connection_close_called_exactly_once_on_clean_exit():
    """open_connection calls conn.close() exactly once on clean exit."""
    cfg = _make_cfg()
    mock_conn = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.get_connection",
            return_value=mock_conn,
        ):
            with open_connection(cfg, "snomed"):
                pass
        if mock_conn.close.call_count != 1:
            _report("open_connection: close called exactly once on clean exit",
                    _FAIL, "call_count={!r} expected 1".format(
                        mock_conn.close.call_count))
            return
        _report("open_connection: close called exactly once on clean exit",
                _PASS)
    except Exception as exc:
        _report("open_connection: close called exactly once on clean exit",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_close_called_exactly_once_on_clean_exit ---


# =============================================================================
# Round 3 -- open_connection exception handling
# =============================================================================

# --- test_open_connection_closes_on_exception_in_block ---
def test_open_connection_closes_on_exception_in_block():
    """open_connection calls conn.close() even when exception raised in block."""
    cfg = _make_cfg()
    mock_conn = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.get_connection",
            return_value=mock_conn,
        ):
            try:
                with open_connection(cfg, "snomed"):
                    raise RuntimeError("inside block")
            except RuntimeError:
                pass
        if not mock_conn.close.called:
            _report("open_connection: closes on exception in block",
                    _FAIL, "conn.close() was not called")
            return
        _report("open_connection: closes on exception in block", _PASS)
    except Exception as exc:
        _report("open_connection: closes on exception in block",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_closes_on_exception_in_block ---


# --- test_open_connection_close_called_exactly_once_on_exception ---
def test_open_connection_close_called_exactly_once_on_exception():
    """open_connection calls conn.close() exactly once when exception raised."""
    cfg = _make_cfg()
    mock_conn = _make_mock_conn()
    try:
        with patch(
            "src.common.db_connection.get_connection",
            return_value=mock_conn,
        ):
            try:
                with open_connection(cfg, "snomed"):
                    raise ValueError("boom")
            except ValueError:
                pass
        if mock_conn.close.call_count != 1:
            _report(
                "open_connection: close called exactly once on exception",
                _FAIL, "call_count={!r} expected 1".format(
                    mock_conn.close.call_count))
            return
        _report("open_connection: close called exactly once on exception",
                _PASS)
    except Exception as exc:
        _report("open_connection: close called exactly once on exception",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_close_called_exactly_once_on_exception ---


# --- test_open_connection_exception_in_block_propagates ---
def test_open_connection_exception_in_block_propagates():
    """An exception raised inside the with block propagates to the caller."""
    cfg = _make_cfg()
    mock_conn = _make_mock_conn()
    propagated = False
    try:
        with patch(
            "src.common.db_connection.get_connection",
            return_value=mock_conn,
        ):
            try:
                with open_connection(cfg, "snomed"):
                    raise RuntimeError("propagate me")
            except RuntimeError as exc:
                if "propagate me" in str(exc):
                    propagated = True
        if not propagated:
            _report("open_connection: exception in block propagates",
                    _FAIL, "RuntimeError did not propagate")
            return
        _report("open_connection: exception in block propagates", _PASS)
    except Exception as exc:
        _report("open_connection: exception in block propagates",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_exception_in_block_propagates ---


# =============================================================================
# Round 3 -- open_connection failure paths
# =============================================================================

# --- test_open_connection_db_error_propagates ---
def test_open_connection_db_error_propagates():
    """SnomedDBConnectionError from get_connection propagates cleanly."""
    cfg = _make_cfg()
    raised = False
    try:
        with patch(
            "src.common.db_connection.get_connection",
            side_effect=SnomedDBConnectionError(
                "Failed to connect.", "schema=snomed"
            ),
        ):
            try:
                with open_connection(cfg, "snomed"):
                    pass
            except SnomedDBConnectionError:
                raised = True
        if not raised:
            _report("open_connection: SnomedDBConnectionError propagates",
                    _FAIL, "exception did not propagate")
            return
        _report("open_connection: SnomedDBConnectionError propagates", _PASS)
    except Exception as exc:
        _report("open_connection: SnomedDBConnectionError propagates",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_db_error_propagates ---


# --- test_open_connection_config_error_propagates ---
def test_open_connection_config_error_propagates():
    """SnomedConfigError from get_connection propagates cleanly."""
    cfg = _make_cfg()
    raised = False
    try:
        with patch(
            "src.common.db_connection.get_connection",
            side_effect=SnomedConfigError(
                "Missing config.", "cfg_path=database.snomed"
            ),
        ):
            try:
                with open_connection(cfg, "snomed"):
                    pass
            except SnomedConfigError:
                raised = True
        if not raised:
            _report("open_connection: SnomedConfigError propagates",
                    _FAIL, "exception did not propagate")
            return
        _report("open_connection: SnomedConfigError propagates", _PASS)
    except Exception as exc:
        _report("open_connection: SnomedConfigError propagates",
                _FAIL, "raised: {}".format(exc))
# --- end test_open_connection_config_error_propagates ---


# --- test_open_connection_invalid_schema_raises_config_error ---
def test_open_connection_invalid_schema_raises_config_error():
    """An invalid schema name raises SnomedConfigError."""
    cfg = _make_cfg()
    raised = False
    try:
        try:
            with open_connection(cfg, "invalid_schema"):
                pass
        except SnomedConfigError:
            raised = True
        if not raised:
            _report("open_connection: invalid schema raises SnomedConfigError",
                    _FAIL, "SnomedConfigError was not raised")
            return
        _report("open_connection: invalid schema raises SnomedConfigError",
                _PASS)
    except Exception as exc:
        _report("open_connection: invalid schema raises SnomedConfigError",
                _FAIL, "wrong exception: {}".format(type(exc).__name__))
# --- end test_open_connection_invalid_schema_raises_config_error ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 3 test functions and print a summary."""
    print("=== test_db_connection_r3_py.py -- Round 3 ===")
    print("")

    print("-- open_connection: happy paths --")
    test_open_connection_yields_connection()
    test_open_connection_closes_on_clean_exit()
    test_open_connection_close_called_exactly_once_on_clean_exit()
    print("")

    print("-- open_connection: exception handling --")
    test_open_connection_closes_on_exception_in_block()
    test_open_connection_close_called_exactly_once_on_exception()
    test_open_connection_exception_in_block_propagates()
    print("")

    print("-- open_connection: failure paths --")
    test_open_connection_db_error_propagates()
    test_open_connection_config_error_propagates()
    test_open_connection_invalid_schema_raises_config_error()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
