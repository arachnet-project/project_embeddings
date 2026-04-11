# test_config_loader_r2_py.py
# Round 2 tests for src/common/config_loader.py.
# Covers: _resolve_paths, _resolve_interpolation.
#
# Usage:
#   python tests/test_config_loader_r2_py.py
#
# Preconditions:
#   Round 1 tests passing.
#   venv active with omegaconf installed.
#   config/project.yaml, config/database.yaml, config/ingestion.yaml present.
#   SNOMED_LOG_DIR set or ./log/ writable.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Last modified: 2026-04-10

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf, DictConfig

from src.common.config_loader import (
    _load_yaml_file,
    _merge_includes,
    _resolve_paths,
    _resolve_interpolation,
    _PROJECT_YAML,
)
from src.common.exceptions import SnomedConfigError


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_results = []


# --- _report ---
def _report(test_name: str, result: str, detail: str = "") -> None:
    """
    Print and record a single test result.

    Args:
        test_name: Short descriptive name for the test case.
        result: _PASS or _FAIL.
        detail: Optional explanation, required on failure.
    """
    if detail:
        line = "{}: {} — {}".format(result, test_name, detail)
    else:
        line = "{}: {}".format(result, test_name)
    print(line)
    _results.append((result, test_name))
# --- end _report ---


# --- _summarise ---
def _summarise() -> int:
    """
    Print pass and fail counts. Return exit code 0 if all passed,
    1 if any failed.

    Returns:
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


# --- _load_merge_resolve ---
def _load_merge_resolve() -> DictConfig:
    """
    Shared helper. Loads, merges, and resolves paths so each test
    starts from a consistent state ready for _resolve_interpolation.

    Returns:
        OmegaConf DictConfig with cfg.paths added.

    Raises:
        SnomedConfigError: If any step fails.
    """
    cfg = _load_yaml_file(_PROJECT_YAML)
    cfg = _merge_includes(cfg)
    cfg = _resolve_paths(cfg)
    return cfg
# --- end _load_merge_resolve ---


# ---------------------------------------------------------------------------
# Round 2 — _resolve_paths
# ---------------------------------------------------------------------------

# --- test_resolve_paths_cfg_paths_present ---
def test_resolve_paths_cfg_paths_present() -> None:
    """
    After _resolve_paths, cfg.paths exists at the top level.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        cfg = _resolve_paths(cfg)
        if "paths" not in cfg:
            _report("resolve_paths: cfg.paths present at top level",
                    _FAIL, "paths key not found")
            return
        _report("resolve_paths: cfg.paths present at top level", _PASS)
    except Exception as e:
        _report("resolve_paths: cfg.paths present at top level",
                _FAIL, "raised: {}".format(e))
# --- end test_resolve_paths_cfg_paths_present ---


# --- test_resolve_paths_base_present ---
def test_resolve_paths_base_present() -> None:
    """
    After _resolve_paths, cfg.paths.base is present and non-empty.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        cfg = _resolve_paths(cfg)
        val = cfg.paths.get("base")
        if not val:
            _report("resolve_paths: cfg.paths.base present",
                    _FAIL, "key absent or empty")
            return
        _report("resolve_paths: cfg.paths.base present", _PASS)
    except Exception as e:
        _report("resolve_paths: cfg.paths.base present",
                _FAIL, "raised: {}".format(e))
# --- end test_resolve_paths_base_present ---


# --- test_resolve_paths_required_keys ---
def test_resolve_paths_required_keys() -> None:
    """
    After _resolve_paths, cfg.paths contains all required path keys:
    base, log, data_volume, rf2, parquet.
    """
    required = ["base", "log", "data_volume", "rf2", "parquet"]
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        cfg = _resolve_paths(cfg)
        missing = [k for k in required if k not in cfg.paths]
        if missing:
            _report("resolve_paths: required path keys present",
                    _FAIL, "missing: {}".format(", ".join(missing)))
            return
        _report("resolve_paths: required path keys present", _PASS)
    except Exception as e:
        _report("resolve_paths: required path keys present",
                _FAIL, "raised: {}".format(e))
# --- end test_resolve_paths_required_keys ---


# --- test_resolve_paths_invalid_environment ---
def test_resolve_paths_invalid_environment() -> None:
    """
    _resolve_paths raises SnomedConfigError if active_environment is
    not a recognised value.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        cfg = OmegaConf.merge(
            cfg, OmegaConf.create({"active_environment": "invalid_env"}))
        _resolve_paths(cfg)
        _report("resolve_paths: invalid environment raises SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("resolve_paths: invalid environment raises SnomedConfigError",
                _PASS)
    except Exception as e:
        _report("resolve_paths: invalid environment raises SnomedConfigError",
                _FAIL, "wrong exception type: {}".format(type(e)))
