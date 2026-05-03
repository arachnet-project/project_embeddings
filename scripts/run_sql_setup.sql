#!/usr/bin/env bash
# scripts/run_sql_setup.sh
# ============================================================
# Arachnet Clinical Embeddings — SQL DDL setup runner
# Version: 1.2
# ============================================================
# Runs the four Oracle DDL setup scripts in order using SQLcl.
# Must be run from the project root directory.
#
# Prerequisites:
#   - TNS_ADMIN must be set and tnsnames.ora must be present.
#   - All Oracle credential environment variables must be set.
#   - SNOMED_LOG_DIR must be set.
#   - SQLcl (sql) must be on PATH.
#
# Usage:
#   bash scripts/run_sql_setup.sh
#
# To include 00_create_profile.sql (SYS-level, normally skipped
# because NO_EXPIRY_PROFILE already exists and SYS/SYSTEM are
# already assigned to it):
#   RUN_00=true bash scripts/run_sql_setup.sh
#
# Exit codes:
#   0 — all selected scripts completed successfully
#   1 — prerequisite check failed or a script failed
# ============================================================

set -euo pipefail
export LC_ALL=C.UTF-8

# ============================================================
# Resolve paths
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ============================================================
# Bootstrap: source logger.sh
# At this point we have no logging infrastructure yet.
# If logger.sh is missing the only option is printf to stderr.
# ============================================================
LOGGER_SH="${SCRIPT_DIR}/common/logger.sh"
if [ ! -f "${LOGGER_SH}" ]; then
    printf "ERROR: logger.sh not found at: %s\n" "${LOGGER_SH}" >&2
    printf "ERROR: Cannot continue without logging infrastructure.\n" >&2
    exit 1
fi
# shellcheck source=scripts/common/logger.sh
source "${LOGGER_SH}"

# ============================================================
# Bootstrap: source functions.sh
# logger.sh is now available so we can log properly.
# ============================================================
FUNCTIONS_SH="${SCRIPT_DIR}/common/functions.sh"
if [ ! -f "${FUNCTIONS_SH}" ]; then
    log_error "setup" "run_sql_setup" \
        "functions.sh not found at: ${FUNCTIONS_SH}"
    log_error "setup" "run_sql_setup" \
        "Cannot continue without shared functions library."
    exit 1
fi
# shellcheck source=scripts/common/functions.sh
source "${FUNCTIONS_SH}"

# ============================================================
# Prerequisite checks — environment variables
# ============================================================
require_var "SNOMED_LOG_DIR"               "log directory for this project"
require_var "TNS_ADMIN"                    "directory containing tnsnames.ora"
require_var "ORACLE_TNS_ALIAS"             "TNS alias for the Oracle database"
require_var "ORACLE_SYS_USER"              "Oracle SYSDBA username"
require_var "ORACLE_SYS_PASSWORD"          "Oracle SYSDBA password"
require_var "ORACLE_SNOMED_USER"           "SNOMED schema username"
require_var "ORACLE_SNOMED_PASSWORD"       "SNOMED schema password"
require_var "ORACLE_SNOMED_STAGE_USER"     "SNOMED_STAGE schema username"
require_var "ORACLE_SNOMED_STAGE_PASSWORD" "SNOMED_STAGE schema password"

# ============================================================
# Prerequisite checks — required commands
# ============================================================
require_command "sql"

# ============================================================
# Verify tnsnames.ora exists under TNS_ADMIN
# ============================================================
TNSNAMES_FILE="${TNS_ADMIN}/tnsnames.ora"
if [ ! -f "${TNSNAMES_FILE}" ]; then
    log_error "setup" "run_sql_setup" \
        "tnsnames.ora not found at: ${TNSNAMES_FILE}"
    log_error "setup" "run_sql_setup" \
        "Set TNS_ADMIN correctly and ensure tnsnames.ora is present."
    exit 1
fi

# ============================================================
# Verify DDL script directory exists
# ============================================================
DDL_DIR="${PROJECT_ROOT}/sql/ddl/setup"
if [ ! -d "${DDL_DIR}" ]; then
    log_error "setup" "run_sql_setup" \
        "DDL setup directory not found: ${DDL_DIR}"
    log_error "setup" "run_sql_setup" \
        "Ensure the repository is complete and the script runs from project root."
    exit 1
fi

# ============================================================
# Determine whether to include 00_create_profile.sql
# ============================================================
# Skipped by default. NO_EXPIRY_PROFILE already exists and
# SYS/SYSTEM are already assigned to it.
# Set RUN_00=true in the environment to include it explicitly.
RUN_00="${RUN_00:-false}"

# ============================================================
# Helper: run one SQL script via SQLcl
#
# Arguments:
#   $1 — human-readable label for log messages
#   $2 — full path to the SQL script file
#   $3 — Oracle username for the connection
#   $4 — Oracle password for the connection
#   $5 — "true" to connect AS SYSDBA, "false" otherwise
#
# Returns:
#   0 on success, 1 on failure
#
# The here-document injects schema credentials as DEFINE variables
# so the SQL scripts can reference them as substitution variables
# (&snomed_user, &snomed_password, etc.) without those values
# appearing in any file on disk.
#
# WHENEVER SQLERROR EXIT SQL.SQLCODE causes SQLcl to exit with the
# Oracle error code on any SQL failure, propagating the error back
# to this script via the exit code.
#
# The SQLcl call uses "|| true" to prevent set -e from firing before
# we can capture and check the exit code explicitly.
# ============================================================

