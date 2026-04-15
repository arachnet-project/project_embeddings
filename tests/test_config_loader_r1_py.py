# =============================================================================
# Arachnet Clinical Embeddings — Config Loader Test Round 1
# tests/test_config_loader_r1_py.py
# =============================================================================
# Purpose:
#   Round 1 tests for _load_yaml_file and _merge_includes.
#   Tests normal behaviour and all documented error paths.
#
# Run with:
#   python tests/test_config_loader_r1_py.py
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
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import OmegaConf, DictConfig
from src.common.config_loader import _load_yaml_file, _merge_includes

# Directory containing the real project config files.
_CONFIG_DIR = str(PROJECT_ROOT / "config")

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
# Round 1 -- _load_yaml_file
# =============================================================================

# --- test_load_valid_file_returns_dictconfig ---
def test_load_valid_file_returns_dictconfig():
    """_load_yaml_file returns a DictConfig for a valid YAML file."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("key: value\n")
            tmp = fh.name
        result = _load_yaml_file(tmp)
        if not isinstance(result, DictConfig):
            _report("load_yaml_file: valid file returns DictConfig",
                    _FAIL, "returned type: {}".format(type(result)))
            return
        if result.key != "value":
            _report("load_yaml_file: valid file returns DictConfig",
                    _FAIL, "expected key=value, got: {}".format(result.key))
            return
        _report("load_yaml_file: valid file returns DictConfig", _PASS)
    except Exception as exc:
        _report("load_yaml_file: valid file returns DictConfig",
                _FAIL, "raised: {}".format(exc))
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
# --- end test_load_valid_file_returns_dictconfig ---


# --- test_load_missing_file_raises_filenotfounderror ---
def test_load_missing_file_raises_filenotfounderror():
    """_load_yaml_file raises FileNotFoundError for a missing file."""
    try:
        _load_yaml_file("/nonexistent/path/to/config.yaml")
        _report("load_yaml_file: missing file raises FileNotFoundError",
                _FAIL, "no exception raised")
    except FileNotFoundError:
        _report("load_yaml_file: missing file raises FileNotFoundError", _PASS)
    except Exception as exc:
        _report("load_yaml_file: missing file raises FileNotFoundError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_load_missing_file_raises_filenotfounderror ---


# --- test_load_empty_file_raises_valueerror ---
def test_load_empty_file_raises_valueerror():
    """_load_yaml_file raises ValueError for an empty file."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("")
            tmp = fh.name
        _load_yaml_file(tmp)
        _report("load_yaml_file: empty file raises ValueError",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "empty" in str(exc).lower():
            _report("load_yaml_file: empty file raises ValueError", _PASS)
        else:
            _report("load_yaml_file: empty file raises ValueError",
                    _FAIL, "wrong message: {}".format(exc))
    except Exception as exc:
        _report("load_yaml_file: empty file raises ValueError",
                _FAIL, "wrong exception: {}".format(type(exc)))
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
# --- end test_load_empty_file_raises_valueerror ---


# --- test_load_invalid_yaml_raises_valueerror ---
def test_load_invalid_yaml_raises_valueerror():
    """_load_yaml_file raises ValueError for a file with invalid YAML."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("key: [\n")
            tmp = fh.name
        _load_yaml_file(tmp)
        _report("load_yaml_file: invalid YAML raises ValueError",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "yaml parse error" in str(exc).lower():
            _report("load_yaml_file: invalid YAML raises ValueError", _PASS)
        else:
            _report("load_yaml_file: invalid YAML raises ValueError",
                    _FAIL, "wrong message: {}".format(exc))
    except Exception as exc:
        _report("load_yaml_file: invalid YAML raises ValueError",
                _FAIL, "wrong exception: {}".format(type(exc)))
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
# --- end test_load_invalid_yaml_raises_valueerror ---


# --- test_load_non_mapping_raises_valueerror ---
def test_load_non_mapping_raises_valueerror():
    """_load_yaml_file raises ValueError when file content is not a mapping."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("- item1\n- item2\n")
            tmp = fh.name
        _load_yaml_file(tmp)
        _report("load_yaml_file: non-mapping raises ValueError",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "mapping" in str(exc).lower():
            _report("load_yaml_file: non-mapping raises ValueError", _PASS)
        else:
            _report("load_yaml_file: non-mapping raises ValueError",
                    _FAIL, "wrong message: {}".format(exc))
    except Exception as exc:
        _report("load_yaml_file: non-mapping raises ValueError",
                _FAIL, "wrong exception: {}".format(type(exc)))
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
# --- end test_load_non_mapping_raises_valueerror ---


# =============================================================================
# Round 1 -- _merge_includes
# =============================================================================

# --- test_merge_includes_no_includes_key ---
def test_merge_includes_no_includes_key():
    """_merge_includes returns cfg unchanged when there is no includes key."""
    try:
        cfg = OmegaConf.create({"key": "value"})
        result = _merge_includes(cfg, _CONFIG_DIR)
        if result.key != "value":
            _report("merge_includes: no includes key leaves cfg unchanged",
                    _FAIL, "key value changed")
            return
        if "includes" in result:
            _report("merge_includes: no includes key leaves cfg unchanged",
                    _FAIL, "includes key present in result")
            return
        _report("merge_includes: no includes key leaves cfg unchanged", _PASS)
    except Exception as exc:
        _report("merge_includes: no includes key leaves cfg unchanged",
                _FAIL, "raised: {}".format(exc))
# --- end test_merge_includes_no_includes_key ---


# --- test_merge_includes_loads_subtree ---
def test_merge_includes_loads_subtree():
    """_merge_includes loads an included file as a named sub-tree."""
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp()
        included_path = os.path.join(tmp_dir, "database.yaml")
        with open(included_path, "w", encoding="utf-8") as fh:
            fh.write("tns_alias: mydb\n")

        cfg = OmegaConf.create({
            "includes": ["database.yaml"],
            "project": {"name": "test"},
        })
        result = _merge_includes(cfg, tmp_dir)

        if "includes" in result:
            _report("merge_includes: loads included file as sub-tree",
                    _FAIL, "includes key still present")
            return
        if result.project.name != "test":
            _report("merge_includes: loads included file as sub-tree",
                    _FAIL, "project.name not preserved")
            return
        if not hasattr(result, "database") or result.database.tns_alias != "mydb":
            _report("merge_includes: loads included file as sub-tree",
                    _FAIL, "database.tns_alias not found or wrong value")
            return
        _report("merge_includes: loads included file as sub-tree", _PASS)
    except Exception as exc:
        _report("merge_includes: loads included file as sub-tree",
                _FAIL, "raised: {}".format(exc))
    finally:
        if tmp_dir:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
# --- end test_merge_includes_loads_subtree ---


# --- test_merge_includes_removes_includes_key ---
def test_merge_includes_removes_includes_key():
    """_merge_includes removes the includes key from the result."""
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp()
        included_path = os.path.join(tmp_dir, "ingestion.yaml")
        with open(included_path, "w", encoding="utf-8") as fh:
            fh.write("batch_size: 500\n")

        cfg = OmegaConf.create({"includes": ["ingestion.yaml"]})
        result = _merge_includes(cfg, tmp_dir)

        if "includes" in result:
            _report("merge_includes: removes includes key",
                    _FAIL, "includes key still present in result")
            return
        _report("merge_includes: removes includes key", _PASS)
    except Exception as exc:
        _report("merge_includes: removes includes key",
                _FAIL, "raised: {}".format(exc))
    finally:
        if tmp_dir:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
# --- end test_merge_includes_removes_includes_key ---


# --- test_merge_includes_missing_file_raises_filenotfounderror ---
def test_merge_includes_missing_file_raises_filenotfounderror():
    """_merge_includes raises FileNotFoundError for a missing included file."""
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp()
        cfg = OmegaConf.create({"includes": ["nonexistent.yaml"]})
        _merge_includes(cfg, tmp_dir)
        _report("merge_includes: missing file raises FileNotFoundError",
                _FAIL, "no exception raised")
    except FileNotFoundError:
        _report("merge_includes: missing file raises FileNotFoundError", _PASS)
    except Exception as exc:
        _report("merge_includes: missing file raises FileNotFoundError",
                _FAIL, "wrong exception: {}".format(type(exc)))
    finally:
        if tmp_dir:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
# --- end test_merge_includes_missing_file_raises_filenotfounderror ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main():
    """Run all Round 1 test functions and print a summary."""
    print("=== test_config_loader_r1_py.py -- Round 1 ===")
    print("")

    print("-- _load_yaml_file --")
    test_load_valid_file_returns_dictconfig()
    test_load_missing_file_raises_filenotfounderror()
    test_load_empty_file_raises_valueerror()
    test_load_invalid_yaml_raises_valueerror()
    test_load_non_mapping_raises_valueerror()
    print("")

    print("-- _merge_includes --")
    test_merge_includes_no_includes_key()
    test_merge_includes_loads_subtree()
    test_merge_includes_removes_includes_key()
    test_merge_includes_missing_file_raises_filenotfounderror()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
