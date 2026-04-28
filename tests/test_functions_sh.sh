#!/usr/bin/env bash
# =============================================================================
# Arachnet Clinical Embeddings — Test suite for scripts/common/functions.sh
# tests/test_functions_sh.sh
# =============================================================================
# Purpose:
#   Tests require_var, require_command, run_test, and summarise_tests from
#   scripts/common/functions.sh. Uses a plain pass/fail pattern consistent
#   with other Bash test scripts in this project.
#
# Usage:
#   bash tests/test_functions_sh.sh
#
#   Can be run from any directory — project root is resolved automatically.
#
# Exit code 0 if all tests pass. Exit code 1 if any test fails.
#
# Author: Jan Mura
# Version: 1.2
# =============================================================================

set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Resolve project root
# ---------------------------------------------------------------------------
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"

# ---------------------------------------------------------------------------
# Set log directory before sourcing logger.sh
# ---------------------------------------------------------------------------
export SNOMED_LOG_DIR="${project_root}/log"

# ---------------------------------------------------------------------------
# Source libraries
# ---------------------------------------------------------------------------
source "${project_root}/scripts/common/logger.sh"
source "${project_root}/scripts/common/functions.sh"

# ---------------------------------------------------------------------------
# Test framework
# Uses separate counter names to avoid collision with _pass/_fail/_failed_labels
# managed by functions.sh run_test and summarise_tests.
# ---------------------------------------------------------------------------
_t_pass=0
_t_fail=0
_t_failed=""

# --- _t_report ---
_t_report() {
    local label="$1"
    local result="$2"
    local detail="${3:-}"

    if [[ "${result}" == "PASS" ]]; then
        log_info "test_functions_sh" "${label}" "PASS ${detail}"
        _t_pass=$((_t_pass + 1))
    else
        log_error "test_functions_sh" "${label}" "FAIL ${detail}"
        _t_fail=$((_t_fail + 1))
        if [[ -z "${_t_failed}" ]]; then
            _t_failed="${label}"
        else
            _t_failed="${_t_failed}, ${label}"
        fi
    fi
}
# --- end _t_report ---

# --- _t_summarise ---
_t_summarise() {
    local total
    total=$((_t_pass + _t_fail))
    log_info "test_functions_sh" "summary" "================================"
    log_info "test_functions_sh" "summary" "Total:  ${total}"
    log_info "test_functions_sh" "summary" "Passed: ${_t_pass}"
    log_info "test_functions_sh" "summary" "Failed: ${_t_fail}"
    if [[ "${_t_fail}" -gt 0 ]]; then
        log_error "test_functions_sh" "summary" "Failed: ${_t_failed}"
        log_error "test_functions_sh" "summary" "Overall: FAIL"
        return 1
    else
        log_info "test_functions_sh" "summary" "Overall: PASS"
        return 0
    fi
}
# --- end _t_summarise ---

# ---------------------------------------------------------------------------
# Tests — require_var
# ---------------------------------------------------------------------------

# --- test_require_var_set ---
test_require_var_set() {
    export _TEST_VAR_SET="hello"
    if require_var "_TEST_VAR_SET" "test variable" 2>/dev/null; then
        _t_report "test_require_var_set" "PASS"
    else
        _t_report "test_require_var_set" "FAIL" "returned non-zero for a set variable"
    fi
    unset _TEST_VAR_SET
}
# --- end test_require_var_set ---

# --- test_require_var_missing ---
test_require_var_missing() {
    unset _TEST_VAR_MISSING 2>/dev/null || true
    if ( require_var "_TEST_VAR_MISSING" "test variable" 2>/dev/null ); then
        _t_report "test_require_var_missing" "FAIL" "did not exit for missing variable"
    else
        _t_report "test_require_var_missing" "PASS"
    fi
}
# --- end test_require_var_missing ---

# --- test_require_var_empty ---
test_require_var_empty() {
    export _TEST_VAR_EMPTY=""
    if ( require_var "_TEST_VAR_EMPTY" "test variable" 2>/dev/null ); then
        _t_report "test_require_var_empty" "FAIL" "did not exit for empty variable"
    else
        _t_report "test_require_var_empty" "PASS"
    fi
    unset _TEST_VAR_EMPTY
}
# --- end test_require_var_empty ---

# ---------------------------------------------------------------------------
# Tests — require_command
# ---------------------------------------------------------------------------

# --- test_require_command_found ---
test_require_command_found() {
    if require_command "bash" 2>/dev/null; then
        _t_report "test_require_command_found" "PASS"
    else
        _t_report "test_require_command_found" "FAIL" "returned non-zero for bash"
    fi
}
# --- end test_require_command_found ---

