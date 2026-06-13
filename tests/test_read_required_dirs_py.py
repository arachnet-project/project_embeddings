# ARC_FILE: tests/test_read_required_dirs_py.py
# tests/test_read_required_dirs_py.py
# =============================================================================
# Arachnet Clinical Terminology Embeddings — read_required_dirs.py Test
# =============================================================================
# Purpose:
#   Tests for src/common/read_required_dirs.py.
#   Tests successful parsing, output format, and error handling for
#   missing file, invalid YAML, and missing/invalid keys.
#   Runs the script as a subprocess against temporary YAML files —
#   no dependency on the real config/directory_structure.yaml content,
#   except for one test that checks the real file is valid.
#
# Run with:
#   python tests/test_read_required_dirs_py.py
#
# Preconditions:
#   venv active with pyyaml installed.
#   src/common/read_required_dirs.py present.
#
# Author: Jan Mura
# Version: 1.0
# =============================================================================

import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "src" / "common" / "read_required_dirs.py"
REAL_CONFIG = PROJECT_ROOT / "config" / "directory_structure.yaml"

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

def _run_script(config_path):
    """Run read_required_dirs.py with PROJECT_ROOT temporarily faked.

    Since the script computes its own project root from __file__, we
    instead copy the script content approach: run it with a modified
    sys.path is not enough because _CONFIG_PATH is computed from
    __file__ location, not cwd. So for tests with custom YAML, we
    invoke the script's main() logic via a small wrapper that monkeypatches
    _CONFIG_PATH — done by running a short inline Python snippet.

    Parameters
    ----------
    config_path : Path or None
        Path to a YAML file to use as config. If None, runs the script
        unmodified against the real project config.

    Returns
    -------
    subprocess.CompletedProcess
        Result of running the script.
    """
    if config_path is None:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True, text=True,
        )

    # Run via inline snippet that patches _CONFIG_PATH before calling main()
    snippet = (
        "import sys, runpy\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, '{}')\n"
        "import importlib.util\n"
        "spec = importlib.util.spec_from_file_location('rrd', '{}')\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        "mod._CONFIG_PATH = Path('{}')\n"
        "mod.main()\n"
    ).format(
        str(SCRIPT_PATH.parent), str(SCRIPT_PATH), str(config_path)
    )
    return subprocess.run(
        [sys.executable, "-c", snippet],
        capture_output=True, text=True,
    )
# --- end _run_script ---


# =============================================================================
# Tests -- happy paths
# =============================================================================

# --- test_prints_each_directory_on_own_line ---
def test_prints_each_directory_on_own_line():
    """Script prints each required directory on its own line."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("required_directories:\n  - log\n  - wrk\n  - tests/results\n")
        config_path = Path(f.name)

    try:
        result = _run_script(config_path)
        lines = result.stdout.strip().splitlines()
        expected = ["log", "wrk", "tests/results"]
        if lines != expected:
            _report("prints each directory on own line",
                    _FAIL, "lines={!r} expected={!r}".format(lines, expected))
            return
        if result.returncode != 0:
            _report("prints each directory on own line",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        _report("prints each directory on own line", _PASS)
    finally:
        config_path.unlink()
# --- end test_prints_each_directory_on_own_line ---


# --- test_real_config_is_valid ---
def test_real_config_is_valid():
    """The real config/directory_structure.yaml parses successfully."""
    if not REAL_CONFIG.exists():
        _report("real config is valid",
                _FAIL, "file not found: {}".format(REAL_CONFIG))
        return
    result = _run_script(None)
    if result.returncode != 0:
        _report("real config is valid",
                _FAIL, "returncode={} stderr={}".format(
                    result.returncode, result.stderr.strip()))
        return
    lines = result.stdout.strip().splitlines()
    if len(lines) == 0:
        _report("real config is valid",
                _FAIL, "no directories printed")
        return
    _report("real config is valid", _PASS)
# --- end test_real_config_is_valid ---


# =============================================================================
# Tests -- failure paths
# =============================================================================

# --- test_missing_file_exits_1 ---
def test_missing_file_exits_1():
    """Script exits 1 with stderr message when YAML file does not exist."""
    missing_path = Path(tempfile.gettempdir()) / "does_not_exist_12345.yaml"
    if missing_path.exists():
        missing_path.unlink()

    result = _run_script(missing_path)
    if result.returncode != 1:
        _report("missing file exits 1",
                _FAIL, "returncode={}".format(result.returncode))
        return
    if "not found" not in result.stderr:
        _report("missing file exits 1",
                _FAIL, "stderr={!r}".format(result.stderr))
        return
    _report("missing file exits 1", _PASS)
# --- end test_missing_file_exits_1 ---


# --- test_invalid_yaml_exits_1 ---
def test_invalid_yaml_exits_1():
    """Script exits 1 with stderr message when YAML is malformed."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("required_directories: [unclosed\n")
        config_path = Path(f.name)

    try:
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("invalid yaml exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "failed to parse" not in result.stderr:
            _report("invalid yaml exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        _report("invalid yaml exits 1", _PASS)
    finally:
        config_path.unlink()
# --- end test_invalid_yaml_exits_1 ---


# --- test_missing_key_exits_1 ---
def test_missing_key_exits_1():
    """Script exits 1 with stderr message when required_directories key is absent."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("some_other_key:\n  - foo\n")
        config_path = Path(f.name)

    try:
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("missing key exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "required_directories" not in result.stderr:
            _report("missing key exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        _report("missing key exits 1", _PASS)
    finally:
        config_path.unlink()
# --- end test_missing_key_exits_1 ---


# --- test_non_list_value_exits_1 ---
def test_non_list_value_exits_1():
    """Script exits 1 with stderr message when required_directories is not a list."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("required_directories: not_a_list\n")
        config_path = Path(f.name)

    try:
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("non-list value exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not a list" not in result.stderr:
            _report("non-list value exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        _report("non-list value exits 1", _PASS)
    finally:
        config_path.unlink()
# --- end test_non_list_value_exits_1 ---


# --- test_empty_list_prints_nothing ---
def test_empty_list_prints_nothing():
    """Script exits 0 and prints nothing when required_directories is empty."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("required_directories: []\n")
        config_path = Path(f.name)

    try:
        result = _run_script(config_path)
        if result.returncode != 0:
            _report("empty list prints nothing",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if result.stdout.strip() != "":
            _report("empty list prints nothing",
                    _FAIL, "stdout={!r}".format(result.stdout))
            return
        _report("empty list prints nothing", _PASS)
    finally:
        config_path.unlink()
# --- end test_empty_list_prints_nothing ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all test functions and print a summary."""
    print("=== test_read_required_dirs_py.py ===")
    print("")

    print("-- happy paths --")
    test_prints_each_directory_on_own_line()
    test_real_config_is_valid()
    test_empty_list_prints_nothing()
    print("")

    print("-- failure paths --")
    test_missing_file_exits_1()
    test_invalid_yaml_exits_1()
    test_missing_key_exits_1()
    test_non_list_value_exits_1()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
