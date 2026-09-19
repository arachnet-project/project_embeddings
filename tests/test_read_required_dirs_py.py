# ARC_FILE: tests/test_read_required_dirs_py.py
# tests/test_read_required_dirs_py.py
# =============================================================================
# Arachnet Clinical Terminology Embeddings — read_required_dirs.py Test
# =============================================================================
# Purpose:
#   Tests for src/common/read_required_dirs.py (v2.0).
#   Tests successful parsing, output format, and error handling for
#   missing file, invalid YAML, non-mapping YAML, invalid UTF-8,
#   missing/invalid keys, non-string/empty/whitespace entries, unsafe
#   path components (leading "/", "..", ".", and empty components —
#   the exact class of component PurePosixPath was found to silently
#   normalize away, which motivated the v2.0 literal-string check),
#   embedded control characters, duplicate entries, and atomicity of
#   output on a later invalid entry.
#   Runs the script as a subprocess via its documented --config
#   option — no dependency on the real config/directory_structure.yaml
#   content, except for one test that checks the real file is valid.
#
# Run with:
#   python tests/test_read_required_dirs_py.py
#
# Preconditions:
#   venv active with pyyaml installed.
#   src/common/read_required_dirs.py present.
#
# Author: Jan Mura
# Version: 2.0
# Last modified: 2026-09-11
# =============================================================================

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

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
    """Run read_required_dirs.py, optionally against a custom config.

    Invokes the script exactly as it is documented to be invoked: with
    no arguments (real production config, its own resolved default),
    or with --config PATH (test isolation, per the script's own
    Usage). This does not touch the script's internals or any
    module-level attribute — it exercises the real, supported CLI
    surface only.

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
    args = [sys.executable, str(SCRIPT_PATH)]
    if config_path is not None:
        args += ["--config", str(config_path)]
    return subprocess.run(
        args,
        capture_output=True, text=True,
    )
# --- end _run_script ---


def _make_temp_config_dir():
    """Return a fresh, process-owned temporary directory for config
    fixtures.

    Using a directory obtained from tempfile.TemporaryDirectory (or
    mkdtemp) rather than a predictable, shared filename under the
    system temp dir avoids acting on a path another process or user
    might own — a fixed name like
    "<tmpdir>/does_not_exist_12345.yaml" is guessable and shared, so
    an existence check followed by unlink() on it is unsafe.

    Returns
    -------
    tempfile.TemporaryDirectory
        Caller is responsible for holding a reference and letting it
        clean itself up (e.g. via a `with` block), which removes the
        directory and everything under it — including any file that
        was never created — with no separate unlink() needed.
    """
    return tempfile.TemporaryDirectory()
# --- end _make_temp_config_dir ---


def _write_config(tmpdir, content):
    """Write YAML text content to a fresh file inside tmpdir and
    return its Path."""
    path = Path(tmpdir) / "directory_structure.yaml"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
# --- end _write_config ---


# =============================================================================
# Tests -- happy paths
# =============================================================================

# --- test_prints_each_directory_on_own_line ---
def test_prints_each_directory_on_own_line():
    """Script prints each required directory on its own line, with no
    stderr output on success."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir,
            "required_directories:\n  - log\n  - wrk\n  - tests/results\n",
        )
        result = _run_script(config_path)
        lines = result.stdout.splitlines()
        expected = ["log", "wrk", "tests/results"]
        if lines != expected:
            _report("prints each directory on own line",
                    _FAIL, "lines={!r} expected={!r}".format(lines, expected))
            return
        if result.returncode != 0:
            _report("prints each directory on own line",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if result.stderr != "":
            _report("prints each directory on own line",
                    _FAIL, "stderr={!r} expected empty".format(result.stderr))
            return
        _report("prints each directory on own line", _PASS)
# --- end test_prints_each_directory_on_own_line ---


# --- test_real_config_is_valid ---
def test_real_config_is_valid():
    """The real config/directory_structure.yaml parses successfully,
    prints at least one validated directory, and produces no stderr.

    This is a structural integration check. The configuration file
    remains the single source of truth for the exact required-
    directory set.
    """
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
    if result.stderr != "":
        _report("real config is valid",
                _FAIL, "stderr={!r} expected empty".format(result.stderr))
        return
    _report("real config is valid", _PASS)
# --- end test_real_config_is_valid ---


# =============================================================================
# Tests -- failure paths: file / parse level
# =============================================================================

# --- test_missing_file_exits_1 ---
def test_missing_file_exits_1():
    """Script exits 1 with stderr message, empty stdout, when the YAML
    file does not exist.

    Uses a path inside a freshly created, process-owned temporary
    directory that is never written to, rather than a predictable
    shared filename — see _make_temp_config_dir.
    """
    with _make_temp_config_dir() as tmpdir:
        missing_path = Path(tmpdir) / "does_not_exist.yaml"

        result = _run_script(missing_path)
        if result.returncode != 1:
            _report("missing file exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not found" not in result.stderr:
            _report("missing file exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("missing file exits 1",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("missing file exits 1", _PASS)
# --- end test_missing_file_exits_1 ---


# --- test_invalid_yaml_exits_1 ---
def test_invalid_yaml_exits_1():
    """Script exits 1 with stderr message, empty stdout, when YAML is
    malformed."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories: [unclosed\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("invalid yaml exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "failed to parse" not in result.stderr:
            _report("invalid yaml exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("invalid yaml exits 1",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("invalid yaml exits 1", _PASS)
# --- end test_invalid_yaml_exits_1 ---


# --- test_invalid_utf8_exits_1 ---
def test_invalid_utf8_exits_1():
    """Script exits 1 with stderr message, empty stdout, when the file
    contains a byte sequence that is not valid UTF-8.

    load_registry() explicitly catches UnicodeDecodeError; this
    exercises that branch directly, writing raw bytes rather than
    going through the text-mode _write_config helper.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = Path(tmpdir) / "directory_structure.yaml"
        with open(config_path, "wb") as f:
            f.write(b"required_directories:\n  - log\n\xff\xfe\n")

        result = _run_script(config_path)
        if result.returncode != 1:
            _report("invalid utf-8 exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "invalid UTF-8" not in result.stderr:
            _report("invalid utf-8 exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("invalid utf-8 exits 1",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("invalid utf-8 exits 1", _PASS)
# --- end test_invalid_utf8_exits_1 ---


# =============================================================================
# Tests -- failure paths: top-level shape
# =============================================================================

# --- test_missing_key_exits_1 ---
def test_missing_key_exits_1():
    """Script exits 1 with stderr message, empty stdout, when
    required_directories key is absent from a mapping document."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "some_other_key:\n  - foo\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("missing key exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "required_directories" not in result.stderr:
            _report("missing key exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("missing key exits 1",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("missing key exits 1", _PASS)
# --- end test_missing_key_exits_1 ---


# --- test_top_level_non_mapping_exits_1 ---
def test_top_level_non_mapping_exits_1():
    """Script exits 1 with stderr message, empty stdout, when the
    top-level YAML document is a list rather than a mapping.

    Hits the same "'required_directories' key not found" branch as
    test_missing_key_exits_1, but via isinstance(data, dict) failing
    outright rather than a dict missing the key — a distinct document
    shape worth covering directly.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "- log\n- wrk\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("top-level non-mapping exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "required_directories" not in result.stderr:
            _report("top-level non-mapping exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("top-level non-mapping exits 1",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("top-level non-mapping exits 1", _PASS)
# --- end test_top_level_non_mapping_exits_1 ---


# --- test_non_list_value_exits_1 ---
def test_non_list_value_exits_1():
    """Script exits 1 with stderr message, empty stdout, when
    required_directories is not a list."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories: not_a_list\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("non-list value exits 1",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "is not a non-empty list" not in result.stderr:
            _report("non-list value exits 1",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("non-list value exits 1",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("non-list value exits 1", _PASS)
# --- end test_non_list_value_exits_1 ---


# --- test_empty_list_rejected ---
def test_empty_list_rejected():
    """Script exits 1 with stderr message, empty stdout, when
    required_directories is an empty list.

    v2.0 treats an empty required-directories registry as invalid
    configuration (most likely a truncated or misconfigured file)
    rather than a degenerate "nothing required" state, matching
    read_required_modules.py's identical non-empty-list requirement.
    Confirmed with Jan as the intended behavior, not reverted.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories: []\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("empty list rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "is not a non-empty list" not in result.stderr:
            _report("empty list rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("empty list rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("empty list rejected", _PASS)
# --- end test_empty_list_rejected ---


# =============================================================================
# Tests -- failure paths: per-entry type/content checks
# =============================================================================

# --- test_non_string_entry_rejected ---
def test_non_string_entry_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    is not a string (e.g. a YAML integer)."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - 123\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("non-string entry rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "is not a string" not in result.stderr:
            _report("non-string entry rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("non-string entry rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("non-string entry rejected", _PASS)
# --- end test_non_string_entry_rejected ---


# --- test_empty_string_entry_rejected ---
def test_empty_string_entry_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    is an empty string."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, 'required_directories:\n  - ""\n'
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("empty string entry rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "is empty" not in result.stderr:
            _report("empty string entry rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("empty string entry rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("empty string entry rejected", _PASS)
# --- end test_empty_string_entry_rejected ---


# --- test_whitespace_entry_rejected ---
def test_whitespace_entry_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    has leading or trailing whitespace.

    Uses a double-quoted YAML scalar so the leading space is preserved
    by the parser rather than trimmed as part of a plain scalar.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, 'required_directories:\n  - " log"\n'
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("whitespace entry rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "leading or trailing whitespace" not in result.stderr:
            _report("whitespace entry rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("whitespace entry rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("whitespace entry rejected", _PASS)
# --- end test_whitespace_entry_rejected ---


# =============================================================================
# Tests -- failure paths: unsafe path components
# =============================================================================

# --- test_absolute_path_rejected ---
def test_absolute_path_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    is an absolute path."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - /etc/passwd\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("absolute path rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not a safe relative directory path" not in result.stderr:
            _report("absolute path rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("absolute path rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("absolute path rejected", _PASS)
# --- end test_absolute_path_rejected ---


# --- test_parent_traversal_rejected ---
def test_parent_traversal_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    contains a ".." path component."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - log\n  - ../escape\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("parent traversal rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not a safe relative directory path" not in result.stderr:
            _report("parent traversal rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("parent traversal rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("parent traversal rejected", _PASS)
# --- end test_parent_traversal_rejected ---


# --- test_dot_component_rejected ---
def test_dot_component_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    contains a "." path component embedded between real components.

    Protects the specific regression identified during v2.0 review:
    PurePosixPath("log/./archive") silently normalizes to
    PosixPath("log/archive"), which is why validation was corrected to
    split on the literal string instead.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - log/./archive\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("dot component rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not a safe relative directory path" not in result.stderr:
            _report("dot component rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("dot component rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("dot component rejected", _PASS)
# --- end test_dot_component_rejected ---


# --- test_double_slash_rejected ---
def test_double_slash_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    contains an empty path component from a repeated slash
    (e.g. "log//archive").

    Same PurePosixPath-normalization regression class as the "."
    case: PurePosixPath("log//archive") silently collapses to
    PosixPath("log/archive").
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - log//archive\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("double slash rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not a safe relative directory path" not in result.stderr:
            _report("double slash rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("double slash rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("double slash rejected", _PASS)
# --- end test_double_slash_rejected ---


# --- test_trailing_slash_rejected ---
def test_trailing_slash_rejected():
    """Script exits 1 with stderr message, empty stdout, when an entry
    has a trailing slash, producing an empty final path component
    (e.g. "log/").

    Same PurePosixPath-normalization regression class: PurePosixPath
    silently strips a trailing slash rather than treating it as an
    empty component to reject.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - log/\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("trailing slash rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "not a safe relative directory path" not in result.stderr:
            _report("trailing slash rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("trailing slash rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("trailing slash rejected", _PASS)
# --- end test_trailing_slash_rejected ---


# =============================================================================
# Tests -- failure paths: control characters and duplicates
# =============================================================================

# --- test_control_char_rejected ---
def test_control_char_rejected():
    """Script exits 1 with the control-character diagnostic, empty
    stdout, when an entry contains an embedded control character.

    The fixture is self-checked before the script is invoked: the YAML
    text is parsed independently with yaml.safe_load and the resulting
    string is asserted to actually contain a character below 0x20, so
    this test cannot pass merely because the YAML failed to parse (a
    distinct branch already covered by test_invalid_yaml_exits_1). A
    double-quoted YAML scalar with a \\n escape is used because plain
    block-style scalars cannot represent an embedded newline at all.
    """
    yaml_text = 'required_directories:\n  - "log\\nwrk"\n'

    # Self-check: confirm the fixture actually round-trips to a string
    # containing a real control character, independent of the script
    # under test. Reported as an ordinary FAIL through this suite's
    # own reporting framework -- not a bare assert -- so a fixture bug
    # shows up in the pass/fail summary like any other failure rather
    # than aborting the run.
    parsed = yaml.safe_load(yaml_text)
    entry = parsed["required_directories"][0]
    if not any(ord(ch) < 32 for ch in entry):
        _report(
            "control char rejected",
            _FAIL,
            "fixture contains no control character: {!r}".format(entry),
        )
        return

    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(tmpdir, yaml_text)
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("control char rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "contains a control character" not in result.stderr:
            _report("control char rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("control char rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("control char rejected", _PASS)
# --- end test_control_char_rejected ---


# --- test_duplicate_entry_rejected ---
def test_duplicate_entry_rejected():
    """Script exits 1 with stderr message, empty stdout, when the same
    directory entry appears twice."""
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir, "required_directories:\n  - log\n  - log\n"
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("duplicate entry rejected",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if "duplicate directory entry" not in result.stderr:
            _report("duplicate entry rejected",
                    _FAIL, "stderr={!r}".format(result.stderr))
            return
        if result.stdout != "":
            _report("duplicate entry rejected",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("duplicate entry rejected", _PASS)
# --- end test_duplicate_entry_rejected ---


# =============================================================================
# Tests -- output atomicity
# =============================================================================

# --- test_no_partial_output_on_later_invalid_entry ---
def test_no_partial_output_on_later_invalid_entry():
    """Script prints nothing at all -- not even the earlier valid
    entries -- when a later entry in the list is invalid.

    Protects validate_registry's documented guarantee that "the
    complete registry is validated before any entry is returned, so
    callers never receive a partially valid list": the two valid
    entries preceding the bad one must not leak onto stdout.
    """
    with _make_temp_config_dir() as tmpdir:
        config_path = _write_config(
            tmpdir,
            "required_directories:\n  - log\n  - wrk\n  - ../escape\n",
        )
        result = _run_script(config_path)
        if result.returncode != 1:
            _report("no partial output on later invalid entry",
                    _FAIL, "returncode={}".format(result.returncode))
            return
        if result.stdout != "":
            _report("no partial output on later invalid entry",
                    _FAIL, "stdout={!r} expected empty".format(result.stdout))
            return
        _report("no partial output on later invalid entry", _PASS)
# --- end test_no_partial_output_on_later_invalid_entry ---


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
    print("")

    print("-- file / parse level --")
    test_missing_file_exits_1()
    test_invalid_yaml_exits_1()
    test_invalid_utf8_exits_1()
    print("")

    print("-- top-level shape --")
    test_missing_key_exits_1()
    test_top_level_non_mapping_exits_1()
    test_non_list_value_exits_1()
    test_empty_list_rejected()
    print("")

    print("-- per-entry type/content checks --")
    test_non_string_entry_rejected()
    test_empty_string_entry_rejected()
    test_whitespace_entry_rejected()
    print("")

    print("-- unsafe path components --")
    test_absolute_path_rejected()
    test_parent_traversal_rejected()
    test_dot_component_rejected()
    test_double_slash_rejected()
    test_trailing_slash_rejected()
    print("")

    print("-- control characters and duplicates --")
    test_control_char_rejected()
    test_duplicate_entry_rejected()
    print("")

    print("-- output atomicity --")
    test_no_partial_output_on_later_invalid_entry()

    sys.exit(_summarise())
# --- end main ---


if __name__ == "__main__":
    main()
