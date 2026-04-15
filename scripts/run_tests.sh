#!/usr/bin/env bash
# run_tests.sh
# Run all unit tests for Arachnet Clinical Embeddings on Ubuntu.
# Execute from the project root with the venv active.
#
# Usage:
#   bash scripts/run_tests.sh
#
# Exit code 0 if all tests pass. Exit code 1 if any test fails.
# Each test script is run in sequence. Output goes to stdout and
# is also appended to log/test_run.txt.
#
# Target platforms: Ubuntu. Unix/Linux only.
# Last modified: 2026-04-10

set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOG_FILE="log/test_run.txt"
PASS=0
FAIL=0
FAILED_SCRIPTS=""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log() {
    echo "$1" | tee -a "${LOG_FILE}"
}

run_test() {
    local label="$1"
    local cmd="$2"

    log ""
    log "--- ${label} ---"

    if eval "${cmd}" 2>&1 | tee -a "${LOG_FILE}"; then
        log "PASS: ${label}"
        PASS=$((PASS + 1))
    else
        log "FAIL: ${label}"
        FAIL=$((FAIL + 1))
        FAILED_SCRIPTS="${FAILED_SCRIPTS} ${label}"
    fi
}

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

mkdir -p log
: > "${LOG_FILE}"

log "=== run_tests.sh ==="
log "Date: $(date '+%Y-%m-%dT%H:%M:%S')"
log "Machine: $(hostname)"
log "Python: $(python --version 2>&1)"
log ""

# ---------------------------------------------------------------------------
# Test scripts
# ---------------------------------------------------------------------------

run_test "test_exceptions_py" \
    "python tests/test_exceptions_py.py"

run_test "test_logger_py" \
    "python tests/test_logger_py.py"

run_test "test_logger_sh" \
    "bash tests/test_logger_sh.sh"

run_test "test_config_loader_py" \
    "python tests/test_config_loader_r1_py.py"
    "python tests/test_config_loader_r2_py.py"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

TOTAL=$((PASS + FAIL))
log ""
log "=== Summary ==="
log "Passed: ${PASS}"
log "Failed: ${FAIL}"
log "Total:  ${TOTAL}"

if [ "${FAIL}" -gt 0 ]; then
    log "Failed scripts:${FAILED_SCRIPTS}"
    log "Overall: FAIL"
    exit 1
else
    log "Overall: PASS"
    exit 0
fi

