# =============================================================================
# Arachnet Clinical Embeddings — Config Loader Orchestrator Test
# tests/test_config_loader_py.py
# =============================================================================
# Purpose:
#   Runs all four round test modules for config_loader in sequence and prints
#   a combined summary. This is the single entry point for the full Step 0.4
#   test suite.
#
# Run with:
#   python tests/test_config_loader_py.py
#
# Preconditions:
#   venv active with omegaconf and pyyaml installed.
#   src/common/config_loader.py present.
#   config/project.yaml, config/database.yaml, config/ingestion.yaml present.
#   All four round test files present in tests/.
#
# Note on design:
#   Each round module's main() ends with sys.exit(), which would terminate
#   the process before subsequent rounds run. The orchestrator therefore
#   calls each test function directly rather than calling main(). Results
#   accumulate in each module's own _results list and are read back here
#   for the combined summary.
#
# Author: Jan Mura
# Version: 0.4.0
# =============================================================================

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Import round modules
# ---------------------------------------------------------------------------

import tests.test_config_loader_r1_py as round1
import tests.test_config_loader_r2_py as round2
import tests.test_config_loader_r3_py as round3
import tests.test_config_loader_r4_py as round4


# ---------------------------------------------------------------------------
# Orchestrator helpers
# ---------------------------------------------------------------------------

# --- _run_round ---
def _run_round(label: str, module, test_functions: list) -> None:
    """Run all test functions for one round module and print a section header.

    Each test function is called in the order given. Results are recorded in
    the module's own _results list. The orchestrator does not call the
    module's main() function because main() calls sys.exit() which would
    terminate the process before subsequent rounds run.

    Parameters
    ----------
    label : str
        Display label printed as a section header, e.g. "Round 1".
    module : module
        The imported round test module.
    test_functions : list
        List of callables to run, in order, drawn from the module.
    """
    print("=== {} ===".format(label))
    print("")

    for fn in test_functions:
        fn()

    total = len(module._results)
    failed = sum(1 for r, _ in module._results if r == module._FAIL)
    passed = total - failed
    print("")
    print("Round results: {} passed, {} failed, {} total.".format(
        passed, failed, total))
    print("")
# --- end _run_round ---


# --- _combined_summary ---
def _combined_summary(modules: list) -> int:
    """Collect results from all round modules and print a combined summary.

    Parameters
    ----------
    modules : list
        List of imported round test modules, each with a _results attribute
        and a _FAIL constant.

    Returns
    -------
    int
        0 if all tests across all rounds passed, 1 if any failed.
    """
    total = 0
    failed = 0

    for module in modules:
        for result, _ in module._results:
            total += 1
            if result == module._FAIL:
                failed += 1

    passed = total - failed

    print("=== Combined Results ===")
    print("")
    print("Results: {} passed, {} failed, {} total.".format(
        passed, failed, total))
    print("")

    return 0 if failed == 0 else 1
# --- end _combined_summary ---


# =============================================================================
# Main
# =============================================================================

# --- main ---
def main() -> None:
    """Run all four round test modules in sequence and print a combined summary."""
    print("=== test_config_loader_py.py -- Full Step 0.4 Test Suite ===")
    print("")

    # Round 1 -- _load_yaml_file and _merge_includes
    _run_round(
        "Round 1 -- _load_yaml_file and _merge_includes",
        round1,
        [
            round1.test_load_valid_file_returns_dictconfig,
            round1.test_load_missing_file_raises_filenotfounderror,
            round1.test_load_empty_file_raises_valueerror,
            round1.test_load_invalid_yaml_raises_valueerror,
            round1.test_load_non_mapping_raises_valueerror,
            round1.test_merge_includes_no_includes_key,
            round1.test_merge_includes_loads_subtree,
            round1.test_merge_includes_removes_includes_key,
            round1.test_merge_includes_missing_file_raises_filenotfounderror,
        ],
    )

    # Round 2 -- _resolve_paths, _walk_tree, _resolve_interpolation
    _run_round(
        "Round 2 -- _resolve_paths, _walk_tree, _resolve_interpolation",
        round2,
        [
            round2.test_resolve_paths_adds_shortcut,
            round2.test_resolve_paths_unknown_environment,
            round2.test_resolve_paths_no_environments_section,
            round2.test_resolve_paths_missing_paths_section,
            round2.test_walk_tree_flat_dict,
            round2.test_walk_tree_nested_dict,
            round2.test_walk_tree_empty_dict,
            round2.test_resolve_interpolation_plain_values,
            round2.test_resolve_interpolation_valid_reference,
        ],
    )

    # Round 3 -- _validate_mandatory_keys
    _run_round(
        "Round 3 -- _validate_mandatory_keys",
        round3,
        [
            round3.test_validate_all_keys_present,
            round3.test_validate_single_missing_key,
            round3.test_validate_multiple_missing_keys,
            round3.test_validate_null_value_treated_as_missing,
            round3.test_validate_error_message_format,
        ],
    )

    # Round 4 -- load_config and _export_to_shell
    _run_round(
        "Round 4 -- load_config and _export_to_shell",
        round4,
        [
            round4.test_load_config_returns_dictconfig,
            round4.test_load_config_has_paths_shortcut,
            round4.test_load_config_has_database,
            round4.test_load_config_has_ingestion,
            round4.test_load_config_missing_config_dir,
            round4.test_load_config_missing_mandatory_key,
            round4.test_export_to_shell_produces_output,
            round4.test_export_to_shell_key_format,
            round4.test_export_to_shell_skips_lists,
        ],
    )

    modules = [round1, round2, round3, round4]
    exit_code = _combined_summary(modules)
    sys.exit(exit_code)
# --- end main ---


if __name__ == "__main__":
    main()
# =============================================================================
# End of file
# =============================================================================