# --- end test_resolve_paths_invalid_environment ---


# --- test_resolve_paths_missing_active_environment ---
def test_resolve_paths_missing_active_environment() -> None:
    """
    _resolve_paths raises SnomedConfigError if active_environment key
    is absent entirely.
    """
    try:
        cfg = OmegaConf.create({
            "environments": {
                "development": {
                    "paths": {"base": "/tmp"}
                }
            }
        })
        _resolve_paths(cfg)
        _report("resolve_paths: missing active_environment raises "
                "SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("resolve_paths: missing active_environment raises "
                "SnomedConfigError", _PASS)
    except Exception as e:
        _report("resolve_paths: missing active_environment raises "
                "SnomedConfigError",
                _FAIL, "wrong exception type: {}".format(type(e)))
# --- end test_resolve_paths_missing_active_environment ---


# ---------------------------------------------------------------------------
# Round 2 — _resolve_interpolation
# ---------------------------------------------------------------------------

# --- test_resolve_interpolation_resolves_paths ---
def test_resolve_interpolation_resolves_paths() -> None:
    """
    After _resolve_interpolation, cfg.paths.base is a plain string
    with no interpolation syntax remaining.
    """
    try:
        cfg = _load_merge_resolve()
        cfg = _resolve_interpolation(cfg)
        val = cfg.paths.base
        if "${" in str(val):
            _report("resolve_interpolation: cfg.paths.base is resolved",
                    _FAIL, "interpolation syntax still present: {}".format(val))
            return
        _report("resolve_interpolation: cfg.paths.base is resolved", _PASS)
    except Exception as e:
        _report("resolve_interpolation: cfg.paths.base is resolved",
                _FAIL, "raised: {}".format(e))
# --- end test_resolve_interpolation_resolves_paths ---


# --- test_resolve_interpolation_resolves_derived_paths ---
def test_resolve_interpolation_resolves_derived_paths() -> None:
    """
    After _resolve_interpolation, derived paths such as cfg.paths.rf2
    are plain strings containing the resolved base path.
    """
    try:
        cfg = _load_merge_resolve()
        cfg = _resolve_interpolation(cfg)
        rf2 = str(cfg.paths.rf2)
        base = str(cfg.paths.base)
        if "${" in rf2:
            _report("resolve_interpolation: cfg.paths.rf2 is resolved",
                    _FAIL, "interpolation syntax still present: {}".format(rf2))
            return
        if not rf2.startswith(base):
            _report("resolve_interpolation: cfg.paths.rf2 is resolved",
                    _FAIL, "rf2 does not start with base. "
                    "rf2: {} base: {}".format(rf2, base))
            return
        _report("resolve_interpolation: cfg.paths.rf2 is resolved", _PASS)
    except Exception as e:
        _report("resolve_interpolation: cfg.paths.rf2 is resolved",
                _FAIL, "raised: {}".format(e))
# --- end test_resolve_interpolation_resolves_derived_paths ---


# --- test_resolve_interpolation_bad_reference ---
def test_resolve_interpolation_bad_reference() -> None:
    """
    _resolve_interpolation raises SnomedConfigError if an interpolation
    expression references a key that does not exist.
    """
    try:
        cfg = OmegaConf.create({
            "good_key": "hello",
            "bad_key": "${nonexistent.key}"
        })
        _resolve_interpolation(cfg)
        _report("resolve_interpolation: bad reference raises SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("resolve_interpolation: bad reference raises SnomedConfigError",
                _PASS)
    except Exception as e:
        _report("resolve_interpolation: bad reference raises SnomedConfigError",
                _FAIL, "wrong exception type: {}".format(type(e)))
# --- end test_resolve_interpolation_bad_reference ---


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
def main() -> None:
    """
    Run all Round 2 test functions in sequence and print a summary.
    """
    print("=== test_config_loader_r2_py.py — Round 2 ===")
    print("")

    print("--- _resolve_paths ---")
    test_resolve_paths_cfg_paths_present()
    test_resolve_paths_base_present()
    test_resolve_paths_required_keys()
    test_resolve_paths_invalid_environment()
    test_resolve_paths_missing_active_environment()
    print("")

    print("--- _resolve_interpolation ---")
    test_resolve_interpolation_resolves_paths()
    test_resolve_interpolation_resolves_derived_paths()
    test_resolve_interpolation_bad_reference()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
