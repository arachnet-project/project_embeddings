# ARC_FILE: tests/test_bootstrap_r1_sh.sh
# tests/test_bootstrap_r1_sh.sh
# Round 1 tests for scripts/bootstrap.sh — required directory check.
#
# Tests that bootstrap.sh:
#   - reports existing directories as OK
#   - creates missing directories
#   - exits 0 on success
#   - auto-detects PROJECT_ROOT when unset
#   - uses PROJECT_ROOT as override when set
#   - fails clearly if PROJECT_ROOT is set but does not exist
#   - prints usage with -h/--help
#   - checks python3 is available
#   - fails clearly if read_required_dirs.py is missing
#
# Runs against a temporary fake project tree — does not touch the
# real project directories.
#
# Usage:
#   bash tests/test_bootstrap_r1_sh.sh
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Last modified: 2026-06-08
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

# --- report ---
report() {
    # Print and record a single test result.
    # Args:
    #   $1 — test name
    #   $2 — PASS or FAIL
    #   $3 — optional detail (required on failure)
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

# --- make_fake_project ---
make_fake_project() {
    # Create a minimal fake project tree with config/directory_structure.yaml
    # and src/common/read_required_dirs.py copied from the real project.
    # Echoes the path to the fake project root.
    local fake_root
    fake_root=$(mktemp -d)

    mkdir -p "${fake_root}/config"
    mkdir -p "${fake_root}/src/common"
    mkdir -p "${fake_root}/scripts"

    cat > "${fake_root}/config/directory_structure.yaml" << 'YAML'
required_directories:
  - log
  - wrk
  - tests/results
  - sql/ddl/tables
YAML

    cp "${REAL_PROJECT_ROOT}/src/common/read_required_dirs.py" \
       "${fake_root}/src/common/read_required_dirs.py"

    cp "${BOOTSTRAP}" "${fake_root}/scripts/bootstrap.sh"

    echo "${fake_root}"
}
# --- end make_fake_project ---

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_creates_missing_directories ---
test_creates_missing_directories() {
    local fake_root
    fake_root=$(make_fake_project)

    local output
    output=$(PROJECT_ROOT="${fake_root}" bash "${fake_root}/scripts/bootstrap.sh" 2>&1) \
        || { report "creates missing directories" "${FAIL}" "exit code != 0"; rm -rf "${fake_root}"; return; }

    local all_created=true
    for dir in log wrk tests/results sql/ddl/tables; do
        if [[ ! -d "${fake_root}/${dir}" ]]; then
            all_created=false
        fi
    done

    if [[ "${all_created}" == "true" ]]; then
        report "creates missing directories" "${PASS}"
    else
        report "creates missing directories" "${FAIL}" "not all directories created"
    fi

    rm -rf "${fake_root}"
}
# --- end test_creates_missing_directories ---

# --- test_reports_existing_directories_as_ok ---
test_reports_existing_directories_as_ok() {
    local fake_root
    fake_root=$(make_fake_project)

    mkdir -p "${fake_root}/log" "${fake_root}/wrk" \
             "${fake_root}/tests/results" "${fake_root}/sql/ddl/tables"

    local output
    output=$(PROJECT_ROOT="${fake_root}" bash "${fake_root}/scripts/bootstrap.sh" 2>&1) \
        || { report "reports existing directories as OK" "${FAIL}" "exit code != 0"; rm -rf "${fake_root}"; return; }

    if echo "${output}" | grep -q "OK       log"; then
        report "reports existing directories as OK" "${PASS}"
    else
        report "reports existing directories as OK" "${FAIL}" "expected OK line not found"
    fi

    rm -rf "${fake_root}"
}
# --- end test_reports_existing_directories_as_ok ---

# --- test_exits_zero_on_success ---
test_exits_zero_on_success() {
    local fake_root
    fake_root=$(make_fake_project)

    local rc=0
    PROJECT_ROOT="${fake_root}" bash "${fake_root}/scripts/bootstrap.sh" > /dev/null 2>&1 || rc=$?

    if [[ "${rc}" -eq 0 ]]; then
        report "exits zero on success" "${PASS}"
    else
        report "exits zero on success" "${FAIL}" "exit code=${rc}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_exits_zero_on_success ---

# --- test_auto_detects_project_root_when_unset ---
test_auto_detects_project_root_when_unset() {
    local fake_root
    fake_root=$(make_fake_project)

    local rc=0
    local output
    output=$(env -u PROJECT_ROOT bash "${fake_root}/scripts/bootstrap.sh" 2>&1) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Auto-detected PROJECT_ROOT: ${fake_root}"; then
        report "auto-detects PROJECT_ROOT when unset" "${PASS}"
    else
        report "auto-detects PROJECT_ROOT when unset" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_auto_detects_project_root_when_unset ---

# --- test_override_used_when_project_root_set ---
test_override_used_when_project_root_set() {
    local fake_root
    fake_root=$(make_fake_project)

    local rc=0
    local output
    output=$(PROJECT_ROOT="${fake_root}" bash "${fake_root}/scripts/bootstrap.sh" 2>&1) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Using PROJECT_ROOT (override): ${fake_root}"; then
        report "override used when PROJECT_ROOT set" "${PASS}"
    else
        report "override used when PROJECT_ROOT set" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_override_used_when_project_root_set ---

# --- test_fails_when_project_root_does_not_exist ---
test_fails_when_project_root_does_not_exist() {
    local fake_root
    fake_root=$(make_fake_project)

    local bogus="/tmp/does_not_exist_bootstrap_test_12345"
    rm -rf "${bogus}"

    local rc=0
    local output
    output=$(PROJECT_ROOT="${bogus}" bash "${fake_root}/scripts/bootstrap.sh" 2>&1) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "PROJECT_ROOT does not exist"; then
        report "fails when PROJECT_ROOT does not exist" "${PASS}"
    else
        report "fails when PROJECT_ROOT does not exist" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_fails_when_project_root_does_not_exist ---

# --- test_help_flag_prints_usage ---
test_help_flag_prints_usage() {
    local fake_root
    fake_root=$(make_fake_project)

    local rc=0
    local output
    output=$(bash "${fake_root}/scripts/bootstrap.sh" --help 2>&1) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Usage: bash scripts/bootstrap.sh"; then
        report "help flag prints usage" "${PASS}"
    else
        report "help flag prints usage" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_help_flag_prints_usage ---

# --- test_checks_python3_available ---
test_checks_python3_available() {
    local fake_root
    fake_root=$(make_fake_project)

    local rc=0
    local output
    output=$(PROJECT_ROOT="${fake_root}" bash "${fake_root}/scripts/bootstrap.sh" 2>&1) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "Checking python3"; then
        report "checks python3 available" "${PASS}"
    else
        report "checks python3 available" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_checks_python3_available ---

# --- test_fails_when_helper_missing ---
test_fails_when_helper_missing() {
    local fake_root
    fake_root=$(make_fake_project)

    rm "${fake_root}/src/common/read_required_dirs.py"

    local rc=0
    local output
    output=$(PROJECT_ROOT="${fake_root}" bash "${fake_root}/scripts/bootstrap.sh" 2>&1) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "helper script not found"; then
        report "fails when helper script missing" "${PASS}"
    else
        report "fails when helper script missing" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_fails_when_helper_missing ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r1_sh.sh -- Round 1 (directories) ==="
    echo ""

    test_creates_missing_directories
    test_reports_existing_directories_as_ok
    test_exits_zero_on_success
    test_auto_detects_project_root_when_unset
    test_override_used_when_project_root_set
    test_fails_when_project_root_does_not_exist
    test_help_flag_prints_usage
    test_checks_python3_available
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
