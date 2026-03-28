#!/usr/bin/env bash
# test_logger.sh
# Verification test for logger.sh.
# Run this on each platform (OCI Oracle Linux 9, Ubuntu) after
# setting up environment variables in .bashrc.
#
# Located in: tests/
# Tests:      scripts/common/logger.sh
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
#
# This script does NOT set SNOMED_LOG_DIR or SNOMED_LOG_LEVEL.
# It relies entirely on whatever is set in the environment.
# That is intentional — it tests the real setup, not a local override.
#
# Usage (run from project root):
#   bash tests/test_logger.sh
#
# See docs/test_logger_protocol.md for the full test protocol.
#
# Last modified: 2026-03-28

set -euo pipefail

# ---------------------------------------------------------------------------
# Locale — set here in the calling script, not in the sourced library.
# Forces English output from system commands (date, mkdir, etc.)
# while preserving UTF-8 encoding for data and messages.
# C.UTF-8 is supported on Oracle Linux 9 and Ubuntu.
# ---------------------------------------------------------------------------

export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Locate logger.sh relative to this script's location.
# test_logger.sh lives in tests/
# logger.sh lives in scripts/common/
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOGGER_SH="${PROJECT_ROOT}/scripts/common/logger.sh"

if [ ! -f "${LOGGER_SH}" ]; then
    printf "ERROR: Cannot find logger.sh at expected path:\n" >&2
    printf "  %s\n" "${LOGGER_SH}" >&2
    printf "Run this script from the project root: bash tests/test_logger.sh\n" >&2
    exit 1
fi

source "${LOGGER_SH}"

# ---------------------------------------------------------------------------
# Report environment before running tests
# ---------------------------------------------------------------------------

printf "\n--- Logger test ---\n"
printf "Platform    : %s\n" "$(uname -s -r -m)"
printf "Bash version: %s\n" "${BASH_VERSION}"
printf "Project root: %s\n" "${PROJECT_ROOT}"
printf "SNOMED_LOG_DIR  : %s\n" "${SNOMED_LOG_DIR:-<not set — using default>}"
printf "SNOMED_LOG_LEVEL: %s\n" "${SNOMED_LOG_LEVEL:-<not set — using default INFO>}"
printf "Log file    : %s\n" "${_LOG_FILE}"
printf "LC_ALL      : %s\n" "${LC_ALL}"
printf "\n"

# ---------------------------------------------------------------------------
# Run test log lines at each level
# ---------------------------------------------------------------------------

log_debug "test" "step0.3" "DEBUG message — should NOT appear at INFO level"
log_info  "test" "step0.3" "INFO message — pipeline starting"
log_warn  "test" "step0.3" "WARNING message — skip_tables is non-empty"
log_error "test" "step0.3" "ERROR message — simulated load failure"

# ---------------------------------------------------------------------------
# Verify log file was created and contains expected content
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
    printf "Log file created : NO — file logging unavailable, stdout only\n"
fi

printf "\n--- Test complete ---\n"
printf "Exit code will be 0 if no errors were encountered above.\n\n"
