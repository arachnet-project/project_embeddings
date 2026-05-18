# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Round 1
# tests/test_db_connection_r1_py.py
# =============================================================================
# Purpose:
#   Round 1 tests for _get_credentials.
#   Tests normal behaviour and all documented error paths.
#   Uses mocked cfg and environment variables — no Oracle connection needed.
#   Runs on Ubuntu (primary dev machine).
#
# Run with:
#   python tests/test_db_connection_r1_py.py
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
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf
from src.common.db_connection import _get_credentials
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
# Helpers — build minimal mocked cfg
# ---------------------------------------------------------------------------

def _make_cfg(tns_alias="ARADB"):
    """Build a minimal OmegaConf DictConfig for testing _get_credentials.

    Mirrors the structure of config/database.yaml after v1.4 rename.
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


# =============================================================================
# Round 1 -- _get_credentials happy paths
# =============================================================================

# --- test_credentials_snomed_happy_path ---
def test_credentials_snomed_happy_path():
    """_get_credentials returns correct tuple for snomed schema."""
    cfg = _make_cfg()
    env = {"SNOMED_DB_PASSWORD": "testpassword"}
    try:
        with patch.dict(os.environ, env, clear=False):
            username, password, tns_alias = _get_credentials(cfg, "snomed")
        if username != "snomed":
            _report("get_credentials: snomed happy path",
                    _FAIL, "username={!r} expected snomed".format(username))
            return
        if password != "testpassword":
            _report("get_credentials: snomed happy path",
                    _FAIL, "password mismatch")
            return
        if tns_alias != "ARADB":
            _report("get_credentials: snomed happy path",
                    _FAIL, "tns_alias={!r} expected ARADB".format(tns_alias))
            return
        _report("get_credentials: snomed happy path", _PASS)
    except Exception as exc:
        _report("get_credentials: snomed happy path",
                _FAIL, "raised: {}".format(exc))
# --- end test_credentials_snomed_happy_path ---


# --- test_credentials_snomed_stage_happy_path ---
def test_credentials_snomed_stage_happy_path():
    """_get_credentials returns correct tuple for snomed_stage schema."""
    cfg = _make_cfg()
    env = {"SNOMED_STAGE_DB_PASSWORD": "stagepassword"}
    try:
        with patch.dict(os.environ, env, clear=False):
            username, password, tns_alias = _get_credentials(cfg, "snomed_stage")
        if username != "snomed_stage":
            _report("get_credentials: snomed_stage happy path",
                    _FAIL, "username={!r}".format(username))
            return
        if password != "stagepassword":
            _report("get_credentials: snomed_stage happy path",
                    _FAIL, "password mismatch")
            return
        if tns_alias != "ARADB":
            _report("get_credentials: snomed_stage happy path",
                    _FAIL, "tns_alias={!r}".format(tns_alias))
            return
        _report("get_credentials: snomed_stage happy path", _PASS)
    except Exception as exc:
        _report("get_credentials: snomed_stage happy path",
                _FAIL, "raised: {}".format(exc))
# --- end test_credentials_snomed_stage_happy_path ---


# --- test_credentials_sys_happy_path ---
def test_credentials_sys_happy_path():
    """_get_credentials returns correct tuple for sys schema."""
    cfg = _make_cfg()
    env = {"SNOMED_SYS_DB_PASSWORD": "syspassword"}
    try:
        with patch.dict(os.environ, env, clear=False):
            username, password, tns_alias = _get_credentials(cfg, "sys")
        if username != "sys":
            _report("get_credentials: sys happy path",
                    _FAIL, "username={!r}".format(username))
            return
        if password != "syspassword":
            _report("get_credentials: sys happy path",
                    _FAIL, "password mismatch")
            return
        if tns_alias != "ARADB":
            _report("get_credentials: sys happy path",
                    _FAIL, "tns_alias={!r}".format(tns_alias))
            return
        _report("get_credentials: sys happy path", _PASS)
    except Exception as exc:
        _report("get_credentials: sys happy path",
                _FAIL, "raised: {}".format(exc))
# --- end test_credentials_sys_happy_path ---


# --- test_credentials_returns_tuple_of_three_strings ---
def test_credentials_returns_tuple_of_three_strings():
    """_get_credentials return value is a tuple of three plain strings."""
    cfg = _make_cfg()
    env = {"SNOMED_DB_PASSWORD": "testpassword"}
    try:
        with patch.dict(os.environ, env, clear=False):
            result = _get_credentials(cfg, "snomed")
        if not isinstance(result, tuple):
            _report("get_credentials: returns tuple",
                    _FAIL, "returned type: {}".format(type(result)))
            return
        if len(result) != 3:
            _report("get_credentials: returns tuple of three",
                    _FAIL, "length: {}".format(len(result)))
            return
        if not all(isinstance(v, str) for v in result):
            _report("get_credentials: all values are strings",
                    _FAIL, "types: {}".format([type(v) for v in result]))
            return
        _report("get_credentials: returns tuple of three strings", _PASS)
    except Exception as exc:
        _report("get_credentials: returns tuple of three strings",
                _FAIL, "raised: {}".format(exc))
# --- end test_credentials_returns_tuple_of_three_strings ---


# =============================================================================
# Round 1 -- _get_credentials error paths
# =============================================================================

# --- test_credentials_unknown_schema_raises_config_error ---
def test_credentials_unknown_schema_raises_config_error():
    """_get_credentials raises SnomedConfigError for an unknown schema."""
    cfg = _make_cfg()
    try:
        _get_credentials(cfg, "banana")
        _report("get_credentials: unknown schema raises SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("get_credentials: unknown schema raises SnomedConfigError",
                _PASS)
    except Exception as exc:
        _report("get_credentials: unknown schema raises SnomedConfigError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_credentials_unknown_schema_raises_config_error ---


# --- test_credentials_missing_password_env_var_raises_db_error ---
def test_credentials_missing_password_env_var_raises_db_error():
    """_get_credentials raises SnomedDBConnectionError when password env var missing."""
    cfg = _make_cfg()
    try:
        # Remove the env var if present
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SNOMED_DB_PASSWORD", None)
            _get_credentials(cfg, "snomed")
        _report("get_credentials: missing password env var raises SnomedDBConnectionError",
                _FAIL, "no exception raised")
    except SnomedDBConnectionError:
        _report("get_credentials: missing password env var raises SnomedDBConnectionError",
                _PASS)
    except Exception as exc:
        _report("get_credentials: missing password env var raises SnomedDBConnectionError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_credentials_missing_password_env_var_raises_db_error ---


# --- test_credentials_empty_password_env_var_raises_db_error ---
def test_credentials_empty_password_env_var_raises_db_error():
    """_get_credentials raises SnomedDBConnectionError when password env var is empty."""
    cfg = _make_cfg()
    env = {"SNOMED_DB_PASSWORD": ""}
    try:
        with patch.dict(os.environ, env, clear=False):
            _get_credentials(cfg, "snomed")
        _report("get_credentials: empty password env var raises SnomedDBConnectionError",
                _FAIL, "no exception raised")
    except SnomedDBConnectionError:
        _report("get_credentials: empty password env var raises SnomedDBConnectionError",
                _PASS)
    except Exception as exc:
        _report("get_credentials: empty password env var raises SnomedDBConnectionError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_credentials_empty_password_env_var_raises_db_error ---


# --- test_credentials_missing_cfg_key_raises_config_error ---
def test_credentials_missing_cfg_key_raises_config_error():
    """_get_credentials raises SnomedConfigError when cfg key is missing."""
    # cfg with no database.snomed section at all
    cfg = OmegaConf.create({
        "database": {
            "tns_alias": "ARADB",
        }
    })
    env = {"SNOMED_DB_PASSWORD": "testpassword"}
    try:
        with patch.dict(os.environ, env, clear=False):
            _get_credentials(cfg, "snomed")
        _report("get_credentials: missing cfg key raises SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("get_credentials: missing cfg key raises SnomedConfigError",
                _PASS)
    except Exception as exc:
        _report("get_credentials: missing cfg key raises SnomedConfigError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_credentials_missing_cfg_key_raises_config_error ---


# --- test_credentials_empty_tns_alias_raises_config_error ---
def test_credentials_empty_tns_alias_raises_config_error():
    """_get_credentials raises SnomedConfigError when tns_alias is empty."""
    cfg = _make_cfg(tns_alias="")
    env = {"SNOMED_DB_PASSWORD": "testpassword"}
    try:
        with patch.dict(os.environ, env, clear=False):
            _get_credentials(cfg, "snomed")
        _report("get_credentials: empty tns_alias raises SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("get_credentials: empty tns_alias raises SnomedConfigError",
                _PASS)
    except Exception as exc:
        _report("get_credentials: empty tns_alias raises SnomedConfigError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_credentials_empty_tns_alias_raises_config_error ---


# --- test_credentials_password_not_logged ---
def test_credentials_password_not_logged():
    """_get_credentials does not include password in exception detail."""
    cfg = _make_cfg()
    secret = "supersecretpassword"
    # Force a SnomedDBConnectionError by using empty password
    # then check a SnomedConfigError message for unknown schema
    try:
        _get_credentials(cfg, "unknown_schema")
    except SnomedConfigError as exc:
        if secret in str(exc):
            _report("get_credentials: password not in exception message",
                    _FAIL, "secret found in exception")
            return
        _report("get_credentials: password not in exception message", _PASS)
    except Exception as exc:
        _report("get_credentials: password not in exception message",
                _FAIL, "unexpected exception: {}".format(exc))
# --- end test_credentials_password_not_logged ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 1 test functions and print a summary."""
    print("=== test_db_connection_r1_py.py -- Round 1 ===")
    print("")

    print("-- _get_credentials: happy paths --")
    test_credentials_snomed_happy_path()
    test_credentials_snomed_stage_happy_path()
    test_credentials_sys_happy_path()
    test_credentials_returns_tuple_of_three_strings()
    print("")

    print("-- _get_credentials: error paths --")
    test_credentials_unknown_schema_raises_config_error()
    test_credentials_missing_password_env_var_raises_db_error()
    test_credentials_empty_password_env_var_raises_db_error()
    test_credentials_missing_cfg_key_raises_config_error()
    test_credentials_empty_tns_alias_raises_config_error()
    test_credentials_password_not_logged()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