# --- run_ddl_script ---
run_ddl_script() {
    local label="$1"
    local script_path="$2"
    local connect_user="$3"
    local connect_password="$4"
    local connect_as_sysdba="$5"

    if [ ! -f "${script_path}" ]; then
        log_error "setup" "run_ddl_script" \
            "SQL script not found: ${script_path}"
        return 1
    fi

    log_info "setup" "run_ddl_script" "Running ${label}: ${script_path}"

    local connect_string
    if [ "${connect_as_sysdba}" = "true" ]; then
        connect_string="${connect_user}/${connect_password}@${ORACLE_TNS_ALIAS} AS SYSDBA"
    else
        connect_string="${connect_user}/${connect_password}@${ORACLE_TNS_ALIAS}"
    fi

    sql -S /nolog <<EOF || true
CONNECT ${connect_string}
SET DEFINE ON
DEFINE snomed_user = "${ORACLE_SNOMED_USER}"
DEFINE snomed_password = "${ORACLE_SNOMED_PASSWORD}"
DEFINE snomed_stage_user = "${ORACLE_SNOMED_STAGE_USER}"
DEFINE snomed_stage_password = "${ORACLE_SNOMED_STAGE_PASSWORD}"
WHENEVER SQLERROR EXIT SQL.SQLCODE
@${script_path}
EXIT SUCCESS
EOF
    local exit_code=$?

    if [ "${exit_code}" -ne 0 ]; then
        log_error "setup" "run_ddl_script" \
            "${label} failed with exit code ${exit_code}."
        return 1
    fi

    log_info "setup" "run_ddl_script" "${label} completed successfully."
    return 0
}
# --- end run_ddl_script ---

# ============================================================
# Main execution
# ============================================================
log_info "setup" "run_sql_setup" "=== Arachnet SQL DDL setup starting ==="
log_info "setup" "run_sql_setup" "Project root : ${PROJECT_ROOT}"
log_info "setup" "run_sql_setup" "DDL directory: ${DDL_DIR}"
log_info "setup" "run_sql_setup" "TNS alias    : ${ORACLE_TNS_ALIAS}"
log_info "setup" "run_sql_setup" "RUN_00 flag  : ${RUN_00}"

# ============================================================
# Script 00 — create profile (optional, SYSDBA)
# ============================================================
if [ "${RUN_00}" = "true" ]; then
    log_info "setup" "run_sql_setup" \
        "RUN_00=true: including 00_create_profile.sql"
    if ! run_ddl_script \
            "00_create_profile.sql" \
            "${DDL_DIR}/00_create_profile.sql" \
            "${ORACLE_SYS_USER}" \
            "${ORACLE_SYS_PASSWORD}" \
            "true"; then
        log_error "setup" "run_sql_setup" \
            "Aborting after 00_create_profile.sql failure."
        exit 1
    fi
else
    log_info "setup" "run_sql_setup" \
        "Skipping 00_create_profile.sql (RUN_00 not set to true)."
    log_info "setup" "run_sql_setup" \
        "NO_EXPIRY_PROFILE already exists. SYS and SYSTEM already assigned."
fi

# ============================================================
# Script 01 — create tablespaces (SYSDBA)
# ============================================================
if ! run_ddl_script \
        "01_create_tablespaces.sql" \
        "${DDL_DIR}/01_create_tablespaces.sql" \
        "${ORACLE_SYS_USER}" \
        "${ORACLE_SYS_PASSWORD}" \
        "true"; then
    log_error "setup" "run_sql_setup" \
        "Aborting after 01_create_tablespaces.sql failure."
    exit 1
fi

# ============================================================
# Script 02 — create schemas (SYSDBA)
# ============================================================
if ! run_ddl_script \
        "02_create_schemas.sql" \
        "${DDL_DIR}/02_create_schemas.sql" \
        "${ORACLE_SYS_USER}" \
        "${ORACLE_SYS_PASSWORD}" \
        "true"; then
    log_error "setup" "run_sql_setup" \
        "Aborting after 02_create_schemas.sql failure."
    exit 1
fi

# ============================================================
# Script 03 — grants (SYSDBA)
# ============================================================
if ! run_ddl_script \
        "03_grants.sql" \
        "${DDL_DIR}/03_grants.sql" \
        "${ORACLE_SYS_USER}" \
        "${ORACLE_SYS_PASSWORD}" \
        "true"; then
    log_error "setup" "run_sql_setup" \
        "Aborting after 03_grants.sql failure."
    exit 1
fi

# ============================================================
# Success
# ============================================================
log_info "setup" "run_sql_setup" "=== All DDL scripts completed successfully ==="
log_info "setup" "run_sql_setup" "Suggested verification queries (run as SYSDBA):"
log_info "setup" "run_sql_setup" "  SELECT username, default_tablespace, profile"
log_info "setup" "run_sql_setup" "  FROM dba_users"
log_info "setup" "run_sql_setup" "  WHERE username IN ('SNOMED', 'SNOMED_STAGE');"
log_info "setup" "run_sql_setup" "  SELECT * FROM dba_sys_privs"
log_info "setup" "run_sql_setup" "  WHERE grantee IN ('SNOMED', 'SNOMED_STAGE')"
log_info "setup" "run_sql_setup" "  ORDER BY grantee, privilege;"

exit 0
