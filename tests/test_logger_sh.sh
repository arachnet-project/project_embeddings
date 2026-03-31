#!/usr/bin/env bash
# test_logger_sh.sh
# Verification test for scripts/common/logger.sh
# Run on each target platform: Ubuntu, OCI Oracle Linux 9.
#
# Located in: tests/
# Tests:      scripts/common/logger.sh
#
# Does NOT set SNOMED_LOG_DIR or SNOMED_LOG_LEVEL.
# Relies entirely on environment — tests the real setup.
#
# Usage (run from project root):
#   bash tests/test_logger_sh.sh
#
# See tests/protocols/test_logger_sh.md for the full test protocol.
#
# Last modified: 2026-03-28

set -euo pipefail
export LC_ALL=C.UTF-8

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOGGER_SH="${PROJECT_ROOT}/scripts/common/logger.sh"

if [ ! -f "${LOGGER_SH}" ]; then
    printf "ERROR: Cannot find logger.sh at expected path:\n" >&2
    printf "  %s\n" "${LOGGER_SH}" >&2
    printf "Run this script from the project root: bash tests/test_logger_sh.sh\n" >&2
    exit 1
fi

source "${LOGGER_SH}"

# ---------------------------------------------------------------------------
# Report environment
# ---------------------------------------------------------------------------

printf "\n--- test_logger_sh.sh ---\n"
printf "Platform    : %s\n" "$(uname -s -r -m)"
printf "Bash version: %s\n" "${BASH_VERSION}"
printf "Project root: %s\n" "${PROJECT_ROOT}"
printf "SNOMED_LOG_DIR  : %s\n" "${SNOMED_LOG_DIR:-<not set — using default>}"
printf "SNOMED_LOG_LEVEL: %s\n" "${SNOMED_LOG_LEVEL:-<not set — using default INFO>}"
printf "Log file    : %s\n" "${_LOG_FILE}"
printf "LC_ALL      : %s\n" "${LC_ALL}"
printf "\n"

# ---------------------------------------------------------------------------
# Test log lines at each level
# ---------------------------------------------------------------------------

log_debug "test" "step0.3" "DEBUG message — should NOT appear at INFO level"
log_info  "test" "step0.3" "INFO message — pipeline starting"
log_warn  "test" "step0.3" "WARNING message — skip_tables is non-empty"
log_error "test" "step0.3" "ERROR message — simulated load failure"

# ---------------------------------------------------------------------------
# Verify log file
# ---------------------------------------------------------------------------

printf "\n--- Verification ---\n"

if [ "${_LOG_TO_FILE}" = true ]; then
    printf "Log file created : YES\n"
    printf "Log file path    : %s\n" "${_LOG_FILE}"
    printf "Log file size    : %s bytes\n" "$(wc -c < "${_LOG_FILE}")"
    printf "Lines in log file: %s\n" "$(wc -l < "${_LOG_FILE}")"
    printf "\nLast 5 lines of log file:\n"
    tail -5 "${_LOG_FILE}"
else
    printf "Log file created : NO — stdout only\n"
fi

printf "\n--- test_logger_sh.sh complete — exit 0 ---\n\n"
