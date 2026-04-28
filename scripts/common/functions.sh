#!/usr/bin/env bash
# =============================================================================
# Arachnet Clinical Embeddings — Shared Bash functions library
# scripts/common/functions.sh
# =============================================================================
# Purpose:
#   Reusable Bash functions sourced by pipeline and infrastructure scripts.
#   Covers environment validation, test execution, and summary reporting.
#
# Usage:
#   source "${script_dir}/common/functions.sh"
#
# This file is a sourced library — not executed directly.
# Does NOT set shell options, traps, or locale variables.
# Those are the responsibility of the calling script.
#
# Requires: scripts/common/logger.sh sourced before this file.
#
# Test counters _pass, _fail, _failed_labels are initialised here with
# defaults so the calling script does not need to declare them first.
# If the calling script declares them before sourcing, those values are
# preserved via the :- default syntax.
#
# Author: Jan Mura
# Version: 1.1
# =============================================================================

# ---------------------------------------------------------------------------
# Bash version check
# Requires Bash 4.0 or later.
# Note: exit here is intentional. This check runs at source time and
# failure is unrecoverable — the calling shell cannot function without
# the minimum required Bash version.
# ---------------------------------------------------------------------------
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    printf "ERROR: functions.sh requires Bash 4.0 or later.\n" >&2
    printf "Current version: %s\n" "${BASH_VERSION}" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Test counters
# Initialised here so callers do not need to declare them before sourcing.
# If the caller has already declared them, the existing values are preserved.
# Under set -u, unset variables in arithmetic or string context would cause
# an error — these defaults prevent that.
# ---------------------------------------------------------------------------
_pass="${_pass:-0}"
_fail="${_fail:-0}"
_failed_labels="${_failed_labels:-}"

# ---------------------------------------------------------------------------
# require_var
#
# Validates that a named environment variable is set and non-empty.
# Logs an error and exits with code 1 if the variable is missing or empty.
#
# Note: exit 1 is intentional here, not return 1. require_var is a
# prerequisite guard called at script startup. If a required variable is
# absent the script cannot proceed and there is no meaningful recovery path
# in the caller. Exiting immediately with a clear message is the correct
# behaviour.
#
# Arguments:
#   $1 — variable name (string, not the value)
#   $2 — human-readable description for the error message
#
# Usage:
#   require_var "TNS_ADMIN" "TNS admin directory"
#   require_var "SNOMED_ADMIN_DB_PASSWORD" "SYSDBA password"
# ---------------------------------------------------------------------------

# --- require_var ---
require_var() {
    local var_name="$1"
    local description="$2"
    local var_value

    var_value="${!var_name:-}"

    if [[ -z "${var_value}" ]]; then
        log_error "common" "functions" \
            "Required variable ${var_name} is not set — ${description}"
        exit 1
    fi
}
# --- end require_var ---

# ---------------------------------------------------------------------------
# require_command
#
# Validates that a named command is available on PATH.
# Logs an error and exits with code 1 if the command is not found.
#
# Note: exit 1 is intentional here, not return 1. require_command is a
# prerequisite guard called at script startup. If a required command is
# absent the script cannot proceed and there is no meaningful recovery path
# in the caller. Exiting immediately with a clear message is the correct
# behaviour.
#
# Arguments:
#   $1 — command name
#
# Usage:
#   require_command "sql"
#   require_command "python"
# ---------------------------------------------------------------------------

# --- require_command ---
require_command() {
    local cmd="$1"

    if ! command -v "${cmd}" &>/dev/null; then
        log_error "common" "functions" \
            "Required command not found on PATH: ${cmd}"
        exit 1
    fi
}
# --- end require_command ---

# ---------------------------------------------------------------------------
# run_test
#
# Runs a single test command, logs pass or fail, and updates the module-level
# pass/fail counters.
#
# Note: test output flows directly to stdout and is not captured to the log
# file. The pass/fail verdict is logged via log_info and log_error, which
# do write to the log file. Capturing full test output to the log file would
# require redirecting stdout, which would suppress terminal output during
# the run. The current behaviour is intentional.
#
# Arguments:
#   $1       — human-readable label for the test
#   $2 ...   — command and arguments to execute
#
# Usage:
#   run_test "test_config_loader_py" python tests/test_config_loader_py.py
#   run_test "test_logger_sh" bash tests/test_logger_sh.sh
# ---------------------------------------------------------------------------

# --- run_test ---
run_test() {
    local label="$1"
    shift

    log_info "common" "run_test" "Running: ${label}"

    if "$@" 2>&1; then
        log_info "common" "run_test" "PASS: ${label}"
        _pass=$((_pass + 1))
    else
        log_error "common" "run_test" "FAIL: ${label}"
        _fail=$((_fail + 1))
        if [[ -z "${_failed_labels}" ]]; then
            _failed_labels="${label}"
        else
            _failed_labels="${_failed_labels}, ${label}"
        fi
    fi
}
# --- end run_test ---

# ---------------------------------------------------------------------------
# summarise_tests
#
# Prints a summary of test results using the module-level counters set by
# run_test. Returns exit code 0 if all tests passed, 1 if any failed.
#
# Arguments: none
#
# Usage:
#   summarise_tests
#   exit $?
# ---------------------------------------------------------------------------

# --- summarise_tests ---
summarise_tests() {
    local total
    total=$((_pass + _fail))

    log_info "common" "summarise_tests" "================================"
    log_info "common" "summarise_tests" "Total:  ${total}"
    log_info "common" "summarise_tests" "Passed: ${_pass}"
    log_info "common" "summarise_tests" "Failed: ${_fail}"

    if [[ "${_fail}" -gt 0 ]]; then
        log_error "common" "summarise_tests" \
            "Failed tests: ${_failed_labels}"
        log_error "common" "summarise_tests" "Overall: FAIL"
        return 1
    else
        log_info "common" "summarise_tests" "Overall: PASS"
        return 0
    fi
}
# --- end summarise_tests ---