# --- test_require_command_missing ---
test_require_command_missing() {
    if ( require_command "_no_such_command_xyz_" 2>/dev/null ); then
        _t_report "test_require_command_missing" "FAIL" \
            "did not exit for missing command"
    else
        _t_report "test_require_command_missing" "PASS"
    fi
}
# --- end test_require_command_missing ---

# ---------------------------------------------------------------------------
# Tests — run_test
#
# run_test writes log output via logger.sh to stdout. To isolate only the
# counter values we redirect the entire subshell stdout and stderr to
# /dev/null and write counters to a temp file directly.
# ---------------------------------------------------------------------------

# --- test_run_test_pass ---
test_run_test_pass() {
    local tmp_file
    tmp_file="$(mktemp)"

    (
        _pass=0
        _fail=0
        _failed_labels=""
        run_test "dummy_pass" true
        echo "${_pass}:${_fail}" > "${tmp_file}"
    ) >/dev/null 2>&1

    local result
    result="$(cat "${tmp_file}")"
    rm -f "${tmp_file}"

    if [[ "${result}" == "1:0" ]]; then
        _t_report "test_run_test_pass" "PASS"
    else
        _t_report "test_run_test_pass" "FAIL" "counters were: ${result}"
    fi
}
# --- end test_run_test_pass ---

# --- test_run_test_fail ---
test_run_test_fail() {
    local tmp_file
    tmp_file="$(mktemp)"

    (
        _pass=0
        _fail=0
        _failed_labels=""
        run_test "dummy_fail" false
        echo "${_pass}:${_fail}" > "${tmp_file}"
    ) >/dev/null 2>&1

    local result
    result="$(cat "${tmp_file}")"
    rm -f "${tmp_file}"

    if [[ "${result}" == "0:1" ]]; then
        _t_report "test_run_test_fail" "PASS"
    else
        _t_report "test_run_test_fail" "FAIL" "counters were: ${result}"
    fi
}
# --- end test_run_test_fail ---

# ---------------------------------------------------------------------------
# Tests — summarise_tests
#
# summarise_tests returns 0 or 1. We redirect subshell output to /dev/null
# and use || exit_code=$? to capture a non-zero return without triggering
# set -e in the outer script.
# ---------------------------------------------------------------------------

# --- test_summarise_tests_all_pass ---
test_summarise_tests_all_pass() {
    local exit_code
    exit_code=0
    (
        _pass=3
        _fail=0
        _failed_labels=""
        summarise_tests
    ) >/dev/null 2>&1 || exit_code=$?

    if [[ "${exit_code}" -eq 0 ]]; then
        _t_report "test_summarise_tests_all_pass" "PASS"
    else
        _t_report "test_summarise_tests_all_pass" "FAIL" \
            "exit code was ${exit_code}, expected 0"
    fi
}
# --- end test_summarise_tests_all_pass ---

# --- test_summarise_tests_some_fail ---
test_summarise_tests_some_fail() {
    local exit_code
    exit_code=0
    (
        _pass=2
        _fail=1
        _failed_labels="dummy_fail"
        summarise_tests
    ) >/dev/null 2>&1 || exit_code=$?

    if [[ "${exit_code}" -eq 1 ]]; then
        _t_report "test_summarise_tests_some_fail" "PASS"
    else
        _t_report "test_summarise_tests_some_fail" "FAIL" \
            "exit code was ${exit_code}, expected 1"
    fi
}
# --- end test_summarise_tests_some_fail ---

# ---------------------------------------------------------------------------
# Tests — counter defaults
# ---------------------------------------------------------------------------

# --- test_counter_defaults ---
test_counter_defaults() {
    # Verify that sourcing functions.sh initialises counters to safe defaults.
    # We check the values in the current shell — they were set when
    # functions.sh was sourced at the top of this script.
    local ok=true
    [[ "${_pass}" == "0" ]]         || ok=false
    [[ "${_fail}" == "0" ]]         || ok=false
    [[ "${_failed_labels}" == "" ]] || ok=false
    if [[ "${ok}" == "true" ]]; then
        _t_report "test_counter_defaults" "PASS"
    else
        _t_report "test_counter_defaults" "FAIL" \
            "pass=${_pass} fail=${_fail} labels=${_failed_labels}"
    fi
}
# --- end test_counter_defaults ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

log_info "test_functions_sh" "startup" "================================"
log_info "test_functions_sh" "startup" "Test suite: scripts/common/functions.sh"
log_info "test_functions_sh" "startup" "Date: $(date '+%Y-%m-%dT%H:%M:%S')"
log_info "test_functions_sh" "startup" "================================"

test_require_var_set
test_require_var_missing
test_require_var_empty
test_require_command_found
test_require_command_missing
test_run_test_pass
test_run_test_fail
test_summarise_tests_all_pass
test_summarise_tests_some_fail
test_counter_defaults

_t_summarise
exit $?
