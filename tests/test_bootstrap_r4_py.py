# ARC_FILE: tests/test_bootstrap_r4_py.py
# tests/test_bootstrap_r4_py.py
# Round 4 — check_env_vars and bootstrap mode selection
#
# Tests for environment variable validation and mode selection in
# scripts/bootstrap.sh. Covers always-required vars, accumulation of
# multiple missing vars, local mode being independent of TNS_ADMIN and
# of the application-schema passwords, and the command-line mode rules
# (docs/todo.md §2.2, D1 and its amendments).
#
# Revised in v1.4 for D1: bootstrap has exactly two modes, local
# (default) and real-db (--real-db), selected only by the command line.
# The v1.3 tests that asserted TNS_ADMIN selects an OCI/production mode
# or makes the application-schema passwords mandatory were replaced;
# v1.3 remains in Git history.
#
# SNOMED_SYS_DB_PASSWORD is deliberately NOT among the vars
# check_env_vars requires: the Phase 0/1 Oracle boundary (todo.md
# §3.5) forbids either bootstrap mode from requiring SYS/SYSDBA
# credentials. An earlier version of bootstrap.sh actively violated
# this by requiring SNOMED_SYS_DB_PASSWORD whenever TNS_ADMIN was set;
# that check was removed as part of the Step 0.6 revision.
# test_sys_db_password_not_required below is a regression guard
# for that removal, not a leftover from before it.
#
# TNS_ADMIN, when set by a test, points to a temporary directory
# created and removed by this file, never to a real wallet or Oracle
# configuration directory (dev_workflow.md §8).
#
# Run with:
#   python tests/test_bootstrap_r4_py.py
#
# Preconditions:
#   venv active.
#   scripts/bootstrap.sh present and executable.
#   PROJECT_ROOT set or auto-detectable.
#
# Author: Jan Mura
# Version: 1.4
# Last modified: 2026-11-28
# =============================================================================

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = str(PROJECT_ROOT / "scripts" / "bootstrap.sh")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REAL_DB_INTERIM_MESSAGE = (
    "bootstrap: --real-db is not implemented yet (Step 0.6, D2)."
)
USAGE_FIRST_LINE = "Usage: bash scripts/bootstrap.sh [--real-db] [-h|--help]"
OLD_MODE_LINE = "Mode: OCI/production"
APP_PASSWORD_VARS = ("SNOMED_DB_PASSWORD", "SNOMED_STAGE_DB_PASSWORD")
SENTINEL_DB_PASSWORD = "r4-sentinel-db-7f3a"
SENTINEL_STAGE_DB_PASSWORD = "r4-sentinel-stage-9c1e"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_results = []

# Temporary directory used as TNS_ADMIN; created and removed by main().
_tns_admin_dir = None


def _run(env_overrides: dict, args: list = None) -> subprocess.CompletedProcess:
    """Run bootstrap.sh with a controlled environment.

    Starts from the current process environment, applies env_overrides
    on top (a value of None removes the key), and runs bootstrap.sh
    with the given command-line arguments.

    Parameters
    ----------
    env_overrides : dict
        Keys to set or remove. None value means unset the variable.
    args : list, optional
        Command-line arguments for bootstrap.sh. Default: none.

    Returns
    -------
    subprocess.CompletedProcess
        Completed process with stdout, stderr, and returncode.
    """
    env = os.environ.copy()
    for key, value in env_overrides.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return subprocess.run(
        ["bash", BOOTSTRAP] + list(args or []),
        env=env,
        capture_output=True,
        text=True,
    )


def _base_env() -> dict:
    """Return a minimal env dict that passes all checks before check_env_vars.

    Relies on the calling process already having: venv active, python3
    correct, modules installed. Sets every var check_env_vars cares
    about explicitly -- including forcing SNOMED_SYS_DB_PASSWORD
    absent -- and pins PROJECT_ROOT to this repository, so results
    depend on this fixture rather than on whatever the caller's shell
    happens to have exported. Without the explicit PROJECT_ROOT
    override, an inherited value could point bootstrap at an unrelated
    directory and cause it to fail earlier (e.g. at check_venv) for
    reasons unrelated to what these tests exercise. Without explicitly
    unsetting SNOMED_SYS_DB_PASSWORD, an inherited value would silently
    defeat test_sys_db_password_not_required's whole purpose.
    BOOTSTRAP_MODE is also removed, so an inherited value cannot affect
    results (see test_mode_not_taken_from_environment).

    Returns
    -------
    dict
        Overrides to pass to _run.
    """
    return {
        "PROJECT_ROOT": str(PROJECT_ROOT),
        "SNOMED_LOG_DIR": "/tmp/ace_test_logs",
        "SNOMED_LOG_LEVEL": "INFO",
        "TNS_ADMIN": None,
        "SNOMED_DB_PASSWORD": None,
        "SNOMED_STAGE_DB_PASSWORD": None,
        "SNOMED_SYS_DB_PASSWORD": None,
        "BOOTSTRAP_MODE": None,
    }


