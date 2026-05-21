# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 2
# tests/test_db_connection_r2_py.py
# =============================================================================
# Purpose:
#   Round 2 tests for get_connection.
#   Tests normal behaviour, SYSDBA mode, retry logic, and all documented
#   error paths.
#   Uses mocked oracledb.connect — no Oracle connection needed.
#   Runs on OCI or Ubuntu.
#
# Run with:
#   python tests/test_db_connection_r2_py.py
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
import oracledb
from src.common.db_connection import get_connection
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
# Helpers — build minimal mocked cfg
# ---------------------------------------------------------------------------

def _make_cfg(tns_alias="ARADB"):
    """Build a minimal OmegaConf DictConfig for testing get_connection.

    Mirrors the structure of config/database.yaml v1.4.
    Schema keys match Oracle usernames: snomed, snomed_stage, sys.
    """
    return OmegaConf.create({
        "database": {
            "tns_alias": tns_alias,
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


# ---------------------------------------------------------------------------
# Shared env patches
# ---------------------------------------------------------------------------

_SNOMED_ENV = {
    "SNOMED_DB_PASSWORD": "testpassword",
    "SNOMED_STAGE_DB_PASSWORD": "stagepassword",
    "SNOMED_SYS_DB_PASSWORD": "syspassword",
}


# =============================================================================
# Round 2 -- get_connection happy paths
# =============================================================================

# --- test_get_connection_returns_connection_object ---
def test_get_connection_returns_connection_object():
    """get_connection returns the object from oracledb.connect on success."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", return_value=mock_conn) as mock_connect:
                result = get_connection(cfg, "snomed")
        if result is not mock_conn:
            _report("get_connection: returns connection object",
                    _FAIL, "returned object is not the mock connection")
            return
        _report("get_connection: returns connection object", _PASS)
    except Exception as exc:
        _report("get_connection: returns connection object",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_returns_connection_object ---


# --- test_get_connection_calls_connect_with_correct_args ---
def test_get_connection_calls_connect_with_correct_args():
    """get_connection calls oracledb.connect with correct user, password, dsn."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", return_value=mock_conn) as mock_connect:
                get_connection(cfg, "snomed")
        args, kwargs = mock_connect.call_args
        if kwargs.get("user") != "snomed":
            _report("get_connection: correct connect args",
                    _FAIL, "user={!r}".format(kwargs.get("user")))
            return
        if kwargs.get("password") != "testpassword":
            _report("get_connection: correct connect args",
                    _FAIL, "password mismatch")
            return
        if kwargs.get("dsn") != "ARADB":
            _report("get_connection: correct connect args",
                    _FAIL, "dsn={!r}".format(kwargs.get("dsn")))
            return
        _report("get_connection: correct connect args", _PASS)
    except Exception as exc:
        _report("get_connection: correct connect args",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_calls_connect_with_correct_args ---


# --- test_get_connection_autocommit_false ---
def test_get_connection_autocommit_false():
    """get_connection passes autocommit=False to oracledb.connect."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", return_value=mock_conn) as mock_connect:
                get_connection(cfg, "snomed")
        args, kwargs = mock_connect.call_args
        if kwargs.get("autocommit") != False:
            _report("get_connection: autocommit=False",
                    _FAIL, "autocommit={!r}".format(kwargs.get("autocommit")))
            return
        _report("get_connection: autocommit=False", _PASS)
    except Exception as exc:
        _report("get_connection: autocommit=False",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_autocommit_false ---


# --- test_get_connection_sys_uses_sysdba_mode ---
def test_get_connection_sys_uses_sysdba_mode():
    """get_connection passes AUTH_MODE_SYSDBA when schema is sys."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", return_value=mock_conn) as mock_connect:
                get_connection(cfg, "sys")
        args, kwargs = mock_connect.call_args
        mode = kwargs.get("mode")
        if mode != oracledb.AUTH_MODE_SYSDBA:
            _report("get_connection: sys uses SYSDBA mode",
                    _FAIL, "mode={!r} expected AUTH_MODE_SYSDBA".format(mode))
            return
        _report("get_connection: sys uses SYSDBA mode", _PASS)
    except Exception as exc:
        _report("get_connection: sys uses SYSDBA mode",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_sys_uses_sysdba_mode ---


# --- test_get_connection_snomed_no_sysdba_mode ---
def test_get_connection_snomed_no_sysdba_mode():
    """get_connection does not pass AUTH_MODE_SYSDBA for non-sys schemas."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", return_value=mock_conn) as mock_connect:
                get_connection(cfg, "snomed")
        args, kwargs = mock_connect.call_args
        mode = kwargs.get("mode")
        if mode == oracledb.AUTH_MODE_SYSDBA:
            _report("get_connection: snomed does not use SYSDBA mode",
                    _FAIL, "SYSDBA mode was set for non-sys schema")
            return
        _report("get_connection: snomed does not use SYSDBA mode", _PASS)
    except Exception as exc:
        _report("get_connection: snomed does not use SYSDBA mode",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_snomed_no_sysdba_mode ---


# =============================================================================
# Round 2 -- get_connection retry and failure paths
# =============================================================================

# --- test_get_connection_retries_once_on_failure ---
def test_get_connection_retries_once_on_failure():
    """get_connection calls oracledb.connect exactly twice when first attempt fails."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    side_effects = [oracledb.DatabaseError("first failure"), mock_conn]
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", side_effect=side_effects) as mock_connect:
                with patch("time.sleep"):  # suppress actual sleep
                    result = get_connection(cfg, "snomed")
        if mock_connect.call_count != 2:
            _report("get_connection: retries once on first failure",
                    _FAIL, "call_count={!r} expected 2".format(
                        mock_connect.call_count))
            return
        if result is not mock_conn:
            _report("get_connection: retries once on first failure",
                    _FAIL, "did not return connection from retry attempt")
            return
        _report("get_connection: retries once on first failure", _PASS)
    except Exception as exc:
        _report("get_connection: retries once on first failure",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_retries_once_on_failure ---


# --- test_get_connection_raises_after_two_failures ---
def test_get_connection_raises_after_two_failures():
    """get_connection raises SnomedDBConnectionError after two consecutive failures."""
    cfg = _make_cfg()
    side_effects = [
        oracledb.DatabaseError("first failure"),
        oracledb.DatabaseError("second failure"),
    ]
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", side_effect=side_effects):
                with patch("time.sleep"):
                    get_connection(cfg, "snomed")
        _report("get_connection: raises after two failures",
                _FAIL, "no exception raised")
    except SnomedDBConnectionError:
        _report("get_connection: raises after two failures", _PASS)
    except Exception as exc:
        _report("get_connection: raises after two failures",
                _FAIL, "wrong exception type: {}".format(type(exc).__name__))
# --- end test_get_connection_raises_after_two_failures ---


# --- test_get_connection_no_retry_on_success ---
def test_get_connection_no_retry_on_success():
    """get_connection calls oracledb.connect exactly once when first attempt succeeds."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", return_value=mock_conn) as mock_connect:
                get_connection(cfg, "snomed")
        if mock_connect.call_count != 1:
            _report("get_connection: no retry on success",
                    _FAIL, "call_count={!r} expected 1".format(
                        mock_connect.call_count))
            return
        _report("get_connection: no retry on success", _PASS)
    except Exception as exc:
        _report("get_connection: no retry on success",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_no_retry_on_success ---


# --- test_get_connection_error_message_excludes_password ---
def test_get_connection_error_message_excludes_password():
    """SnomedDBConnectionError raised by get_connection does not contain the password."""
    cfg = _make_cfg()
    secret = "testpassword"
    side_effects = [
        oracledb.DatabaseError("first failure"),
        oracledb.DatabaseError("second failure"),
    ]
    try:
        with patch.dict(os.environ, {**_SNOMED_ENV,
                                     "SNOMED_DB_PASSWORD": secret},
                        clear=False):
            with patch("oracledb.connect", side_effect=side_effects):
                with patch("time.sleep"):
                    get_connection(cfg, "snomed")
        _report("get_connection: error message excludes password",
                _FAIL, "no exception raised")
    except SnomedDBConnectionError as exc:
        if secret in str(exc):
            _report("get_connection: error message excludes password",
                    _FAIL, "password found in exception message")
            return
        _report("get_connection: error message excludes password", _PASS)
    except Exception as exc:
        _report("get_connection: error message excludes password",
                _FAIL, "wrong exception: {}".format(type(exc).__name__))
# --- end test_get_connection_error_message_excludes_password ---


# --- test_get_connection_sleep_called_between_attempts ---
def test_get_connection_sleep_called_between_attempts():
    """get_connection calls time.sleep exactly once between the two attempts."""
    cfg = _make_cfg()
    mock_conn = MagicMock()
    side_effects = [oracledb.DatabaseError("first failure"), mock_conn]
    try:
        with patch.dict(os.environ, _SNOMED_ENV, clear=False):
            with patch("oracledb.connect", side_effect=side_effects):
                with patch("time.sleep") as mock_sleep:
                    get_connection(cfg, "snomed")
        if mock_sleep.call_count != 1:
            _report("get_connection: sleep called once between attempts",
                    _FAIL, "sleep call_count={!r}".format(
                        mock_sleep.call_count))
            return
        _report("get_connection: sleep called once between attempts", _PASS)
    except Exception as exc:
        _report("get_connection: sleep called once between attempts",
                _FAIL, "raised: {}".format(exc))
# --- end test_get_connection_sleep_called_between_attempts ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 2 test functions and print a summary."""
    print("=== test_db_connection_r2_py.py -- Round 2 ===")
    print("")

    print("-- get_connection: happy paths --")
    test_get_connection_returns_connection_object()
    test_get_connection_calls_connect_with_correct_args()
    test_get_connection_autocommit_false()
    test_get_connection_sys_uses_sysdba_mode()
    test_get_connection_snomed_no_sysdba_mode()
    print("")

    print("-- get_connection: retry and failure paths --")
    test_get_connection_retries_once_on_failure()
    test_get_connection_raises_after_two_failures()
    test_get_connection_no_retry_on_success()
    test_get_connection_error_message_excludes_password()
    test_get_connection_sleep_called_between_attempts()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
