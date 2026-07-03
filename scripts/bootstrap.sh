# ARC_FILE: scripts/bootstrap.sh
# scripts/bootstrap.sh
# Prerequisite gate for Arachnet Clinical Embeddings.
# Checks that the environment is ready before any work begins.
# Does NOT invoke pipeline scripts.
#
# Usage:
#   bash scripts/bootstrap.sh [-h|--help]
#
# Environment variables:
#   PROJECT_ROOT — absolute path to project root. Optional.
#   If unset, auto-detected as the parent of the directory containing
#   this script. Set explicitly to override auto-detection.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.7
# Last modified: 2026-07-02
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# Script-scoped variables set by check functions and reused downstream.
# resolved_venv — physical path of VIRTUAL_ENV (set by check_venv,
#                 read by check_python3).
# PYTHON        — verified venv Python executable (set by check_python3,
#                 read by check_python_modules and check_required_dirs).
resolved_venv=""
PYTHON=""

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

# --- print_usage ---
print_usage() {
    # Print usage information to stdout.
    cat << 'USAGE'
Usage: bash scripts/bootstrap.sh [-h|--help]

Prerequisite gate for Arachnet Clinical Embeddings. Checks that the
environment is ready before any work begins. Does NOT invoke pipeline
scripts.

Checks performed (in order):
  1. Resolve PROJECT_ROOT (auto-detect or override)
  2. Verify virtual environment is active and inside PROJECT_ROOT
  3. Verify python3 resolves to the active venv Python
  4. Verify required Python modules are installed (oracledb, omegaconf, yaml)
  5. Verify required environment variables are set
  6. Verify required directories exist (create if missing)

Environment variables:
  PROJECT_ROOT  Absolute path to project root. Optional — if unset,
                auto-detected as the parent of the directory containing
                this script. Set explicitly to override.
  VIRTUAL_ENV   Set automatically by Python venv activation. Must point
                to a directory inside PROJECT_ROOT.

Exit codes:
  0  All checks passed.
  1  A check failed. Message identifies what and why.

Examples:
  bash scripts/bootstrap.sh
  bash scripts/bootstrap.sh --help
  PROJECT_ROOT=/home/opc/project_embeddings bash scripts/bootstrap.sh
USAGE
}
# --- end print_usage ---

# --- resolve_project_root ---
resolve_project_root() {
    # Determine PROJECT_ROOT and export it.
    # If PROJECT_ROOT is already set in the environment, use it as-is
    # (override). Otherwise, auto-detect as the parent directory of
    # the directory containing this script.
    # Normalizes the resolved path via cd && pwd -P to canonicalize
    # symlinks and relative components.
    # Verifies the resolved path exists and is a directory.
    # Exports PROJECT_ROOT so all child processes inherit it.
    # Exits 1 with a clear message if any step fails.
    if [[ -n "${PROJECT_ROOT:-}" ]]; then
        if [[ ! -d "${PROJECT_ROOT}" ]]; then
            echo "bootstrap: PROJECT_ROOT does not exist: ${PROJECT_ROOT}" >&2
            echo "bootstrap: check your export or set PROJECT_ROOT to the correct path." >&2
            exit 1
        fi
        if ! PROJECT_ROOT="$(cd "${PROJECT_ROOT}" && pwd -P)"; then
            echo "bootstrap: failed to resolve PROJECT_ROOT: ${PROJECT_ROOT}" >&2
            echo "bootstrap: check permissions on the directory." >&2
            exit 1
        fi
        echo "Using PROJECT_ROOT (override): ${PROJECT_ROOT}"
    else
        local script_dir
        if ! script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"; then
            echo "bootstrap: failed to resolve script directory." >&2
            echo "bootstrap: check permissions on the scripts/ directory." >&2
            exit 1
        fi
        PROJECT_ROOT="$(dirname "${script_dir}")"

        if [[ ! -d "${PROJECT_ROOT}" ]]; then
            echo "bootstrap: auto-detected PROJECT_ROOT does not exist: ${PROJECT_ROOT}" >&2
            echo "bootstrap: run the script from within the project tree." >&2
            exit 1
        fi

        echo "Auto-detected PROJECT_ROOT: ${PROJECT_ROOT}"
    fi

    export PROJECT_ROOT
}
# --- end resolve_project_root ---