def _record(name: str, result: str, detail: str = "") -> None:
    """Record and print a test result.

    Parameters
    ----------
    name : str
        Test name.
    result : str
        _PASS or _FAIL.
    detail : str, optional
        Additional context printed on failure.
    """
    _results.append((name, result))
    line = f"  {result:<6}  {name}"
    if detail:
        line += f"\n         {detail}"
    print(line)


# --- _detail ---
def _detail(result: subprocess.CompletedProcess) -> str:
    """Format a completed run for a failure diagnostic.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        Completed bootstrap run.

    Returns
    -------
    str
        Return code, stdout and stderr in one line.
    """
    return "returncode={} stdout={!r} stderr={!r}".format(
        result.returncode, result.stdout.strip(), result.stderr.strip()
    )
# --- end _detail ---


# --- _local_env_with_tns_admin ---
def _local_env_with_tns_admin() -> dict:
    """Return _base_env() with TNS_ADMIN set to the temporary directory.

    Returns
    -------
    dict
        Overrides to pass to _run.
    """
    env = _base_env()
    env["TNS_ADMIN"] = _tns_admin_dir
    return env
# --- end _local_env_with_tns_admin ---


# --- _is_local_pass ---
def _is_local_pass(result: subprocess.CompletedProcess) -> bool:
    """Return True if a run passed and reported local mode only.

    Requires exit 0, an exact "Mode: local" output line, and no
    "Mode: OCI/production" line in either output stream.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        Completed bootstrap run.

    Returns
    -------
    bool
        True if the run is a clean local-mode pass.
    """
    return (
        result.returncode == 0
        and "Mode: local" in result.stdout.splitlines()
        and OLD_MODE_LINE not in result.stdout
        and OLD_MODE_LINE not in result.stderr
    )
# --- end _is_local_pass ---


# --- _password_vars_mentioned ---
def _password_vars_mentioned(result: subprocess.CompletedProcess) -> list:
    """Return the application-schema password variables named in output.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        Completed bootstrap run.

    Returns
    -------
    list
        Names from APP_PASSWORD_VARS found in stdout or stderr.
    """
    output = result.stdout + result.stderr
    return [var for var in APP_PASSWORD_VARS if var in output]
# --- end _password_vars_mentioned ---


# --- _ran_no_checks ---
def _ran_no_checks(result: subprocess.CompletedProcess) -> bool:
    """Return True if a run printed no check progress and no summary.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        Completed bootstrap run.

    Returns
    -------
    bool
        True if neither stream contains check or summary output.
    """
    output = result.stdout + result.stderr
    markers = (
        "PROJECT_ROOT:",
        "Checking ",
        "=== Environment summary ===",
        "all checks passed",
    )
    return not any(marker in output for marker in markers)
# --- end _ran_no_checks ---


# ---------------------------------------------------------------------------
# Tests — environment variables, local mode
# ---------------------------------------------------------------------------

# --- test_ubuntu_all_required_set ---
def test_ubuntu_all_required_set() -> None:
    """Local mode: always-required vars set, no TNS_ADMIN — passes and
    reports local mode.

    Asserts the environment-summary mode line explicitly, not just
    the return code. Checked as an exact output line (not a substring
    of stdout), so an unrelated longer line containing this text could
    not satisfy the assertion. On failure, both stdout and stderr are
    included -- an incorrect summary is a stdout-content problem and
    normally leaves stderr empty, so a stderr-only diagnostic would not
    show what actually went wrong.
    """
    result = _run(_base_env())
    if result.returncode == 0 and "Mode: local" in result.stdout.splitlines():
        _record("ubuntu_all_required_set", _PASS)
    else:
        _record("ubuntu_all_required_set", _FAIL, _detail(result))
# --- end test_ubuntu_all_required_set ---


