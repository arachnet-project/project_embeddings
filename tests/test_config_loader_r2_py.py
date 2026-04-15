#
# Arachnet Clinical Embeddings — Config Loader Test Round 2
# tests/test_config_loader_r2_py.py
# =============================================================================
# Purpose:
#   Round 2 tests for _resolve_paths, _walk_tree, and _resolve_interpolation.
#   Tests normal behaviour and all documented error paths.
#
# Run with:
#   python tests/test_config_loader_r2_py.py
#
# Preconditions:
#   venv active with omegaconf and pyyaml installed.
#   src/common/config_loader.py present.
#
# Author: Jan Mura
# Version: 0.4.0
# =============================================================================

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf, DictConfig
from src.common.config_loader import (
    _resolve_paths,
    _walk_tree,
    _resolve_interpolation,
)

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_results = []


# --- _report ---
def _report(test_name, result, detail=""):
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
def _summarise():
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


# =============================================================================
# Round 2 -- _resolve_paths
# =============================================================================

# --- test_resolve_paths_adds_shortcut ---
def test_resolve_paths_adds_shortcut():
    """_resolve_paths adds cfg.paths as shortcut to active environment paths."""
    try:
        cfg = OmegaConf.create({
            "active_environment": "dev",
            "environments": {
                "dev": {
                    "paths": {
                        "base": "/data/dev",
                        "log": "/data/dev/logs",
                    }
                }
            }
        })
        result = _resolve_paths(cfg)
        if not hasattr(result, "paths"):
            _report("resolve_paths: adds cfg.paths shortcut",
                    _FAIL, "cfg.paths not present")
            return
        if result.paths.base != "/data/dev":
            _report("resolve_paths: adds cfg.paths shortcut",
                    _FAIL, "paths.base wrong: {}".format(result.paths.base))
            return
        if result.paths.log != "/data/dev/logs":
            _report("resolve_paths: adds cfg.paths shortcut",
                    _FAIL, "paths.log wrong: {}".format(result.paths.log))
            return
        _report("resolve_paths: adds cfg.paths shortcut", _PASS)
    except Exception as exc:
        _report("resolve_paths: adds cfg.paths shortcut",
                _FAIL, "raised: {}".format(exc))
# --- end test_resolve_paths_adds_shortcut ---