# --- check_venv ---
check_venv() {
    # Verify a virtual environment is active and lives inside PROJECT_ROOT.
    # Does not assume the venv name — accepts any venv whose physical path
    # starts with PROJECT_ROOT.
    # Checks:
    #   1. VIRTUAL_ENV is set and non-empty.
    #   2. VIRTUAL_ENV exists on disk.
    #   3. VIRTUAL_ENV contains bin/activate (structurally valid venv).
    #   4. VIRTUAL_ENV resolves to a physical path inside PROJECT_ROOT.
    # Sets script-scoped resolved_venv for reuse by check_python3.
    # Exits 1 with actionable message on any failure.
    echo "Checking virtual environment..."

    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        echo "bootstrap: no virtual environment is active." >&2
        echo "bootstrap: activate one with: source <venv_dir>/bin/activate" >&2
        echo "bootstrap: expected venv inside: ${PROJECT_ROOT}" >&2
        exit 1
    fi

    if [[ ! -d "${VIRTUAL_ENV}" ]]; then
        echo "bootstrap: VIRTUAL_ENV is set but does not exist: ${VIRTUAL_ENV}" >&2
        echo "bootstrap: the venv may have been deleted or moved." >&2
        echo "bootstrap: recreate it or activate the correct one." >&2
        exit 1
    fi

    if [[ ! -f "${VIRTUAL_ENV}/bin/activate" ]]; then
        echo "bootstrap: VIRTUAL_ENV exists but is not a valid venv: ${VIRTUAL_ENV}" >&2
        echo "bootstrap: bin/activate is missing — recreate the venv." >&2
        exit 1
    fi

    if ! resolved_venv="$(cd "${VIRTUAL_ENV}" && pwd -P)"; then
        echo "bootstrap: failed to resolve VIRTUAL_ENV path: ${VIRTUAL_ENV}" >&2
        echo "bootstrap: check permissions on the venv directory." >&2
        exit 1
    fi

    local resolved_root
    if ! resolved_root="$(cd "${PROJECT_ROOT}" && pwd -P)"; then
        echo "bootstrap: failed to resolve PROJECT_ROOT path: ${PROJECT_ROOT}" >&2
        exit 1
    fi

    if [[ "${resolved_venv}" != "${resolved_root}/"* ]]; then
        echo "bootstrap: active venv is outside PROJECT_ROOT." >&2
        echo "bootstrap: active venv:  ${resolved_venv}" >&2
        echo "bootstrap: project root: ${resolved_root}" >&2
        echo "bootstrap: activate the project venv from inside: ${resolved_root}" >&2
        exit 1
    fi

    echo "  OK       ${VIRTUAL_ENV}"
}
# --- end check_venv ---