# --- test_ubuntu_db_passwords_not_checked ---
def test_ubuntu_db_passwords_not_checked() -> None:
    """Local mode: DB password vars absent, TNS_ADMIN unset — passes."""
    env = _base_env()
    # DB passwords absent and TNS_ADMIN unset.
    result = _run(env)
    if result.returncode == 0:
        _record("ubuntu_db_passwords_not_checked", _PASS)
    else:
        _record("ubuntu_db_passwords_not_checked", _FAIL, result.stderr.strip())
# --- end test_ubuntu_db_passwords_not_checked ---


# --- test_missing_snomed_log_dir ---
def test_missing_snomed_log_dir() -> None:
    """SNOMED_LOG_DIR unset — fails, named in output."""
    env = _base_env()
    env["SNOMED_LOG_DIR"] = None
    result = _run(env)
    if result.returncode != 0 and "SNOMED_LOG_DIR" in result.stderr:
        _record("missing_snomed_log_dir", _PASS)
    else:
        _record("missing_snomed_log_dir", _FAIL, result.stderr.strip())
# --- end test_missing_snomed_log_dir ---


# --- test_missing_snomed_log_level ---
def test_missing_snomed_log_level() -> None:
    """SNOMED_LOG_LEVEL unset — fails, named in output."""
    env = _base_env()
    env["SNOMED_LOG_LEVEL"] = None
    result = _run(env)
    if result.returncode != 0 and "SNOMED_LOG_LEVEL" in result.stderr:
        _record("missing_snomed_log_level", _PASS)
    else:
        _record("missing_snomed_log_level", _FAIL, result.stderr.strip())
# --- end test_missing_snomed_log_level ---


# --- test_missing_both_always_required ---
def test_missing_both_always_required() -> None:
    """Both always-required vars unset — fails, both named (accumulation)."""
    env = _base_env()
    env["SNOMED_LOG_DIR"] = None
    env["SNOMED_LOG_LEVEL"] = None
    result = _run(env)
    both_named = (
        "SNOMED_LOG_DIR" in result.stderr
        and "SNOMED_LOG_LEVEL" in result.stderr
    )
    if result.returncode != 0 and both_named:
        _record("missing_both_always_required", _PASS)
    else:
        _record("missing_both_always_required", _FAIL, result.stderr.strip())
# --- end test_missing_both_always_required ---


# --- test_local_tns_admin_set_no_passwords ---
def test_local_tns_admin_set_no_passwords() -> None:
    """Local mode: TNS_ADMIN set, both application passwords absent —
    passes, reports local mode, and asks for no password.

    The central D1 guard (replaces v1.3's OCI missing-password tests):
    the Step 0.6 specification forbids local mode from requiring
    application-schema passwords, and TNS_ADMIN must not change what
    local mode checks.
    """
    result = _run(_local_env_with_tns_admin())
    mentioned = _password_vars_mentioned(result)
    if _is_local_pass(result) and not mentioned:
        _record("local_tns_admin_set_no_passwords", _PASS)
    else:
        detail = "password vars mentioned={} {}".format(
            mentioned, _detail(result)
        )
        _record("local_tns_admin_set_no_passwords", _FAIL, detail)
# --- end test_local_tns_admin_set_no_passwords ---


# --- test_local_tns_admin_and_passwords_set ---
def test_local_tns_admin_and_passwords_set() -> None:
    """Local mode: TNS_ADMIN and both application passwords set —
    passes, reports local mode, and never echoes a password value.

    Replaces v1.3's test_oci_all_vars_set, which expected
    "Mode: OCI/production" for this environment.
    """
    env = _local_env_with_tns_admin()
    env["SNOMED_DB_PASSWORD"] = SENTINEL_DB_PASSWORD
    env["SNOMED_STAGE_DB_PASSWORD"] = SENTINEL_STAGE_DB_PASSWORD
    result = _run(env)
    output = result.stdout + result.stderr
    leaked = [
        value for value in (SENTINEL_DB_PASSWORD, SENTINEL_STAGE_DB_PASSWORD)
        if value in output
    ]
    if _is_local_pass(result) and not leaked:
        _record("local_tns_admin_and_passwords_set", _PASS)
    else:
        detail = "password values in output={} {}".format(
            bool(leaked), _detail(result)
        )
        _record("local_tns_admin_and_passwords_set", _FAIL, detail)
# --- end test_local_tns_admin_and_passwords_set ---


