# Arachnet Clinical Embeddings — Config Loader Test Round 4
# tests/test_config_loader_r4_py.py
# =============================================================================
# Purpose:
#   Round 4 tests for load_config and _export_to_shell.
#   Tests normal behaviour and all documented error paths.
#
# Run with:
#   python tests/test_config_loader_r4_py.py
#
# Preconditions:
#   venv active with omegaconf and pyyaml installed.
#   src/common/config_loader.py present.
#   config/project.yaml, config/database.yaml, config/ingestion.yaml present.
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
from src.common.config_loader import load_config, _export_to_shell

# Real config directory.
_CONFIG_DIR = str(PROJECT_ROOT / "config")

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


# =============================================================================
# Round 4 -- load_config
# =============================================================================

# --- test_load_config_returns_dictconfig ---
def test_load_config_returns_dictconfig() -> None:
    """load_config returns a DictConfig when called with real config files."""
    try:
        cfg = load_config(config_dir=_CONFIG_DIR)
        if not isinstance(cfg, DictConfig):
            _report("load_config: returns DictConfig",
                    _FAIL, "returned type: {}".format(type(cfg)))
            return
        _report("load_config: returns DictConfig", _PASS)
    except Exception as exc:
        _report("load_config: returns DictConfig",
                _FAIL, "raised: {}".format(exc))
# --- end test_load_config_returns_dictconfig ---


# --- test_load_config_has_paths_shortcut ---
def test_load_config_has_paths_shortcut() -> None:
    """load_config result has cfg.paths shortcut populated."""
    try:
        cfg = load_config(config_dir=_CONFIG_DIR)
        if not hasattr(cfg, "paths"):
            _report("load_config: cfg.paths shortcut present",
                    _FAIL, "paths not in cfg")
            return
        if cfg.paths.base is None:
            _report("load_config: cfg.paths shortcut present",
                    _FAIL, "paths.base is None")
            return
        _report("load_config: cfg.paths shortcut present", _PASS)
    except Exception as exc:
        _report("load_config: cfg.paths shortcut present",
                _FAIL, "raised: {}".format(exc))
# --- end test_load_config_has_paths_shortcut ---


# --- test_load_config_has_database ---
def test_load_config_has_database() -> None:
    """load_config result contains cfg.database sub-tree."""
    try:
        cfg = load_config(config_dir=_CONFIG_DIR)
        if "database" not in cfg:
            _report("load_config: cfg.database present",
                    _FAIL, "database not in cfg")
            return
        _report("load_config: cfg.database present", _PASS)
    except Exception as exc:
        _report("load_config: cfg.database present",
                _FAIL, "raised: {}".format(exc))
# --- end test_load_config_has_database ---


# --- test_load_config_has_ingestion ---
def test_load_config_has_ingestion() -> None:
    """load_config result contains cfg.ingestion sub-tree."""
    try:
        cfg = load_config(config_dir=_CONFIG_DIR)
        if "ingestion" not in cfg:
            _report("load_config: cfg.ingestion present",
                    _FAIL, "ingestion not in cfg")
            return
        _report("load_config: cfg.ingestion present", _PASS)
    except Exception as exc:
        _report("load_config: cfg.ingestion present",
                _FAIL, "raised: {}".format(exc))
# --- end test_load_config_has_ingestion ---


# --- test_load_config_missing_config_dir ---
def test_load_config_missing_config_dir() -> None:
    """load_config raises FileNotFoundError for a nonexistent config_dir."""
    try:
        load_config(config_dir="/nonexistent/config/dir")
        _report("load_config: missing config_dir raises FileNotFoundError",
                _FAIL, "no exception raised")
    except FileNotFoundError:
        _report("load_config: missing config_dir raises FileNotFoundError",
                _PASS)
    except Exception as exc:
        _report("load_config: missing config_dir raises FileNotFoundError",
                _FAIL, "wrong exception: {}".format(type(exc)))
# --- end test_load_config_missing_config_dir ---


