#!/usr/bin/env bash
# =============================================================================
# Arachnet Clinical Embeddings — Run all tests
# scripts/run_tests.sh
# =============================================================================
# Purpose:
#   Runs all unit and integration tests for the project in sequence.
#   Works on both Ubuntu (mocked database tests) and OCI (real database).
#   Set SNOMED_TEST_REAL_DB=true on OCI to enable real database tests.
#
# Usage:
#   bash scripts/run_tests.sh
#   SNOMED_TEST_REAL_DB=true bash scripts/run_tests.sh
#
#   Can be run from any directory — project root is resolved automatically
#   from the location of this script.
#
# Prerequisites:
#   - Python venv must be active.
#   - SNOMED_LOG_LEVEL set, or default INFO accepted.
#   - On OCI: SNOMED_DB_PASSWORD and SNOMED_STAGE_DB_PASSWORD must be set.
#
# Exit code 0 if all tests pass. Exit code 1 if any test fails.
#
# Author: Jan Mura
# Version: 1.1
# =============================================================================

set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Resolve project root — parent of the directory holding this script.
# Works regardless of where the script is called from.
# ---------------------------------------------------------------------------
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"

# ---------------------------------------------------------------------------
# Set log directory before sourcing logger.sh so it writes to the correct
# location under the project root rather than the default ./log.
# ---------------------------------------------------------------------------
export SNOMED_LOG_DIR="${project_root}/log"

# ---------------------------------------------------------------------------
# Source libraries
# ---------------------------------------------------------------------------
source "${script_dir}/common/logger.sh"
source "${script_dir}/common/functions.sh"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Real database tests — false on Ubuntu, true on OCI
real_db="${SNOMED_TEST_REAL_DB:-false}"

# Python interpreter — must be the venv python
python_cmd="python"

# Test script directory
tests_dir="${project_root}/tests"

# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------
log_info "run_tests" "startup" "================================"
log_info "run_tests" "startup" "Arachnet Clinical Embeddings — Test Runner"
log_info "run_tests" "startup" "Date:    $(date '+%Y-%m-%dT%H:%M:%S')"
log_info "run_tests" "startup" "Machine: $(hostname)"
log_info "run_tests" "startup" "Python:  $(${python_cmd} --version 2>&1)"
log_info "run_tests" "startup" "Real DB: ${real_db}"
log_info "run_tests" "startup" "================================"

# ---------------------------------------------------------------------------
# Validate prerequisites
# ---------------------------------------------------------------------------
require_command "${python_cmd}"

if [[ "${real_db}" == "true" ]]; then
    require_var "SNOMED_DB_PASSWORD" "production schema password"
    require_var "SNOMED_STAGE_DB_PASSWORD" "stage schema password"
    require_var "TNS_ADMIN" "TNS admin directory"
fi

# ---------------------------------------------------------------------------
# Tests — Phase 0 foundation
# These tests run identically on Ubuntu and OCI.
# ---------------------------------------------------------------------------
log_info "run_tests" "phase0" "Running Phase 0 foundation tests"

run_test "test_exceptions_py" \
    "${python_cmd}" "${tests_dir}/test_exceptions_py.py"

run_test "test_logger_py" \
    "${python_cmd}" "${tests_dir}/test_logger_py.py"

run_test "test_logger_sh" \
    bash "${tests_dir}/test_logger_sh.sh"

run_test "test_functions_sh" \
    bash "${tests_dir}/test_functions_sh.sh"

run_test "test_config_loader_py" \
    "${python_cmd}" "${tests_dir}/test_config_loader_py.py"

# ---------------------------------------------------------------------------
# Tests — Step 0.6 database connection
# Runs on both platforms. The test script itself detects
# SNOMED_TEST_REAL_DB and switches between mock and real modes.
# ---------------------------------------------------------------------------
log_info "run_tests" "step06" "Running Step 0.6 database connection tests"

run_test "test_db_connection_py" \
    "${python_cmd}" "${tests_dir}/test_db_connection_py.py"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
summarise_tests
exit $?
