#!/usr/bin/env bash
# test_logger.sh
# Verification test for logger.sh.
# Run this on each platform (macOS, OCI Oracle Linux 9, Ubuntu) after
# setting up environment variables in .bashrc.
#
# This script does NOT set SNOMED_LOG_DIR or SNOMED_LOG_LEVEL.
# It relies entirely on whatever is set in the environment.
# That is intentional — it tests the real setup, not a local override.
#
# Usage:
#   bash scripts/common/test_logger.sh
#
# Expected outcome:
#   - All test lines appear on stdout in the correct format
#   - A log file is created in $SNOMED_LOG_DIR
#   - The log file contains the same lines as stdout
#   - The DEBUG line does NOT appear when SNOMED_LOG_LEVEL=INFO
#   - The script exits with code 0
#
# See docs/test_logger_protocol.md for the full test protocol.
#
# Last modified: 2026-03-27

set -euo pipefail

# ---------------------------------------------------------------------------
# Locate and source logger.sh relative to this script's location.
# This works regardless of which directory the script is called from.
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/logger.sh"

# ---------------------------------------------------------------------------
# Report environment before running tests
# ---------------------------------------------------------------------------

printf "\n--- Logger test ---\n"
printf "Platform    : %s\n" "$(uname -s -r -m)"
printf "Bash version: %s\n" "${BASH_VERSION}"
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