# --- test_load_config_missing_mandatory_key ---
def test_load_config_missing_mandatory_key() -> None:
    """load_config raises ValueError when a mandatory key is missing."""
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp()

        # Write a minimal project.yaml with no includes and missing keys.
        project_yaml = os.path.join(tmp_dir, "project.yaml")
        with open(project_yaml, "w", encoding="utf-8") as fh:
            fh.write(
                "active_environment: dev\n"
                "project:\n"
                "  name: test\n"
                "environments:\n"
                "  dev:\n"
                "    paths:\n"
                "      base: /data\n"
                "      log: /data/log\n"
                "      data_volume: /data/volume\n"
                "      rf2: /data/rf2\n"
                "      parquet: /data/parquet\n"
            )

        load_config(config_dir=tmp_dir)
        _report("load_config: missing mandatory key raises ValueError",
                _FAIL, "no exception raised")
    except ValueError as exc:
        if "mandatory keys" in str(exc).lower():
            _report("load_config: missing mandatory key raises ValueError",
                    _PASS)
        else:
            _report("load_config: missing mandatory key raises ValueError",
                    _FAIL, "wrong message: {}".format(exc))
    except Exception as exc:
        _report("load_config: missing mandatory key raises ValueError",
                _FAIL, "wrong exception: {}".format(type(exc)))
    finally:
        if tmp_dir:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
# --- end test_load_config_missing_mandatory_key ---


# =============================================================================
# Round 4 -- _export_to_shell
# =============================================================================

# --- test_export_to_shell_produces_output ---
def test_export_to_shell_produces_output() -> None:
    """_export_to_shell prints at least one SNOMED_ variable to stdout."""
    try:
        cfg = load_config(config_dir=_CONFIG_DIR)

        # Capture stdout.
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            _export_to_shell(cfg)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        if not output:
            _report("export_to_shell: produces output",
                    _FAIL, "no output produced")
            return
        if "SNOMED_" not in output:
            _report("export_to_shell: produces output",
                    _FAIL, "SNOMED_ prefix not found in output")
            return
        _report("export_to_shell: produces output", _PASS)
    except Exception as exc:
        _report("export_to_shell: produces output",
                _FAIL, "raised: {}".format(exc))
# --- end test_export_to_shell_produces_output ---


# --- test_export_to_shell_key_format ---
def test_export_to_shell_key_format() -> None:
    """_export_to_shell output lines have KEY=value format."""
    try:
        cfg = OmegaConf.create({
            "database": {"tns_alias": "mydb"},
        })

        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            _export_to_shell(cfg)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        lines = [l for l in output.strip().splitlines() if l]
        for line in lines:
            if "=" not in line:
                _report("export_to_shell: output lines have KEY=value format",
                        _FAIL, "line missing equals sign: {}".format(line))
                return
            if not line.startswith("SNOMED_"):
                _report("export_to_shell: output lines have KEY=value format",
                        _FAIL, "line missing SNOMED_ prefix: {}".format(line))
                return
        _report("export_to_shell: output lines have KEY=value format", _PASS)
    except Exception as exc:
        _report("export_to_shell: output lines have KEY=value format",
                _FAIL, "raised: {}".format(exc))
# --- end test_export_to_shell_key_format ---


# --- test_export_to_shell_skips_lists ---
def test_export_to_shell_skips_lists() -> None:
    """_export_to_shell skips list values and warns to stderr."""
    try:
        cfg = OmegaConf.create({
            "database": {
                "tns_alias": "mydb",
                "tables": ["concept", "description"],
            },
        })

        import io
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            _export_to_shell(cfg)
            output = sys.stdout.getvalue()
            errors = sys.stderr.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        # tables list should not appear in stdout.
        if "SNOMED_DATABASE_TABLES" in output:
            _report("export_to_shell: skips list values",
                    _FAIL, "list value appeared in output")
            return
        # Warning should appear in stderr.
        if "WARNING" not in errors:
            _report("export_to_shell: skips list values",
                    _FAIL, "no warning in stderr")
            return
        _report("export_to_shell: skips list values", _PASS)
    except Exception as exc:
        _report("export_to_shell: skips list values",
                _FAIL, "raised: {}".format(exc))
# --- end test_export_to_shell_skips_lists ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all Round 4 test functions and print a summary."""
    print("=== test_config_loader_r4_py.py -- Round 4 ===")
    print("")

    print("-- load_config --")
    test_load_config_returns_dictconfig()
    test_load_config_has_paths_shortcut()
    test_load_config_has_database()
    test_load_config_has_ingestion()
    test_load_config_missing_config_dir()
    test_load_config_missing_mandatory_key()
    print("")

    print("-- _export_to_shell --")
    test_export_to_shell_produces_output()
    test_export_to_shell_key_format()
    test_export_to_shell_skips_lists()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
