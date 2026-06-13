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
# Version: 1.0
# Last modified: 2026-06-08
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

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

Environment variables:
  PROJECT_ROOT  Absolute path to project root. Optional — if unset,
                auto-detected as the parent of the directory containing
                this script. Set explicitly to override.

Exit codes:
  0  All checks passed.
  1  A check failed. Message identifies what and why.
USAGE
}
# --- end print_usage ---

# --- resolve_project_root ---
resolve_project_root() {
    # Determine PROJECT_ROOT.
    # If PROJECT_ROOT is already set in the environment, use it as-is
    # (override). Otherwise, auto-detect as the parent directory of
    # the directory containing this script.
    # Verifies the resolved path exists and is a directory.
    # Exits 1 if PROJECT_ROOT is set but does not exist, or if
    # auto-detection fails.
    if [[ -n "${PROJECT_ROOT:-}" ]]; then
        if [[ ! -d "${PROJECT_ROOT}" ]]; then
            echo "bootstrap: PROJECT_ROOT does not exist: ${PROJECT_ROOT}" >&2
            exit 1
        fi
        echo "Using PROJECT_ROOT (override): ${PROJECT_ROOT}"
        return
    fi

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "${script_dir}")"

    if [[ ! -d "${PROJECT_ROOT}" ]]; then
        echo "bootstrap: auto-detected PROJECT_ROOT does not exist: ${PROJECT_ROOT}" >&2
        exit 1
    fi

    echo "Auto-detected PROJECT_ROOT: ${PROJECT_ROOT}"
}
# --- end resolve_project_root ---

# --- check_python3 ---
check_python3() {
    # Verify python3 is available on PATH.
    # Exits 1 if python3 is not found.
    echo "Checking python3..."
    if ! command -v python3 > /dev/null 2>&1; then
        echo "bootstrap: python3 not found on PATH." >&2
        exit 1
    fi
    echo "  OK       $(command -v python3)"
}
# --- end check_python3 ---

# --- check_required_dirs ---
check_required_dirs() {
    # Round 1: ensure all required directories exist, creating any
    # that are missing.
    # Reads the directory list from config/directory_structure.yaml
    # via src/common/read_required_dirs.py.
    # Returns:
    #   0 always — missing directories are created, not treated as
    #   failures. Exits 1 only if the directory list cannot be read
    #   or a directory cannot be created.
    echo "Checking required directories..."

    local read_required_dirs="${PROJECT_ROOT}/src/common/read_required_dirs.py"

    if [[ ! -f "${read_required_dirs}" ]]; then
        echo "bootstrap: helper script not found: ${read_required_dirs}" >&2
        exit 1
    fi

    local dirs
    local helper_err
    helper_err="$(mktemp)"
    if ! dirs=$(python3 "${read_required_dirs}" 2> "${helper_err}"); then
        echo "bootstrap: failed to read required directories:" >&2
        cat "${helper_err}" >&2
        rm -f "${helper_err}"
        exit 1
    fi
    rm -f "${helper_err}"

    while IFS= read -r dir; do
        [[ -z "${dir}" ]] && continue
        local full_path="${PROJECT_ROOT}/${dir}"
        if [[ -d "${full_path}" ]]; then
            echo "  OK       ${dir}"
        else
            if ! mkdir -p "${full_path}"; then
                echo "bootstrap: failed to create directory: ${full_path}" >&2
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
    if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
        print_usage
        exit 0
    fi

    resolve_project_root
    check_python3
    check_required_dirs

    echo ""
    echo "bootstrap: round 1 (directories) complete."
}
# --- end main ---

main "$@"
