# test_config_loader_py.py
# Partial test script for src/common/config_loader.py.
# Tests are added incrementally as functions are implemented.
# Run from the project root with the venv active.
#
# Usage:
#   python tests/test_config_loader_py.py
#
# Round 1 covers: _load_yaml_file, _merge_includes.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Last modified: 2026-04-06

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

# Ensure project root is on sys.path so src.common imports resolve correctly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from omegaconf import DictConfig

from src.common.config_loader import _load_yaml_file, _merge_includes, _CONFIG_DIR, _PROJECT_YAML
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


# ---------------------------------------------------------------------------
# Round 1 — _load_yaml_file and _merge_includes
# ---------------------------------------------------------------------------

# --- test_load_yaml_file_project ---
def test_load_yaml_file_project() -> None:
    """
    _load_yaml_file loads project.yaml and returns a DictConfig.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        if not isinstance(cfg, DictConfig):
            _report("load_yaml_file: project.yaml returns DictConfig",
                    _FAIL, "returned type: {}".format(type(cfg)))
            return
        _report("load_yaml_file: project.yaml returns DictConfig", _PASS)
    except Exception as e:
        _report("load_yaml_file: project.yaml returns DictConfig",
                _FAIL, "raised: {}".format(e))
# --- end test_load_yaml_file_project ---


# --- test_load_yaml_file_has_active_environment ---
def test_load_yaml_file_has_active_environment() -> None:
    """
    project.yaml loaded by _load_yaml_file contains active_environment key.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        if "active_environment" not in cfg:
            _report("load_yaml_file: active_environment present",
                    _FAIL, "key not found in loaded config")
            return
        _report("load_yaml_file: active_environment present", _PASS)
    except Exception as e:
        _report("load_yaml_file: active_environment present",
                _FAIL, "raised: {}".format(e))
# --- end test_load_yaml_file_has_active_environment ---


# --- test_load_yaml_file_has_includes ---
def test_load_yaml_file_has_includes() -> None:
    """
    project.yaml loaded by _load_yaml_file contains includes list.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        if "includes" not in cfg:
            _report("load_yaml_file: includes key present",
                    _FAIL, "key not found in loaded config")
            return
        _report("load_yaml_file: includes key present", _PASS)
    except Exception as e:
        _report("load_yaml_file: includes key present",
                _FAIL, "raised: {}".format(e))
# --- end test_load_yaml_file_has_includes ---


# --- test_load_yaml_file_missing_file ---
def test_load_yaml_file_missing_file() -> None:
    """
    _load_yaml_file raises SnomedConfigError for a nonexistent file.
    """
    fake_path = _CONFIG_DIR / "nonexistent_file.yaml"
    try:
        _load_yaml_file(fake_path)
        _report("load_yaml_file: missing file raises SnomedConfigError",
                _FAIL, "no exception raised")
    except SnomedConfigError:
        _report("load_yaml_file: missing file raises SnomedConfigError",
                _PASS)
    except Exception as e:
        _report("load_yaml_file: missing file raises SnomedConfigError",
                _FAIL, "wrong exception type: {}".format(type(e)))
# --- end test_load_yaml_file_missing_file ---


# --- test_load_yaml_file_bad_yaml ---
def test_load_yaml_file_bad_yaml() -> None:
    """
    _load_yaml_file raises SnomedConfigError for a malformed YAML file.
    Creates a temporary bad YAML file, tests, then removes it.
    """
    bad_file = _CONFIG_DIR / "_test_bad_yaml_temp.yaml"
    try:
        bad_file.write_text("key: [\nbad yaml: {unclosed", encoding="utf-8")
        try:
            _load_yaml_file(bad_file)
            _report("load_yaml_file: bad YAML raises SnomedConfigError",
                    _FAIL, "no exception raised")
        except SnomedConfigError:
            _report("load_yaml_file: bad YAML raises SnomedConfigError",
                    _PASS)
        except Exception as e:
            _report("load_yaml_file: bad YAML raises SnomedConfigError",
                    _FAIL, "wrong exception type: {}".format(type(e)))
    finally:
        if bad_file.exists():
            bad_file.unlink()
# --- end test_load_yaml_file_bad_yaml ---


# --- test_merge_includes_subtrees_present ---
def test_merge_includes_subtrees_present() -> None:
    """
    After _merge_includes, cfg contains cfg.database and cfg.ingestion.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        missing = []
        if "database" not in cfg:
            missing.append("cfg.database")
        if "ingestion" not in cfg:
            missing.append("cfg.ingestion")
        if missing:
            _report("merge_includes: subtrees present",
                    _FAIL, "missing: {}".format(", ".join(missing)))
            return
        _report("merge_includes: subtrees present", _PASS)
    except Exception as e:
        _report("merge_includes: subtrees present",
                _FAIL, "raised: {}".format(e))
