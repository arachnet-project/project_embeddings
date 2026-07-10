# ARC_FILE: tests/test_bootstrap_r1_sh.sh
# tests/test_bootstrap_r1_sh.sh
# Round 1 tests for scripts/bootstrap.sh — required directory check.
#
# Tests that bootstrap.sh:
#   - reports existing directories as OK
#   - creates missing directories
#   - exits 0 on success
#   - fails clearly if PROJECT_ROOT is set but does not exist
#   - fails clearly if read_required_dirs.py is missing
#   - prints usage with -h/--help
#   - rejects unknown arguments
#   - auto-detects PROJECT_ROOT when unset
#   - uses PROJECT_ROOT as override when set
#
# Happy-path tests use REAL_PROJECT_ROOT as PROJECT_ROOT so the real
# venv is inside PROJECT_ROOT and all checks pass. A temporary
# directory_structure.yaml override is not possible without patching,
# so these tests accept that real project dirs are checked/created.
#
# Usage:
#   bash tests/test_bootstrap_r1_sh.sh
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.4
# Last modified: 2026-07-06
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REAL_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${REAL_PROJECT_ROOT}/scripts/bootstrap.sh"

PASS="PASS"
FAIL="FAIL"
RESULTS_FILE="$(mktemp)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# --- detect_venv_dir ---
detect_venv_dir() {
    # Find whichever immediate subdirectory of REAL_PROJECT_ROOT contains
    # bin/activate. Returns the path without trailing slash.
    # Exits 1 with a message if none found.
    local d
    for d in "${REAL_PROJECT_ROOT}"/*/; do
        [[ -f "${d}bin/activate" ]] && echo "${d%/}" && return 0
    done
    echo "bootstrap test: no venv found under ${REAL_PROJECT_ROOT}" >&2
    return 1
}
# --- end detect_venv_dir ---

REAL_VENV="$(detect_venv_dir)"

# --- report ---
report() {
    local name="$1"
    local result="$2"
    local detail="${3:-}"
    if [[ -n "${detail}" ]]; then
        echo "${result}: ${name} -- ${detail}"
    else
        echo "${result}: ${name}"
    fi
    echo "${result}" >> "${RESULTS_FILE}"
}
# --- end report ---

# --- run_bootstrap ---
run_bootstrap() {
    # Run bootstrap against REAL_PROJECT_ROOT with the real venv active.
    # Args:
    #   $@ — arguments passed to bootstrap
    VIRTUAL_ENV="${REAL_VENV}" \
    PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
    bash "${BOOTSTRAP}" "$@" 2>&1
}
# --- end run_bootstrap ---

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_exits_zero_on_success ---
test_exits_zero_on_success() {
    local rc=0
    run_bootstrap > /dev/null || rc=$?

    if [[ "${rc}" -eq 0 ]]; then
        report "exits zero on success" "${PASS}"
    else
        report "exits zero on success" "${FAIL}" "exit code=${rc}"
    fi
}
# --- end test_exits_zero_on_success ---

# --- test_reports_existing_directories_as_ok ---
test_reports_existing_directories_as_ok() {
    local rc=0
    local output
    output=$(run_bootstrap) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "OK       log"; then
        report "reports existing directories as OK" "${PASS}"
    else
        report "reports existing directories as OK" "${FAIL}" "rc=${rc}"
    fi
}
# --- end test_reports_existing_directories_as_ok ---

# --- test_creates_missing_directory ---
test_creates_missing_directory() {
    # Temporarily remove a required dir, run bootstrap, verify it recreates it.
    # Uses sql/ddl/tables — safe to remove temporarily, not used by test runner.
    # Restores .gitkeep after the test to keep the repo clean.
    local test_dir="${REAL_PROJECT_ROOT}/sql/ddl/tables"
    local gitkeep="${test_dir}/.gitkeep"
    local had_gitkeep=0
    [[ -f "${gitkeep}" ]] && had_gitkeep=1

    rm -rf "${test_dir}"

    local rc=0
    run_bootstrap > /dev/null || rc=$?

    local dir_exists=0
    [[ -d "${test_dir}" ]] && dir_exists=1

    # Restore .gitkeep if it existed before the test.
    if [[ "${had_gitkeep}" -eq 1 && "${dir_exists}" -eq 1 ]]; then
        touch "${gitkeep}"
    fi

    if [[ "${rc}" -eq 0 ]] && [[ "${dir_exists}" -eq 1 ]]; then
        report "creates missing directory" "${PASS}"
    else
        report "creates missing directory" "${FAIL}" "rc=${rc} dir_exists=${dir_exists}"
    fi
}
# --- end test_creates_missing_directory ---

# --- test_auto_detects_project_root_when_unset ---
test_auto_detects_project_root_when_unset() {
    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${REAL_VENV}" \
        env -u PROJECT_ROOT \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Auto-detected PROJECT_ROOT"; then
        report "auto-detects PROJECT_ROOT when unset" "${PASS}"
    else
        report "auto-detects PROJECT_ROOT when unset" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_auto_detects_project_root_when_unset ---

# --- test_override_used_when_project_root_set ---
test_override_used_when_project_root_set() {
    local rc=0
    local output
    output=$(run_bootstrap) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Using PROJECT_ROOT (override)"; then
        report "override used when PROJECT_ROOT set" "${PASS}"
    else
        report "override used when PROJECT_ROOT set" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_override_used_when_project_root_set ---

# --- test_fails_when_project_root_does_not_exist ---
test_fails_when_project_root_does_not_exist() {
    local bogus="/tmp/does_not_exist_bootstrap_test_12345"
    rm -rf "${bogus}"

    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${REAL_VENV}" \
        PROJECT_ROOT="${bogus}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "PROJECT_ROOT does not exist"; then
        report "fails when PROJECT_ROOT does not exist" "${PASS}"
    else
        report "fails when PROJECT_ROOT does not exist" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_project_root_does_not_exist ---

# --- test_help_flag_prints_usage ---
test_help_flag_prints_usage() {
    local rc=0
    local output
    output=$(run_bootstrap --help) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Usage: bash scripts/bootstrap.sh"; then
        report "help flag prints usage" "${PASS}"
    else
        report "help flag prints usage" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_help_flag_prints_usage ---

# --- test_unknown_argument_rejected ---
test_unknown_argument_rejected() {
    local rc=0
    local output
    output=$(run_bootstrap --unknown-flag 2>&1) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "unknown argument"; then
        report "unknown argument rejected" "${PASS}"
    else
        report "unknown argument rejected" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_unknown_argument_rejected ---

# --- test_fails_when_helper_missing ---
test_fails_when_helper_missing() {
    # Temporarily rename helper, run bootstrap, restore it.
    local helper="${REAL_PROJECT_ROOT}/src/common/read_required_dirs.py"
    local backup="${helper}.bak"

    mv "${helper}" "${backup}"

    local rc=0
    local output
    output=$(run_bootstrap 2>&1) || rc=$?

    mv "${backup}" "${helper}"

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "helper script not found"; then
        report "fails when helper script missing" "${PASS}"
    else
        report "fails when helper script missing" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_helper_missing ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r1_sh.sh -- Round 1 (directories) ==="
    echo ""

    test_exits_zero_on_success
    test_reports_existing_directories_as_ok
    test_creates_missing_directory
    test_auto_detects_project_root_when_unset
    test_override_used_when_project_root_set
    test_fails_when_project_root_does_not_exist
    test_help_flag_prints_usage
    test_unknown_argument_rejected
    test_fails_when_helper_missing

    echo ""
    local total passed failed
    total=$(wc -l < "${RESULTS_FILE}")
    passed=$(grep -c "${PASS}" "${RESULTS_FILE}" || true)
    failed=$(grep -c "${FAIL}" "${RESULTS_FILE}" || true)
    rm -f "${RESULTS_FILE}"

    echo "Results: ${passed} passed, ${failed} failed, ${total} total."

    if [[ "${failed}" -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}
# --- end main ---

main "$@"
