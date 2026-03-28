#!/usr/bin/env bash
# logger.sh
# Bash logging functions for Arachnet Clinical Embeddings.
#
# This file is a sourced library — not executed directly.
# Source it at the top of every Bash script:
#   source "$(dirname "$0")/../common/logger.sh"
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
#
# This file does NOT set shell options (set -euo pipefail), traps,
# or locale variables. Those are the responsibility of the calling
# script. Setting them here would affect the sourcing shell in
# unpredictable ways and is not the role of a sourced library.
#
# Environment variables read:
#   SNOMED_LOG_DIR   — log directory. Default: ./log/
#   SNOMED_LOG_LEVEL — DEBUG | INFO | WARNING | ERROR. Default: INFO
#
# Usage:
#   log_info  "phase1" "step1.2" "Starting RF2 load"
#   log_warn  "phase1" "step1.2" "skip_tables is non-empty"
#   log_error "phase1" "step1.2" "Load failed — exit code $?"
#
# Last modified: 2026-03-28

# ---------------------------------------------------------------------------
# Bash version check
# Requires Bash 4.0 or later.
# Oracle Linux 9 and Ubuntu ship Bash 5.x — this check is a safety net.
# ---------------------------------------------------------------------------

if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    printf "ERROR: logger.sh requires Bash 4.0 or later.\n" >&2
    printf "Current version: %s\n" "${BASH_VERSION}" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve configuration from environment
# ---------------------------------------------------------------------------

_LOG_DIR="${SNOMED_LOG_DIR:-./log}"
_LOG_LEVEL="${SNOMED_LOG_LEVEL:-INFO}"
_LOG_FILE="${_LOG_DIR}/snomed.log"

# ---------------------------------------------------------------------------
# Create log directory if it does not exist.
# If creation fails, fall back to stdout only — do not abort.
# Logging infrastructure failure must never suppress the original operation.
# ---------------------------------------------------------------------------

_LOG_TO_FILE=true
if ! mkdir -p "${_LOG_DIR}" 2>/dev/null; then
    printf "WARNING: Cannot create log directory '%s'. Logging to stdout only.\n" \
        "${_LOG_DIR}" >&2
    _LOG_TO_FILE=false
fi

# ---------------------------------------------------------------------------
# Level filtering
# Map level name strings to numeric values for comparison.
# Naming convention: functions prefixed with _ are internal to this file.
# There are no true private functions in Bash — this is convention only.
# ---------------------------------------------------------------------------

_level_value() {
    case "$1" in
        DEBUG)   echo 10 ;;
        INFO)    echo 20 ;;
        WARNING) echo 30 ;;
        ERROR)   echo 40 ;;
        *)       echo 20 ;;   # unknown level — treat as INFO
    esac
}

_current_level_value=$(_level_value "${_LOG_LEVEL}")

# ---------------------------------------------------------------------------
# Internal write function
# Called by all public log_* functions. Not intended for direct use.
#
# Arguments:
#   $1 — level string: DEBUG | INFO | WARNING | ERROR
#   $2 — phase identifier, e.g. "phase1"
#   $3 — step identifier, e.g. "step1.2"
#   $4 — message text
# ---------------------------------------------------------------------------

_log_write() {
    local level="$1"
    local phase="$2"
    local step="$3"
    local message="$4"

    local msg_level_value
    msg_level_value=$(_level_value "${level}")

    # Suppress messages below the current log level
    if [ "${msg_level_value}" -lt "${_current_level_value}" ]; then
        return 0
    fi

    # Format mirrors Python logger output:
    # 2026-03-28T14:23:01 | INFO     | phase1.step1.2            | message
    local timestamp
    timestamp=$(date '+%Y-%m-%dT%H:%M:%S')

    local name="${phase}.${step}"
    local line
    line=$(printf "%s | %-8s | %-40s | %s" \
        "${timestamp}" "${level}" "${name}" "${message}")

    # Write to stdout
    printf "%s\n" "${line}"

    # Write to file if the log directory is available
    if [ "${_LOG_TO_FILE}" = true ]; then
        printf "%s\n" "${line}" >> "${_LOG_FILE}" 2>/dev/null || {
            printf "WARNING: Cannot write to log file '%s'. File logging disabled.\n" \
                "${_LOG_FILE}" >&2
            _LOG_TO_FILE=false
        }
    fi
}

# ---------------------------------------------------------------------------
# Public functions
# These are the intended interface for all calling scripts.
# Naming convention only — Bash has no access control.
#
# All functions take three arguments:
#   $1 — phase identifier, e.g. "phase1"
#   $2 — step identifier,  e.g. "step1.2"
#   $3 — message text
#
# Defaults are provided for all arguments so a missing argument does not
# cause an unbound variable error under set -u in the calling script.
# ---------------------------------------------------------------------------

log_debug() {
    _log_write "DEBUG" "${1:-unknown}" "${2:-unknown}" "${3:-}"
}

log_info() {
    _log_write "INFO" "${1:-unknown}" "${2:-unknown}" "${3:-}"
}

log_warn() {
    _log_write "WARNING" "${1:-unknown}" "${2:-unknown}" "${3:-}"
}

log_error() {
    # Errors are written to both the log (via _log_write) and to stderr
    # directly, so they remain visible even if the caller has redirected
    # stdout to a file or pipe.
    _log_write "ERROR" "${1:-unknown}" "${2:-unknown}" "${3:-}"
    printf "ERROR: %s\n" "${3:-}" >&2
}