# --- end test_merge_includes_subtrees_present ---


# --- test_merge_includes_database_has_tns_alias ---
def test_merge_includes_database_has_tns_alias() -> None:
    """
    After _merge_includes, cfg.database.tns_alias is present and non-empty.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        val = cfg.database.get("tns_alias")
        if not val:
            _report("merge_includes: cfg.database.tns_alias present",
                    _FAIL, "key absent or empty")
            return
        _report("merge_includes: cfg.database.tns_alias present", _PASS)
    except Exception as e:
        _report("merge_includes: cfg.database.tns_alias present",
                _FAIL, "raised: {}".format(e))
# --- end test_merge_includes_database_has_tns_alias ---


# --- test_merge_includes_ingestion_has_release ---
def test_merge_includes_ingestion_has_release() -> None:
    """
    After _merge_includes, cfg.ingestion.release is present.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        if "release" not in cfg.ingestion:
            _report("merge_includes: cfg.ingestion.release present",
                    _FAIL, "key not found")
            return
        _report("merge_includes: cfg.ingestion.release present", _PASS)
    except Exception as e:
        _report("merge_includes: cfg.ingestion.release present",
                _FAIL, "raised: {}".format(e))
# --- end test_merge_includes_ingestion_has_release ---


# --- test_merge_includes_project_keys_preserved ---
def test_merge_includes_project_keys_preserved() -> None:
    """
    After _merge_includes, original project.yaml keys are still present.
    Checks active_environment and project.name.
    """
    try:
        cfg = _load_yaml_file(_PROJECT_YAML)
        cfg = _merge_includes(cfg)
        missing = []
        if "active_environment" not in cfg:
            missing.append("active_environment")
        if "project" not in cfg or "name" not in cfg.project:
            missing.append("project.name")
        if missing:
            _report("merge_includes: project.yaml keys preserved",
                    _FAIL, "missing: {}".format(", ".join(missing)))
            return
        _report("merge_includes: project.yaml keys preserved", _PASS)
    except Exception as e:
        _report("merge_includes: project.yaml keys preserved",
                _FAIL, "raised: {}".format(e))
# --- end test_merge_includes_project_keys_preserved ---


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
def main() -> None:
    """
    Run all test functions in sequence and print a summary.
    """
    print("=== test_config_loader_py.py — Round 1 ===")
    print("")

    # Round 1 — _load_yaml_file
    print("--- _load_yaml_file ---")
    test_load_yaml_file_project()
    test_load_yaml_file_has_active_environment()
    test_load_yaml_file_has_includes()
    test_load_yaml_file_missing_file()
    test_load_yaml_file_bad_yaml()
    print("")

    # Round 1 — _merge_includes
    print("--- _merge_includes ---")
    test_merge_includes_subtrees_present()
    test_merge_includes_database_has_tns_alias()
    test_merge_includes_ingestion_has_release()
    test_merge_includes_project_keys_preserved()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