# --- test_resolve_paths_unknown_environment ---
def test_resolve_paths_unknown_environment():
    """_resolve_paths raises KeyError when active_environment is not in environments."""
    try:
        cfg = OmegaConf.create({
            "active_environment": "staging",
            "environments": {
                "dev": {
                    "paths": {"base": "/data/dev"}
                }
            }
        })
        _resolve_paths(cfg)
        _report("resolve_paths: unknown environment raises KeyError",
                _FAIL, "no exception raised")
    except KeyError as exc:
        if "staging" in str(exc):
            _report("resolve_paths: unknown environment raises KeyError", _PASS)
        else:
            _report("resolve_paths: unknown environment raises KeyError",
                    _FAIL, "message does not mention staging: {}".format(exc))
    except Exception as exc:
        _report("resolve_paths: unknown environment raises KeyError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_resolve_paths_unknown_environment ---


# --- test_resolve_paths_no_environments_section ---
def test_resolve_paths_no_environments_section():
    """_resolve_paths raises KeyError when there is no environments section."""
    try:
        cfg = OmegaConf.create({
            "active_environment": "dev",
        })
        _resolve_paths(cfg)
        _report("resolve_paths: no environments section raises KeyError",
                _FAIL, "no exception raised")
    except KeyError as exc:
        if "environments" in str(exc).lower():
            _report("resolve_paths: no environments section raises KeyError", _PASS)
        else:
            _report("resolve_paths: no environments section raises KeyError",
                    _FAIL, "message does not mention environments: {}".format(exc))
    except Exception as exc:
        _report("resolve_paths: no environments section raises KeyError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_resolve_paths_no_environments_section ---


# --- test_resolve_paths_missing_paths_section ---
def test_resolve_paths_missing_paths_section():
    """_resolve_paths raises ValueError when active environment has no paths."""
    try:
        cfg = OmegaConf.create({
            "active_environment": "dev",
            "environments": {
                "dev": {
                    "database": {"tns_alias": "mydb"}
                }
            }
        })
        _resolve_paths(cfg)
        _report("resolve_paths: missing paths section raises ValueError",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "paths section" in str(exc).lower():
            _report("resolve_paths: missing paths section raises ValueError", _PASS)
        else:
            _report("resolve_paths: missing paths section raises ValueError",
                    _FAIL, "wrong message: {}".format(exc))
    except Exception as exc:
        _report("resolve_paths: missing paths section raises ValueError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_resolve_paths_missing_paths_section ---


# =============================================================================
# Round 2 -- _walk_tree
# =============================================================================

# --- test_walk_tree_flat_dict ---
def test_walk_tree_flat_dict():
    """_walk_tree yields all key-value pairs from a flat DictConfig."""
    try:
        cfg = OmegaConf.create({"a": 1, "b": "hello"})
        result = dict(_walk_tree(cfg))
        expected = {"a": 1, "b": "hello"}
        if result != expected:
            _report("walk_tree: flat dict yields all pairs",
                    _FAIL, "got: {}".format(result))
            return
        _report("walk_tree: flat dict yields all pairs", _PASS)
    except Exception as exc:
        _report("walk_tree: flat dict yields all pairs",
                _FAIL, "raised: {}".format(exc))
# --- end test_walk_tree_flat_dict ---


# --- test_walk_tree_nested_dict ---
def test_walk_tree_nested_dict():
    """_walk_tree yields dot-separated keys for nested DictConfig."""
    try:
        cfg = OmegaConf.create({"outer": {"inner": "value"}})
        result = dict(_walk_tree(cfg))
        expected = {"outer.inner": "value"}
        if result != expected:
            _report("walk_tree: nested dict yields dot-separated keys",
                    _FAIL, "got: {}".format(result))
            return
        _report("walk_tree: nested dict yields dot-separated keys", _PASS)
    except Exception as exc:
        _report("walk_tree: nested dict yields dot-separated keys",
                _FAIL, "raised: {}".format(exc))
# --- end test_walk_tree_nested_dict ---


# --- test_walk_tree_empty_dict ---
def test_walk_tree_empty_dict():
    """_walk_tree yields nothing for an empty DictConfig."""
    try:
        cfg = OmegaConf.create({})
        result = list(_walk_tree(cfg))
        if result:
            _report("walk_tree: empty dict yields nothing",
                    _FAIL, "got: {}".format(result))
            return
        _report("walk_tree: empty dict yields nothing", _PASS)
    except Exception as exc:
        _report("walk_tree: empty dict yields nothing",
                _FAIL, "raised: {}".format(exc))
# --- end test_walk_tree_empty_dict ---


# =============================================================================
# Round 2 -- _resolve_interpolation
# =============================================================================

# --- test_resolve_interpolation_plain_values ---
def test_resolve_interpolation_plain_values():
    """_resolve_interpolation returns cfg unchanged for plain values."""
    try:
        cfg = OmegaConf.create({"key": "value", "number": 42})
        result = _resolve_interpolation(cfg)
        if result.key != "value":
            _report("resolve_interpolation: plain values pass through",
                    _FAIL, "key wrong: {}".format(result.key))
            return
        if result.number != 42:
            _report("resolve_interpolation: plain values pass through",
                    _FAIL, "number wrong: {}".format(result.number))
            return
        _report("resolve_interpolation: plain values pass through", _PASS)
    except Exception as exc:
        _report("resolve_interpolation: plain values pass through",
                _FAIL, "raised: {}".format(exc))
# --- end test_resolve_interpolation_plain_values ---


# --- test_resolve_interpolation_valid_reference ---
def test_resolve_interpolation_valid_reference():
    """_resolve_interpolation passes when all interpolation references exist."""
    try:
        cfg = OmegaConf.create({"base": "/data", "log": "${base}/logs"})
        result = _resolve_interpolation(cfg)
        if result is not cfg:
            _report("resolve_interpolation: valid reference passes",
                    _FAIL, "returned different object")
            return
        _report("resolve_interpolation: valid reference passes", _PASS)
    except Exception as exc:
        _report("resolve_interpolation: valid reference passes",
                _FAIL, "raised: {}".format(exc))
# --- end test_resolve_interpolation_valid_reference ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main():
    """Run all Round 2 test functions and print a summary."""
    print("=== test_config_loader_r2_py.py -- Round 2 ===")
    print("")

    print("-- _resolve_paths --")
    test_resolve_paths_adds_shortcut()
    test_resolve_paths_unknown_environment()
    test_resolve_paths_no_environments_section()
    test_resolve_paths_missing_paths_section()
    print("")

    print("-- _walk_tree --")
    test_walk_tree_flat_dict()
    test_walk_tree_nested_dict()
    test_walk_tree_empty_dict()
    print("")

    print("-- _resolve_interpolation --")
    test_resolve_interpolation_plain_values()
    test_resolve_interpolation_valid_reference()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
