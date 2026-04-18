# =============================================================================
# Arachnet Clinical Embeddings — Config Loader Test Round 3
# tests/test_config_loader_r3_py.py
# =============================================================================
# Purpose:
#   Round 3 tests for _validate_mandatory_keys.
#   Tests normal behaviour and all documented error paths.
#
# Run with:
#   python tests/test_config_loader_r3_py.py
#
# Preconditions:
#   venv active with omegaconf and pyyaml installed.
#   src/common/config_loader.py present.
#
# Author: Jan Mura
# Version: 0.4.0
# =============================================================================

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf
from src.common.config_loader import _validate_mandatory_keys, MANDATORY_KEYS

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
# Helper to build a minimal valid cfg for testing.
# All mandatory keys present and non-null.
# ---------------------------------------------------------------------------

# --- _make_valid_cfg ---
def _make_valid_cfg() -> OmegaConf:
    """Build a minimal OmegaConf DictConfig with all mandatory keys present.

    Returns
    -------
    DictConfig
        A configuration object that passes _validate_mandatory_keys.
    """
    return OmegaConf.create({
        "active_environment": "dev",
        "project": {
            "name": "arachnet",
            "data_release": "20240101",
            "snomed_notice": "SNOMED CT notice text",
        },
        "paths": {
            "base": "/data",
            "log": "/data/log",
            "data_volume": "/data/volume",
            "rf2": "/data/rf2",
            "parquet": "/data/parquet",
        },
        "database": {
            "tns_alias": "mydb",
            "production_schema": {
                "user": "prod_user",
                "password_env_var": "PROD_PASSWORD",
                "tablespace": "prod_ts",
            },
            "stage_schema": {
                "user": "stage_user",
                "password_env_var": "STAGE_PASSWORD",
                "tablespace": "stage_ts",
            },
            "tables": ["concept", "description"],
        },
        "ingestion": {
            "release": {
                "release_type": "full",
                "encoding": "utf-8",
                "delimiter": "\\t",
                "skip_header": True,
            },
            "load": {
                "batch_size": 1000,
                "truncate_before_load": True,
                "commit_frequency": 1000,
                "stop_on_error": True,
            },
            "national_extensions": {
                "enabled": False,
            },
            "validation": {
                "enabled": True,
                "abort_on_blocking_failure": True,
            },
            "swap": {
                "strategy": "rename",
                "previous_schema_action": "drop",
                "previous_schema_name": "prev_schema",
            },
            "logging": {
                "level": "INFO",
                "manifest_target": "file",
                "manifest_filename": "manifest.json",
            },
        },
        "governance": {
            "license": "Apache 2.0",
        },
    })
# --- end _make_valid_cfg ---


# =============================================================================
# Round 3 -- _validate_mandatory_keys
# =============================================================================

# --- test_validate_all_keys_present ---
def test_validate_all_keys_present() -> None:
    """_validate_mandatory_keys returns cfg when all mandatory keys present."""
    try:
        cfg = _make_valid_cfg()
        result = _validate_mandatory_keys(cfg)
        if result is not cfg:
            _report("validate_mandatory_keys: all keys present returns cfg",
                    _FAIL, "returned different object")
            return
        _report("validate_mandatory_keys: all keys present returns cfg", _PASS)
    except Exception as exc:
        _report("validate_mandatory_keys: all keys present returns cfg",
                _FAIL, "raised: {}".format(exc))
# --- end test_validate_all_keys_present ---


# --- test_validate_single_missing_key ---
def test_validate_single_missing_key() -> None:
    """_validate_mandatory_keys raises ValueError when one key is missing."""
    try:
        cfg = _make_valid_cfg()
        # Remove governance.license by rebuilding without it.
        d = OmegaConf.to_container(cfg, resolve=False)
        del d["governance"]["license"]
        cfg = OmegaConf.create(d)

        _validate_mandatory_keys(cfg)
        _report("validate_mandatory_keys: single missing key raises ValueError",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "governance.license" in str(exc):
            _report("validate_mandatory_keys: single missing key raises ValueError",
                    _PASS)
        else:
            _report("validate_mandatory_keys: single missing key raises ValueError",
                    _FAIL, "missing key not in message: {}".format(exc))
    except Exception as exc:
        _report("validate_mandatory_keys: single missing key raises ValueError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_validate_single_missing_key ---


# --- test_validate_multiple_missing_keys ---
def test_validate_multiple_missing_keys() -> None:
    """_validate_mandatory_keys reports all missing keys in one error."""
    try:
        cfg = _make_valid_cfg()
        d = OmegaConf.to_container(cfg, resolve=False)
        del d["governance"]["license"]
        del d["project"]["name"]
        cfg = OmegaConf.create(d)

        _validate_mandatory_keys(cfg)
        _report("validate_mandatory_keys: multiple missing keys all reported",
                _FAIL, "no exception raised")
    except ValueError as exc:
        msg = str(exc)
        if "governance.license" in msg and "project.name" in msg:
            _report("validate_mandatory_keys: multiple missing keys all reported",
                    _PASS)
        else:
            _report("validate_mandatory_keys: multiple missing keys all reported",
                    _FAIL, "not all keys in message: {}".format(exc))
    except Exception as exc:
        _report("validate_mandatory_keys: multiple missing keys all reported",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_validate_multiple_missing_keys ---


# --- test_validate_null_value_treated_as_missing ---
def test_validate_null_value_treated_as_missing() -> None:
    """_validate_mandatory_keys treats a null value as missing."""
    try:
        cfg = _make_valid_cfg()
        d = OmegaConf.to_container(cfg, resolve=False)
        d["database"]["tns_alias"] = None
        cfg = OmegaConf.create(d)

        _validate_mandatory_keys(cfg)
        _report("validate_mandatory_keys: null value treated as missing",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "database.tns_alias" in str(exc):
            _report("validate_mandatory_keys: null value treated as missing",
                    _PASS)
        else:
            _report("validate_mandatory_keys: null value treated as missing",
                    _FAIL, "key not in message: {}".format(exc))
    except Exception as exc:
        _report("validate_mandatory_keys: null value treated as missing",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_validate_null_value_treated_as_missing ---


# --- test_validate_error_message_format ---
def test_validate_error_message_format() -> None:
    """_validate_mandatory_keys error message contains expected prefix."""
    try:
        cfg = _make_valid_cfg()
        d = OmegaConf.to_container(cfg, resolve=False)
        del d["governance"]["license"]
        cfg = OmegaConf.create(d)

        _validate_mandatory_keys(cfg)
        _report("validate_mandatory_keys: error message has expected prefix",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "mandatory keys" in str(exc).lower():
            _report("validate_mandatory_keys: error message has expected prefix",
                    _PASS)
        else:
            _report("validate_mandatory_keys: error message has expected prefix",
                    _FAIL, "prefix not found in message: {}".format(exc))
    except Exception as exc:
        _report("validate_mandatory_keys: error message has expected prefix",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_validate_error_message_format ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 3 test functions and print a summary."""
    print("=== test_config_loader_r3_py.py -- Round 3 ===")
    print("")

    print("-- _validate_mandatory_keys --")
    test_validate_all_keys_present()
    test_validate_single_missing_key()
    test_validate_multiple_missing_keys()
    test_validate_null_value_treated_as_missing()
    test_validate_error_message_format()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
