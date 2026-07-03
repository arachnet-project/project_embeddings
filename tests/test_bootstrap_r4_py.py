# ARC_FILE: tests/test_bootstrap_r4_py.py
# tests/test_bootstrap_r4_py.py
# Round 4 — check_env_vars
#
# Tests for environment variable validation in scripts/bootstrap.sh.
# Covers always-required vars, OCI branch via TNS_ADMIN, accumulation
# of multiple missing vars, and Ubuntu/OCI distinction.
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
# Version: 1.0
# Last modified: 2026-07-02
# =============================================================================

import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = str(PROJECT_ROOT / "scripts" / "bootstrap.sh")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_results = []


def _run(env_overrides: dict) -> subprocess.CompletedProcess:
    """Run bootstrap.sh with a controlled environment.

    Starts from the current process environment, applies env_overrides
    on top (a value of None removes the key), and runs bootstrap.sh.

    Parameters
    ----------
    env_overrides : dict
        Keys to set or remove. None value means unset the variable.

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
        ["bash", BOOTSTRAP],
        env=env,
        capture_output=True,
        text=True,
    )


def _base_env() -> dict:
    """Return a minimal env dict that passes all checks before check_env_vars.

    Relies on the calling process already having: venv active, python3
    correct, modules installed. Sets only the vars that check_env_vars
    cares about, leaving the rest to the inherited environment.

    Returns
    -------
    dict
        Overrides to pass to _run.
    """
    return {
        "SNOMED_LOG_DIR": "/tmp/ace_test_logs",
        "SNOMED_LOG_LEVEL": "INFO",
        "TNS_ADMIN": None,
        "SNOMED_DB_PASSWORD": None,
        "SNOMED_STAGE_DB_PASSWORD": None,
        "SNOMED_SYS_DB_PASSWORD": None,
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_ubuntu_all_required_set ---
def test_ubuntu_all_required_set() -> None:
    """Ubuntu: always-required vars set, no TNS_ADMIN — passes."""
    result = _run(_base_env())
    if result.returncode == 0:
        _record("ubuntu_all_required_set", _PASS)
    else:
        _record("ubuntu_all_required_set", _FAIL, result.stderr.strip())
# --- end test_ubuntu_all_required_set ---


# --- test_ubuntu_db_passwords_not_checked ---
def test_ubuntu_db_passwords_not_checked() -> None:
    """Ubuntu: DB password vars absent but TNS_ADMIN unset — passes."""
    env = _base_env()
    # DB passwords absent and TNS_ADMIN unset: OCI branch must be skipped.
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


# --- test_oci_all_vars_set ---
def test_oci_all_vars_set() -> None:
    """OCI: TNS_ADMIN set, all DB password vars set — passes."""
    env = _base_env()
    env["TNS_ADMIN"] = "/opt/oracle/wallet"
    env["SNOMED_DB_PASSWORD"] = "secret1"
    env["SNOMED_STAGE_DB_PASSWORD"] = "secret2"
    env["SNOMED_SYS_DB_PASSWORD"] = "secret3"
    result = _run(env)
    if result.returncode == 0:
        _record("oci_all_vars_set", _PASS)
    else:
        _record("oci_all_vars_set", _FAIL, result.stderr.strip())
# --- end test_oci_all_vars_set ---


# --- test_oci_missing_db_password ---
def test_oci_missing_db_password() -> None:
    """OCI: SNOMED_DB_PASSWORD missing — fails, named in output."""
    env = _base_env()
    env["TNS_ADMIN"] = "/opt/oracle/wallet"
    env["SNOMED_STAGE_DB_PASSWORD"] = "secret2"
    env["SNOMED_SYS_DB_PASSWORD"] = "secret3"
    result = _run(env)
    if result.returncode != 0 and "SNOMED_DB_PASSWORD" in result.stderr:
        _record("oci_missing_db_password", _PASS)
    else:
        _record("oci_missing_db_password", _FAIL, result.stderr.strip())
# --- end test_oci_missing_db_password ---


# --- test_oci_missing_stage_db_password ---
def test_oci_missing_stage_db_password() -> None:
    """OCI: SNOMED_STAGE_DB_PASSWORD missing — fails, named in output."""
    env = _base_env()
    env["TNS_ADMIN"] = "/opt/oracle/wallet"
    env["SNOMED_DB_PASSWORD"] = "secret1"
    env["SNOMED_SYS_DB_PASSWORD"] = "secret3"
    result = _run(env)
    if result.returncode != 0 and "SNOMED_STAGE_DB_PASSWORD" in result.stderr:
        _record("oci_missing_stage_db_password", _PASS)
    else:
        _record("oci_missing_stage_db_password", _FAIL, result.stderr.strip())
# --- end test_oci_missing_stage_db_password ---


# --- test_oci_missing_sys_db_password ---
def test_oci_missing_sys_db_password() -> None:
    """OCI: SNOMED_SYS_DB_PASSWORD missing — fails, named in output."""
    env = _base_env()
    env["TNS_ADMIN"] = "/opt/oracle/wallet"
    env["SNOMED_DB_PASSWORD"] = "secret1"
    env["SNOMED_STAGE_DB_PASSWORD"] = "secret2"
    result = _run(env)
    if result.returncode != 0 and "SNOMED_SYS_DB_PASSWORD" in result.stderr:
        _record("oci_missing_sys_db_password", _PASS)
    else:
        _record("oci_missing_sys_db_password", _FAIL, result.stderr.strip())
# --- end test_oci_missing_sys_db_password ---


# --- test_oci_all_db_passwords_missing ---
def test_oci_all_db_passwords_missing() -> None:
    """OCI: all three DB password vars missing — fails, all three named."""
    env = _base_env()
    env["TNS_ADMIN"] = "/opt/oracle/wallet"
    result = _run(env)
    all_named = (
        "SNOMED_DB_PASSWORD" in result.stderr
        and "SNOMED_STAGE_DB_PASSWORD" in result.stderr
        and "SNOMED_SYS_DB_PASSWORD" in result.stderr
    )
    if result.returncode != 0 and all_named:
        _record("oci_all_db_passwords_missing", _PASS)
    else:
        _record("oci_all_db_passwords_missing", _FAIL, result.stderr.strip())
# --- end test_oci_all_db_passwords_missing ---


# --- test_oci_always_required_and_db_passwords_missing ---
def test_oci_always_required_and_db_passwords_missing() -> None:
    """OCI: always-required and DB password vars all missing — all named."""
    env = _base_env()
    env["TNS_ADMIN"] = "/opt/oracle/wallet"
    env["SNOMED_LOG_DIR"] = None
    env["SNOMED_LOG_LEVEL"] = None
    result = _run(env)
    all_named = (
        "SNOMED_LOG_DIR" in result.stderr
        and "SNOMED_LOG_LEVEL" in result.stderr
        and "SNOMED_DB_PASSWORD" in result.stderr
        and "SNOMED_STAGE_DB_PASSWORD" in result.stderr
        and "SNOMED_SYS_DB_PASSWORD" in result.stderr
    )
    if result.returncode != 0 and all_named:
        _record("oci_always_required_and_db_passwords_missing", _PASS)
    else:
        _record("oci_always_required_and_db_passwords_missing", _FAIL,
                result.stderr.strip())
# --- end test_oci_always_required_and_db_passwords_missing ---


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

# --- main ---
def main() -> None:
    """Run all Round 4 tests and report results."""
    print("Round 4 — check_env_vars")
    print("=" * 60)

    test_ubuntu_all_required_set()
    test_ubuntu_db_passwords_not_checked()
    test_missing_snomed_log_dir()
    test_missing_snomed_log_level()
    test_missing_both_always_required()
    test_oci_all_vars_set()
    test_oci_missing_db_password()
    test_oci_missing_stage_db_password()
    test_oci_missing_sys_db_password()
    test_oci_all_db_passwords_missing()
    test_oci_always_required_and_db_passwords_missing()

    print("=" * 60)
    passed = sum(1 for _, r in _results if r == _PASS)
    total = len(_results)
    print(f"Result: {passed}/{total} passed")

    if passed < total:
        sys.exit(1)
# --- end main ---


if __name__ == "__main__":
    main()
