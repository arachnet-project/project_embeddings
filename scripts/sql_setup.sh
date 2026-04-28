#!/bin/bash
# =============================================================================
# Arachnet Clinical Embeddings — Database schema setup
# scripts/sql_setup.sh
# =============================================================================
# Purpose:
#   Runs the numbered SQL setup scripts in sql/ddl/setup/ in order as SYSDBA.
#   Connects to Oracle via TNS using SQLcl. Spools all output to a timestamped
#   log file in log/sql_setup/.
#
#   Run this script once on a fresh Oracle instance before Phase 1 begins.
#   On OCI: NO_EXPIRY_PROFILE already exists. Script 00 is skipped by default.
#   Set RUN_00=true to include it on a genuinely fresh instance.
#
# Usage:
#   export SNOMED_ADMIN_DB_PASSWORD="your_password"
#   export DB_TNS_ALIAS="ARADB"
#   export TNS_ADMIN="/path/to/tns/dir"
#   bash scripts/sql_setup.sh
#
#   To include 00_create_profile.sql on a fresh instance:
#   RUN_00=true bash scripts/sql_setup.sh
#
# Prerequisites:
#   - SQLcl 24.4.1 or later installed and on PATH
#   - TNS_ADMIN set and tnsnames.ora present
#   - SNOMED_ADMIN_DB_PASSWORD set in environment
#   - DB_TNS_ALIAS set in environment
#   - Tablespaces, schemas, and grants not yet created
#
# Author: Jan Mura
# Version: 1.0
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve project root — always the parent of the directory holding this
# script, regardless of where it is called from.
# ---------------------------------------------------------------------------
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"

# ---------------------------------------------------------------------------
# Validate required environment variables
# ---------------------------------------------------------------------------
if [[ -z "${SNOMED_ADMIN_DB_PASSWORD:-}" ]]; then
    echo "ERROR: SNOMED_ADMIN_DB_PASSWORD is not set." >&2
    exit 1
fi

if [[ -z "${DB_TNS_ALIAS:-}" ]]; then
    echo "ERROR: DB_TNS_ALIAS is not set." >&2
    exit 1
fi

if [[ -z "${TNS_ADMIN:-}" ]]; then
    echo "ERROR: TNS_ADMIN is not set." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate SQLcl is available
# ---------------------------------------------------------------------------
if ! command -v sql &>/dev/null; then
    echo "ERROR: SQLcl (sql) not found on PATH." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Prepare spool output directory and log file
# ---------------------------------------------------------------------------
log_dir="${project_root}/log/sql_setup"
mkdir -p "${log_dir}"
timestamp="$(date +%Y%m%dT%H%M%S)"
spool_file="${log_dir}/sql_setup_${timestamp}.log"

echo "SQL setup starting at ${timestamp}"
echo "Spool output: ${spool_file}"
echo "TNS alias: ${DB_TNS_ALIAS}"
echo "TNS_ADMIN: ${TNS_ADMIN}"

# ---------------------------------------------------------------------------
# Resolve setup script directory
# ---------------------------------------------------------------------------
setup_dir="${project_root}/sql/ddl/setup"

# ---------------------------------------------------------------------------
# Build the SQLcl input. Each script is run via @path inside SQLcl.
# WHENEVER SQLERROR EXIT FAILURE ensures SQLcl exits non-zero on any error.
# SET FEEDBACK ON ensures Oracle echoes each statement result.
# SPOOL captures all output to the log file.
# ---------------------------------------------------------------------------
run_00="${RUN_00:-false}"

sqlcl_input="WHENEVER SQLERROR EXIT FAILURE
SET FEEDBACK ON
SET ECHO ON
SPOOL ${spool_file}
"

if [[ "${run_00}" == "true" ]]; then
    sqlcl_input="${sqlcl_input}
-- Running 00_create_profile.sql
@${setup_dir}/00_create_profile.sql
"
else
    sqlcl_input="${sqlcl_input}
-- Skipping 00_create_profile.sql (RUN_00 not set to true)
-- NO_EXPIRY_PROFILE assumed to already exist on this instance.
"
fi

sqlcl_input="${sqlcl_input}
-- Running 01_create_tablespaces.sql
@${setup_dir}/01_create_tablespaces.sql

-- Running 02_create_schemas.sql
@${setup_dir}/02_create_schemas.sql

-- Running 03_grants.sql
@${setup_dir}/03_grants.sql

SPOOL OFF
EXIT SUCCESS
"

# ---------------------------------------------------------------------------
# Run SQLcl as SYSDBA over TNS
# Password is passed via environment variable — never echoed to terminal.
# ---------------------------------------------------------------------------
echo "${sqlcl_input}" | sql "system/${SNOMED_ADMIN_DB_PASSWORD}@${DB_TNS_ALIAS}" as sysdba

exit_code=$?

# ---------------------------------------------------------------------------
# Report outcome
# ---------------------------------------------------------------------------
if [[ "${exit_code}" -eq 0 ]]; then
    echo "SQL setup completed successfully."
    echo "Review spool output at: ${spool_file}"
else
    echo "ERROR: SQL setup failed with exit code ${exit_code}." >&2
    echo "Review spool output at: ${spool_file}" >&2
    exit "${exit_code}"
fi