# --- check_python3 ---
check_python3() {
    # Verify python3 exists on PATH and is the active venv Python.
    # Must run after check_venv so VIRTUAL_ENV and resolved_venv are
    # confirmed valid.
    # Uses sys.executable to ask Python itself where it is — more
    # robust than shell symlink resolution via dirname/cd.
    # Warns (does not fail) if Python version is below 3.12.
    # Sets script-scoped PYTHON to the verified executable for reuse
    # by check_python_modules and check_required_dirs.
    # Exits 1 with actionable message if python3 is missing or reports
    # a location outside the active venv.
    echo "Checking python3..."

    local python_path
    local actual_python

    if ! command -v python3 > /dev/null 2>&1; then
        echo "bootstrap: python3 not found on PATH." >&2
        echo "bootstrap: ensure the venv is activated: source ${VIRTUAL_ENV}/bin/activate" >&2
        exit 1
    fi

    python_path="$(command -v python3)"

    if ! actual_python="$(python3 -c "import sys; print(sys.executable)")"; then
        echo "bootstrap: python3 failed to report its executable path." >&2
        echo "bootstrap: the venv Python may be broken — try recreating it." >&2
        exit 1
    fi

    if [[ -z "${actual_python}" ]]; then
        echo "bootstrap: python3 returned an empty executable path." >&2
        echo "bootstrap: the venv Python may be broken — try recreating it." >&2
        exit 1
    fi

    if [[ "${actual_python}" != "${VIRTUAL_ENV}/"* ]] && \
       [[ "${actual_python}" != "${resolved_venv}/"* ]]; then
        echo "bootstrap: python3 is not from the active venv." >&2
        echo "bootstrap: python3 reports: ${actual_python}" >&2
        echo "bootstrap: expected inside: ${VIRTUAL_ENV}" >&2
        echo "bootstrap: activate the correct venv: source ${VIRTUAL_ENV}/bin/activate" >&2
        exit 1
    fi

    # Warn if Python version is below 3.12. ACE targets >= 3.12.
    local version
    version="$(python3 -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))")"
    local major minor
    major="$(python3 -c "import sys; print(sys.version_info.major)")"
    minor="$(python3 -c "import sys; print(sys.version_info.minor)")"
    if [[ "${major}" -lt 3 ]] || { [[ "${major}" -eq 3 ]] && [[ "${minor}" -lt 12 ]]; }; then
        echo "  WARN     python3 version ${version} (ACE target: >= 3.12)" >&2
    fi

    PYTHON="${actual_python}"
    echo "  OK       ${python_path} (${actual_python})"
}
# --- end check_python3 ---

# --- check_python_modules ---
check_python_modules() {
    # Verify that required Python packages are installed in the active venv.
    # Checks all modules and accumulates failures before reporting —
    # missing modules are independent of each other and knowing all
    # missing ones at once is more useful than stopping at the first.
    # Reports the install package name alongside the module name for
    # modules where they differ.
    # Exits 1 if any module is missing, listing all missing ones.
    echo "Checking required Python modules..."

    # Map: import name -> install package name (for actionable error messages).
    # Only entries where the names differ strictly need to be listed, but all
    # checked modules are included for explicitness.
    declare -A module_to_package=(
        [oracledb]="oracledb"
        [omegaconf]="omegaconf"
        [yaml]="PyYAML"
    )

    local modules=("oracledb" "omegaconf" "yaml")
    local missing=()
    local module

    for module in "${modules[@]}"; do
        if "${PYTHON}" -c "import ${module}" 2>/dev/null; then
            echo "  OK       ${module}"
        else
            local pkg="${module_to_package[${module}]:-${module}}"
            echo "  MISSING  ${module} (package: ${pkg})"
            missing+=("${module}")
        fi
    done

    if [[ "${#missing[@]}" -gt 0 ]]; then
        echo "" >&2
        echo "bootstrap: missing Python modules: ${missing[*]}" >&2
        echo "bootstrap: install with: ${PYTHON} -m pip install -r requirements.txt" >&2
        exit 1
    fi
}
# --- end check_python_modules ---

