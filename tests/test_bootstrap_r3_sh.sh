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
# inside PROJECT_ROOT and check_venv/check_python3 pass.
#
# Failure cases use a synthetic fake venv in REAL_PROJECT_ROOT that
# mirrors enough of the real venv structure to pass check_venv and
# check_python3 (bin/activate present, bin/python3 a fake script that
# reports its own path as sys.executable so PYTHON gets set to the
# fake). The fake python3 delegates real module imports to the real
# interpreter, but fails the target import. This technique is required
# because v1.7 bootstrap sets script-scoped PYTHON via sys.executable
# rather than invoking python3 by PATH name — so PATH-prefix injection
# alone is insufficient after check_python3 completes. The fake
# venv's bin/ must also be prepended to PATH so check_python3's
# `command -v python3` resolves to the fake, not the real interpreter.
#
# Usage:
#   bash tests/test_bootstrap_r3_sh.sh
#
# Preconditions:
#   venv active with oracledb, omegaconf, pyyaml installed.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.4
# Last modified: 2026-07-08
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

# --- make_fake_venv ---
make_fake_venv() {
    # Build a minimal synthetic venv inside REAL_PROJECT_ROOT so that
    # check_venv and check_python3 both pass, while the fake python3
    # simulates a missing module.
    #
    # The fake venv must live inside REAL_PROJECT_ROOT so check_venv's
    # path-prefix check passes. The fake python3 must report its own
    # absolute path as sys.executable so check_python3 sets PYTHON to
    # the fake script rather than the real interpreter. The fake then
    # delegates all calls to REAL_PYTHON3 except the target import.
    #
    # Args:
    #   $1 — name of the missing module to simulate
    #
    # Prints the fake venv directory path to stdout.
    local missing_module="$1"

    local fake_venv
    fake_venv="$(mktemp -d "${REAL_PROJECT_ROOT}/.fake_venv_test_XXXXXX")"

    mkdir -p "${fake_venv}/bin"

    # Minimal activate script so check_venv's bin/activate check passes.
    touch "${fake_venv}/bin/activate"

    local fake_python="${fake_venv}/bin/python3"

    cat > "${fake_python}" << PYSCRIPT
#!/bin/bash
# Synthetic fake python3 for Round 3 module-check tests.
# Reports own path as sys.executable so bootstrap's PYTHON variable
# is set to this script. Fails the target import; delegates all else
# to the real interpreter.
if [[ "\$*" == *"print(sys.executable)"* ]]; then
    echo "${fake_python}"
    exit 0
fi
if [[ "\$*" == *"import ${missing_module}"* ]]; then
    echo "ModuleNotFoundError: No module named '${missing_module}'" >&2
    exit 1
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_python}"

    echo "${fake_venv}"
}
# --- end make_fake_venv ---

# --- make_fake_venv_all_missing ---
make_fake_venv_all_missing() {
    # Variant of make_fake_venv that fails all three required module
    # imports: oracledb, omegaconf, yaml.
    #
    # Prints the fake venv directory path to stdout.
    local fake_venv
    fake_venv="$(mktemp -d "${REAL_PROJECT_ROOT}/.fake_venv_test_XXXXXX")"

    mkdir -p "${fake_venv}/bin"
    touch "${fake_venv}/bin/activate"

    local fake_python="${fake_venv}/bin/python3"

    cat > "${fake_python}" << PYSCRIPT
#!/bin/bash
# Fails all three required module imports, delegates everything else.
if [[ "\$*" == *"print(sys.executable)"* ]]; then
    echo "${fake_python}"
    exit 0
fi
if [[ "\$*" == *"import oracledb"* ]] \
    || [[ "\$*" == *"import omegaconf"* ]] \
    || [[ "\$*" == *"import yaml"* ]]; then
    echo "ModuleNotFoundError" >&2
    exit 1
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_python}"

    echo "${fake_venv}"
}
# --- end make_fake_venv_all_missing ---

# --- run_bootstrap ---
run_bootstrap() {
    # Run bootstrap with the given VIRTUAL_ENV and real PROJECT_ROOT.
    # Prepends the venv's bin/ onto PATH so check_python3's
    # `command -v python3` resolves to this venv's python3 (real or
    # fake) rather than whatever venv is already active in the
    # inherited shell PATH.
    # Args:
    #   $1 — VIRTUAL_ENV path to use (real or fake venv)
    local venv="$1"

    PATH="${venv}/bin:${PATH}" \
    VIRTUAL_ENV="${venv}" \
    PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
    bash "${BOOTSTRAP}" 2>&1
}
# --- end run_bootstrap ---

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_all_modules_present_reports_ok ---
test_all_modules_present_reports_ok() {
    local rc=0
    local output
    output=$(run_bootstrap "${REAL_VENV}") || rc=$?

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
    local fake_venv
    fake_venv="$(make_fake_venv "oracledb")"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_venv}") || rc=$?

    rm -rf "${fake_venv}"

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "missing Python modules"; then
        report "missing module reported and exits 1" "${PASS}"
    else
        report "missing module reported and exits 1" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_module_reported_and_exits_1 ---

# --- test_all_missing_modules_accumulated ---
test_all_missing_modules_accumulated() {
    local fake_venv
    fake_venv="$(make_fake_venv_all_missing)"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_venv}") || rc=$?

    rm -rf "${fake_venv}"

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
    local fake_venv
    fake_venv="$(make_fake_venv "oracledb")"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_venv}") || rc=$?

    rm -rf "${fake_venv}"

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
