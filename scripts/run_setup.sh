#!/usr/bin/env bash
# =============================================================================
# Arachnet Clinical Embeddings — Run DDL setup scripts
# scripts/run_setup.sh
# =============================================================================
# Purpose:
#   Runs sql/ddl/setup/00..03 in order, injecting Oracle credentials from
#   environment variables so that no passwords appear in SQL source files.
#
# Target:  Oracle 23ai / 26ai (OCI Base Database Service)
#
# Prerequisites:
#   The following variables must be set in your shell (e.g. via .bashrc):
#
#     export ORACLE_SYS_USER="SYS"
#     export ORACLE_SYS_PASSWORD=""               # fill in .bashrc
#     export ORACLE_SNOMED_USER="SNOMED"
#     export ORACLE_SNOMED_PASSWORD=""            # fill in .bashrc
#     export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
#     export ORACLE_SNOMED_STAGE_PASSWORD=""      # fill in .bashrc
#     export OCI_DB_CONNECTION_STRING="<host>:<port>/<service_name>"
#
# Usage:
#   bash scripts/run_setup.sh
#
# Author: Jan Mura
# Version: 1.2
# Last modified: 2026-05-01
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_DIR="${SCRIPT_DIR}/../sql/ddl/setup"

# ---------------------------------------------------------------------------
# Validate required environment variables
# ---------------------------------------------------------------------------
required_vars=(
    ORACLE_SYS_USER
    ORACLE_SYS_PASSWORD
    ORACLE_SNOMED_USER
    ORACLE_SNOMED_PASSWORD
    ORACLE_SNOMED_STAGE_USER
    ORACLE_SNOMED_STAGE_PASSWORD
    OCI_DB_CONNECTION_STRING
)

missing=0
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: Required environment variable ${var} is not set or empty." >&2
        missing=1
    fi
done
[[ $missing -eq 1 ]] && exit 1

# ---------------------------------------------------------------------------
# Helper: run a SQL file as SYSDBA with substitution variables injected
# ---------------------------------------------------------------------------
run_sql() {
    local label="$1"
    local sqlfile="$2"
    echo "========================================"
    echo "Running: ${label}"
    echo "File:    ${sqlfile}"
    echo "========================================"
    sqlplus -S \
        "${ORACLE_SYS_USER}/${ORACLE_SYS_PASSWORD}@${OCI_DB_CONNECTION_STRING} AS SYSDBA" \
        <<SQL
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET VERIFY OFF
DEFINE ORACLE_SNOMED_USER="${ORACLE_SNOMED_USER}"
DEFINE ORACLE_SNOMED_PASSWORD="${ORACLE_SNOMED_PASSWORD}"
DEFINE ORACLE_SNOMED_STAGE_USER="${ORACLE_SNOMED_STAGE_USER}"
DEFINE ORACLE_SNOMED_STAGE_PASSWORD="${ORACLE_SNOMED_STAGE_PASSWORD}"
@${sqlfile}
EXIT
SQL
    echo "Done: ${label}"
    echo ""
}

# ---------------------------------------------------------------------------
# Execute scripts in order
# ---------------------------------------------------------------------------
run_sql "00 — Create profile"     "${SQL_DIR}/00_create_profile.sql"
run_sql "01 — Create tablespaces" "${SQL_DIR}/01_create_tablespaces.sql"
run_sql "02 — Create schemas"     "${SQL_DIR}/02_create_schemas.sql"
run_sql "03 — Grants"             "${SQL_DIR}/03_grants.sql"

echo "========================================"
echo "Setup complete."
echo "========================================"