# --- test_local_tns_admin_set_log_vars_missing ---
def test_local_tns_admin_set_log_vars_missing() -> None:
    """Local mode: TNS_ADMIN set, both always-required vars missing —
    fails, names both, and names no password variable.

    Replaces v1.3's test_oci_always_required_and_db_passwords_missing,
    which expected the password variables to be reported as missing.
    """
    env = _local_env_with_tns_admin()
    env["SNOMED_LOG_DIR"] = None
    env["SNOMED_LOG_LEVEL"] = None
    result = _run(env)
    both_named = (
        "SNOMED_LOG_DIR" in result.stderr
        and "SNOMED_LOG_LEVEL" in result.stderr
    )
    mentioned = _password_vars_mentioned(result)
    if result.returncode != 0 and both_named and not mentioned:
        _record("local_tns_admin_set_log_vars_missing", _PASS)
    else:
        detail = "password vars mentioned={} {}".format(
            mentioned, _detail(result)
        )
        _record("local_tns_admin_set_log_vars_missing", _FAIL, detail)
# --- end test_local_tns_admin_set_log_vars_missing ---


# --- test_sys_db_password_not_required ---
def test_sys_db_password_not_required() -> None:
    """TNS_ADMIN set, SNOMED_SYS_DB_PASSWORD absent — still passes and
    never names SNOMED_SYS_DB_PASSWORD.

    Regression guard for the Phase 0/1 Oracle boundary (todo.md §3.5):
    neither bootstrap mode may require SYS/SYSDBA credentials. An
    earlier version of bootstrap.sh violated this by requiring
    SNOMED_SYS_DB_PASSWORD whenever TNS_ADMIN was set; this test fails
    if that requirement is ever reintroduced. Renamed from v1.3's
    test_oci_sys_db_password_not_required, since TNS_ADMIN no longer
    selects an OCI mode; TNS_ADMIN and both application passwords are
    still set, as in v1.3, so the guard covers the environment in
    which the violation originally occurred and can fail only because
    of SNOMED_SYS_DB_PASSWORD.
    """
    env = _local_env_with_tns_admin()
    env["SNOMED_DB_PASSWORD"] = SENTINEL_DB_PASSWORD
    env["SNOMED_STAGE_DB_PASSWORD"] = SENTINEL_STAGE_DB_PASSWORD
    # SNOMED_SYS_DB_PASSWORD is explicitly forced absent by
    # _base_env() (not merely assumed absent from the caller's shell)
    # -- that guarantee is what makes this test meaningful.
    result = _run(env)
    output = result.stdout + result.stderr
    if result.returncode == 0 and "SNOMED_SYS_DB_PASSWORD" not in output:
        _record("sys_db_password_not_required", _PASS)
    else:
        _record("sys_db_password_not_required", _FAIL, _detail(result))
# --- end test_sys_db_password_not_required ---


# --- test_mode_not_taken_from_environment ---
def test_mode_not_taken_from_environment() -> None:
    """BOOTSTRAP_MODE=real-db inherited from the environment, no
    arguments — still runs and reports local mode.

    Guards D1's rule that only the command line selects the mode.
    """
    env = _base_env()
    env["BOOTSTRAP_MODE"] = "real-db"
    result = _run(env)
    if _is_local_pass(result):
        _record("mode_not_taken_from_environment", _PASS)
    else:
        _record("mode_not_taken_from_environment", _FAIL, _detail(result))
# --- end test_mode_not_taken_from_environment ---


# ---------------------------------------------------------------------------
# Tests — command-line mode selection
# ---------------------------------------------------------------------------

# --- test_help_options ---
def test_help_options() -> None:
    """-h and --help — exit 0, usage on stdout, empty stderr, no checks."""
    failures = []
    for option in ("-h", "--help"):
        result = _run(_base_env(), [option])
        lines = result.stdout.splitlines()
        ok = (
            result.returncode == 0
            and bool(lines)
            and lines[0] == USAGE_FIRST_LINE
            and result.stderr == ""
            and _ran_no_checks(result)
        )
        if not ok:
            failures.append("{}: {}".format(option, _detail(result)))
    if not failures:
        _record("help_options", _PASS)
    else:
        _record("help_options", _FAIL, " | ".join(failures))
# --- end test_help_options ---


# --- test_help_takes_precedence ---
def test_help_takes_precedence() -> None:
    """Help together with other arguments — exit 0, usage on stdout,
    no checks (D1 amendment 7).

    Covers --real-db before and after --help, a repeated --real-db, and
    an unknown argument before --help.
    """
    cases = (
        ["--real-db", "--help"],
        ["--help", "--real-db"],
        ["--real-db", "--real-db", "-h"],
        ["--bogus", "--help"],
    )
    failures = []
    for args in cases:
        result = _run(_base_env(), args)
        lines = result.stdout.splitlines()
        ok = (
            result.returncode == 0
            and bool(lines)
            and lines[0] == USAGE_FIRST_LINE
            and result.stderr == ""
            and _ran_no_checks(result)
        )
        if not ok:
            failures.append("{}: {}".format(" ".join(args), _detail(result)))
    if not failures:
        _record("help_takes_precedence", _PASS)
    else:
        _record("help_takes_precedence", _FAIL, " | ".join(failures))
