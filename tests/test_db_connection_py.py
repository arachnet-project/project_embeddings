# ARC_FILE: tests/test_db_connection_py.py
# =============================================================================
# Arachnet Clinical Terminology Embeddings — DB Connection Test Orchestrator
# tests/test_db_connection_py.py
# =============================================================================
# Purpose:
#   Runs all db_connection test rounds in sequence and reports a combined
#   result. This is the definitive test record for Step 0.5.
#
#   Rounds:
#     Round 1 — _get_credentials
#     Round 2 — get_connection
#     Round 3 — open_connection
#     Round 4 — test_connection
#     Round 5 — execute_ddl
#     Round 6 — execute_batch
#     Round 7 — execute_query
#     Inline   — get_pool stub
#
#   Each round runs as a subprocess. A round is reported as PASS if its
#   process exits with code 0, FAIL otherwise. Output from each round
#   is printed in full.
#
# Run with:
#   python tests/test_db_connection_py.py
#
# Preconditions:
#   venv active with oracledb and omegaconf installed.
#   src/common/db_connection.py present.
#   src/common/exceptions.py present.
#   SNOMED_LOG_DIR set in environment.
#   All round test files present in tests/.
#
# Author: Jan Mura
# Version: 1.0
# =============================================================================

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Rounds to run
# ---------------------------------------------------------------------------

_ROUNDS = [
    ("Round 1", "tests/test_db_connection_r1_py.py"),
    ("Round 2", "tests/test_db_connection_r2_py.py"),
    ("Round 3", "tests/test_db_connection_r3_py.py"),
    ("Round 4", "tests/test_db_connection_r4_py.py"),
    ("Round 5", "tests/test_db_connection_r5_py.py"),
    ("Round 6", "tests/test_db_connection_r6_py.py"),
    ("Round 7", "tests/test_db_connection_r7_py.py"),
]

_PASS = "PASS"
_FAIL = "FAIL"


# ---------------------------------------------------------------------------
# Inline test — get_pool stub
# ---------------------------------------------------------------------------

# --- _test_get_pool_stub ---
def _test_get_pool_stub() -> str:
    """Verify get_pool raises NotImplementedError.

    Returns
    -------
    str
        _PASS or _FAIL.
    """
    from src.common.db_connection import get_pool
    from omegaconf import OmegaConf

    cfg = OmegaConf.create({
        "database": {
            "tns_alias": "ARADB",
            "snomed": {
                "user": "snomed",
                "password_env_var": "SNOMED_DB_PASSWORD",
            },
            "snomed_stage": {
                "user": "snomed_stage",
                "password_env_var": "SNOMED_STAGE_DB_PASSWORD",
            },
            "sys": {
                "user": "sys",
                "password_env_var": "SNOMED_SYS_DB_PASSWORD",
            },
        }
    })

    try:
        get_pool(cfg, "snomed")
        return _FAIL
    except NotImplementedError:
        return _PASS
    except Exception:
        return _FAIL
# --- end _test_get_pool_stub ---


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

# --- _run_round ---
def _run_round(label: str, path: str) -> bool:
    """Run a single test round as a subprocess.

    Parameters
    ----------
    label : str
        Human-readable round label for output.
    path : str
        Relative path to the test file from PROJECT_ROOT.

    Returns
    -------
    bool
        True if the round passed, False if it failed.
    """
    full_path = PROJECT_ROOT / path
    if not full_path.exists():
        print("{}: {} -- file not found: {}".format(_FAIL, label, path))
        return False

    print("--- {} --- {}".format(label, path))
    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=str(PROJECT_ROOT),
    )
    print("")
    return result.returncode == 0
# --- end _run_round ---


# --- main ---
def main() -> None:
    """Run all rounds and print a combined summary."""
    print("=" * 70)
    print("test_db_connection_py.py — Step 0.5 full test record")
    print("=" * 70)
    print("")

    round_results = []

    # Run each round as subprocess
    for label, path in _ROUNDS:
        passed = _run_round(label, path)
        round_results.append((label, passed))

    # Run inline get_pool test
    print("--- Inline --- get_pool stub")
    pool_result = _test_get_pool_stub()
    pool_passed = pool_result == _PASS
    print("{}: get_pool raises NotImplementedError".format(pool_result))
    print("")
    round_results.append(("get_pool stub", pool_passed))

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    total = len(round_results)
    failed = 0
    for label, passed in round_results:
        status = _PASS if passed else _FAIL
        if not passed:
            failed += 1
        print("{}: {}".format(status, label))

    print("")
    print("Rounds: {} passed, {} failed, {} total.".format(
        total - failed, failed, total))

    sys.exit(0 if failed == 0 else 1)
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