# --- check_env_vars ---
check_env_vars() {
    # Verify required environment variables are set and non-empty.
    # Always checks: SNOMED_LOG_DIR, SNOMED_LOG_LEVEL.
    # If TNS_ADMIN is set (OCI), also checks: TNS_ADMIN,
    # SNOMED_DB_PASSWORD, SNOMED_STAGE_DB_PASSWORD, SNOMED_SYS_DB_PASSWORD.
    # Accumulates all failures before reporting — missing vars are
    # independent and knowing all of them at once is more useful than
    # stopping at the first.
    # Exits 1 if any required variable is missing, listing all.
    echo "Checking environment variables..."

    local missing=()
    local var

    local always_required=(
        "SNOMED_LOG_DIR"
        "SNOMED_LOG_LEVEL"
    )

    for var in "${always_required[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            echo "  MISSING  ${var}"
            missing+=("${var}")
        else
            echo "  OK       ${var}"
        fi
    done

    # OCI path: TNS_ADMIN presence signals production environment.
    if [[ -n "${TNS_ADMIN:-}" ]]; then
        local oci_required=(
            "TNS_ADMIN"
            "SNOMED_DB_PASSWORD"
            "SNOMED_STAGE_DB_PASSWORD"
            "SNOMED_SYS_DB_PASSWORD"
        )
        for var in "${oci_required[@]}"; do
            if [[ -z "${!var:-}" ]]; then
                echo "  MISSING  ${var}"
                missing+=("${var}")
            else
                echo "  OK       ${var}"
            fi
        done
    fi

    if [[ "${#missing[@]}" -gt 0 ]]; then
        echo "" >&2
        echo "bootstrap: missing environment variables: ${missing[*]}" >&2
        echo "bootstrap: set them in your shell profile or before invoking bootstrap." >&2
        exit 1
    fi
}
# --- end check_env_vars ---

# --- check_required_dirs ---
check_required_dirs() {
    # Ensure all required directories exist, creating any that are
    # missing. Reads the directory list from
    # config/directory_structure.yaml via src/common/read_required_dirs.py.
    # Validates each returned path against traversal attacks before use.
    # Exits 1 if the directory list cannot be read, is empty, contains
    # unsafe paths, or a directory cannot be created.
    echo "Checking required directories..."

    local read_required_dirs
    local dirs
    local full_path
    local dir
    local helper_err

    read_required_dirs="${PROJECT_ROOT}/src/common/read_required_dirs.py"

    if [[ ! -f "${read_required_dirs}" ]]; then
        echo "bootstrap: helper script not found: ${read_required_dirs}" >&2
        echo "bootstrap: ensure the repository is complete and PROJECT_ROOT is correct." >&2
        exit 1
    fi

    if ! helper_err="$(mktemp)"; then
        echo "bootstrap: unable to create temporary file for helper stderr." >&2
        exit 1
    fi

    if ! dirs=$("${PYTHON}" "${read_required_dirs}" 2>"${helper_err}"); then
        echo "bootstrap: failed to read required directories:" >&2
        cat "${helper_err}" >&2
        rm -f "${helper_err}"
        exit 1
    fi

    rm -f "${helper_err}"

    if [[ -z "${dirs}" ]]; then
        echo "bootstrap: required directory list is empty." >&2
        echo "bootstrap: check config/directory_structure.yaml and read_required_dirs.py." >&2
        exit 1
    fi

    while IFS= read -r dir; do
        [[ -z "${dir}" ]] && continue

        # Reject absolute paths and path traversal components.
        if [[ "${dir}" = /* ]]; then
            echo "bootstrap: unsafe absolute path from helper: ${dir}" >&2
            exit 1
        fi
        if [[ "${dir}" == *".."* ]]; then
            echo "bootstrap: unsafe traversal path from helper: ${dir}" >&2
            exit 1
        fi

        full_path="${PROJECT_ROOT}/${dir}"
        if [[ -d "${full_path}" ]]; then
            echo "  OK       ${dir}"
        else
            if ! mkdir -p "${full_path}"; then
                echo "bootstrap: failed to create directory: ${full_path}" >&2
                echo "bootstrap: check permissions on: ${PROJECT_ROOT}" >&2
                exit 1
            fi
            echo "  CREATED  ${dir}"
        fi
    done <<< "${dirs}"
}
# --- end check_required_dirs ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    local arg

    for arg in "$@"; do
        case "${arg}" in
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                echo "bootstrap: unknown argument: ${arg}" >&2
                echo "bootstrap: use -h or --help for usage." >&2
                exit 1
                ;;
        esac
    done

    resolve_project_root
    check_venv
    check_python3
    check_python_modules
    check_env_vars
    check_required_dirs

    echo ""
    echo "bootstrap: all checks passed. Environment is ready."
}
# --- end main ---

main "$@"