# --- end test_help_takes_precedence ---


# --- test_real_db_interim_failure ---
def test_real_db_interim_failure() -> None:
    """--real-db before D2 — exit 1, exactly the interim message on
    stderr, nothing on stdout, no checks and no summary (D1 amendment 3).

    Run with TNS_ADMIN and both application passwords set, so a
    rejection cannot be explained by a missing real-db prerequisite.
    """
    env = _local_env_with_tns_admin()
    env["SNOMED_DB_PASSWORD"] = SENTINEL_DB_PASSWORD
    env["SNOMED_STAGE_DB_PASSWORD"] = SENTINEL_STAGE_DB_PASSWORD
    result = _run(env, ["--real-db"])
    ok = (
        result.returncode == 1
        and result.stdout == ""
        and result.stderr.strip() == REAL_DB_INTERIM_MESSAGE
        and _ran_no_checks(result)
    )
    if ok:
        _record("real_db_interim_failure", _PASS)
    else:
        _record("real_db_interim_failure", _FAIL, _detail(result))
# --- end test_real_db_interim_failure ---


# --- test_real_db_repeated ---
def test_real_db_repeated() -> None:
    """--real-db given twice — exit 1, usage on stderr, nothing on
    stdout, no checks (D1 amendment 7)."""
    result = _run(_base_env(), ["--real-db", "--real-db"])
    ok = (
        result.returncode == 1
        and result.stdout == ""
        and "more than once" in result.stderr
        and USAGE_FIRST_LINE in result.stderr.splitlines()
        and _ran_no_checks(result)
    )
    if ok:
        _record("real_db_repeated", _PASS)
    else:
        _record("real_db_repeated", _FAIL, _detail(result))
# --- end test_real_db_repeated ---


# --- test_unknown_argument ---
def test_unknown_argument() -> None:
    """Unknown arguments — exit 1, argument named, usage on stderr,
    nothing on stdout, no checks (D1 amendment 2).

    Covers "realdb" without the leading dashes, an unknown option, and
    an unknown argument together with --real-db.
    """
    cases = (
        (["realdb"], "realdb"),
        (["--bogus"], "--bogus"),
        (["--real-db", "--bogus"], "--bogus"),
    )
    failures = []
    for args, named in cases:
        result = _run(_base_env(), args)
        ok = (
            result.returncode == 1
            and result.stdout == ""
            and "bootstrap: unknown argument: {}".format(named)
            in result.stderr.splitlines()
            and USAGE_FIRST_LINE in result.stderr.splitlines()
            and _ran_no_checks(result)
        )
        if not ok:
            failures.append("{}: {}".format(" ".join(args), _detail(result)))
    if not failures:
        _record("unknown_argument", _PASS)
    else:
        _record("unknown_argument", _FAIL, " | ".join(failures))
# --- end test_unknown_argument ---


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

# --- main ---
def main() -> None:
    """Run all Round 4 tests and report results."""
    global _tns_admin_dir

    print("Round 4 — check_env_vars and bootstrap mode selection")
    print("=" * 60)

    _tns_admin_dir = tempfile.mkdtemp(prefix="ace_r4_tns_admin_")
    try:
        test_ubuntu_all_required_set()
        test_ubuntu_db_passwords_not_checked()
        test_missing_snomed_log_dir()
        test_missing_snomed_log_level()
        test_missing_both_always_required()
        test_local_tns_admin_set_no_passwords()
        test_local_tns_admin_and_passwords_set()
        test_local_tns_admin_set_log_vars_missing()
        test_sys_db_password_not_required()
        test_mode_not_taken_from_environment()
        test_help_options()
        test_help_takes_precedence()
        test_real_db_interim_failure()
        test_real_db_repeated()
        test_unknown_argument()
    finally:
        shutil.rmtree(_tns_admin_dir, ignore_errors=True)

    print("=" * 60)
    passed = sum(1 for _, r in _results if r == _PASS)
    total = len(_results)
    print(f"Result: {passed}/{total} passed")

    if passed < total:
        sys.exit(1)
# --- end main ---


if __name__ == "__main__":
    main()
