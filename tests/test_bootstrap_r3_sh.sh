# ARC_FILE: tests/test_bootstrap_r3_sh.sh
# tests/test_bootstrap_r3_sh.sh
# Round 3 tests for scripts/bootstrap.sh — Python module check.
#
# Tests that bootstrap.sh:
#   - reports OK for all required modules when present
#   - reports MISSING for absent modules and accumulates all failures
#   - exits 1 listing all missing modules when any are absent
#   - shows pip install hint on failure
#
# All tests use REAL_PROJECT_ROOT as PROJECT_ROOT so the real venv is
# inside PROJECT_ROOT and check_venv/check_python3 pass. Failure cases
# inject a fake python3 via PATH that simulates missing modules while
# delegating sys.executable and everything else to the real python3.
#
# Usage:
#   bash tests/test_bootstrap_r3_sh.sh
#
# Preconditions:
#   venv active with oracledb, omegaconf, pyyaml installed.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.2
# Last modified: 2026-06-16
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REAL_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${REAL_PROJECT_ROOT}/scripts/bootstrap.sh"
REAL_PYTHON3="$(command -v python3)"

PASS="PASS"
FAIL="FAIL"
RESULTS_FILE="$(mktemp)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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

# --- make_fake_python3 ---
make_fake_python3() {
    # Create a fake python3 wrapper in a given directory.
    # Fails 'import MODULE' for the named module, delegates everything
    # else (including sys.executable) to the real python3.
    # Args:
    #   $1 — directory to place fake python3 in
    #   $2 — module name to fake as missing
    local bin_dir="$1"
    local missing_module="$2"

    cat > "${bin_dir}/python3" << PYSCRIPT
#!/bin/bash
# Fails import of ${missing_module}, delegates everything else.
if [[ "\$*" == *"import ${missing_module}"* ]]; then
    echo "ModuleNotFoundError: No module named '${missing_module}'" >&2
    exit 1
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${bin_dir}/python3"
}
# --- end make_fake_python3 ---

# --- run_bootstrap ---
run_bootstrap() {
    # Run bootstrap with real PROJECT_ROOT and venv.
    # Optional: prepend a directory to PATH for fake python3 injection.
    # Args:
    #   $1 — optional fake bin dir to prepend to PATH (or empty string)
    #   $@ — additional args passed to bootstrap
    local fake_bin="${1:-}"
    shift || true

    local path_prefix=""
    if [[ -n "${fake_bin}" ]]; then
        path_prefix="${fake_bin}:"
    fi

    PATH="${path_prefix}${PATH}" \
    VIRTUAL_ENV="${REAL_PROJECT_ROOT}/venv" \
    PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
    bash "${BOOTSTRAP}" "$@" 2>&1
}
# --- end run_bootstrap ---

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_all_modules_present_reports_ok ---
test_all_modules_present_reports_ok() {
    local rc=0
    local output
    output=$(run_bootstrap "") || rc=$?

    if [[ "${rc}" -eq 0 ]] \
        && echo "${output}" | grep -q "OK       oracledb" \
        && echo "${output}" | grep -q "OK       omegaconf" \
        && echo "${output}" | grep -q "OK       yaml"; then
        report "all modules present reports OK" "${PASS}"
    else
        report "all modules present reports OK" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_all_modules_present_reports_ok ---

# --- test_missing_module_reported_and_exits_1 ---
test_missing_module_reported_and_exits_1() {
    local fake_bin
    fake_bin=$(mktemp -d)
    make_fake_python3 "${fake_bin}" "oracledb"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "missing Python modules"; then
        report "missing module reported and exits 1" "${PASS}"
    else
        report "missing module reported and exits 1" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_module_reported_and_exits_1 ---

# --- test_all_missing_modules_accumulated ---
test_all_missing_modules_accumulated() {
    local fake_bin
    fake_bin=$(mktemp -d)

    cat > "${fake_bin}/python3" << PYSCRIPT
#!/bin/bash
# Fails all three module imports, delegates everything else.
if [[ "\$*" == *"import oracledb"* ]] \\
    || [[ "\$*" == *"import omegaconf"* ]] \\
    || [[ "\$*" == *"import yaml"* ]]; then
    echo "ModuleNotFoundError" >&2
    exit 1
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_bin}/python3"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "MISSING  oracledb" \
        && echo "${output}" | grep -q "MISSING  omegaconf" \
        && echo "${output}" | grep -q "MISSING  yaml"; then
        report "all missing modules accumulated before exit" "${PASS}"
    else
        report "all missing modules accumulated before exit" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_all_missing_modules_accumulated ---

# --- test_install_hint_shown_on_failure ---
test_install_hint_shown_on_failure() {
    local fake_bin
    fake_bin=$(mktemp -d)
    make_fake_python3 "${fake_bin}" "oracledb"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "pip install -r requirements.txt"; then
        report "install hint shown on failure" "${PASS}"
    else
        report "install hint shown on failure" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_install_hint_shown_on_failure ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r3_sh.sh -- Round 3 (Python modules) ==="
    echo ""

    test_all_modules_present_reports_ok
    test_missing_module_reported_and_exits_1
    test_all_missing_modules_accumulated
    test_install_hint_shown_on_failure

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
