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
# Version: 1.9
# Last modified: 2026-09-06
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# Script-scoped variables set by check functions and reused downstream.
# resolved_venv  — physical path of VIRTUAL_ENV (set by check_venv,
#                  read by check_python3).
# PYTHON         — verified venv Python executable (set by check_python3,
#                  read by check_python_modules and check_required_dirs).
# RESOLVED_ROOT  — canonicalized PROJECT_ROOT (set by resolve_project_root,
#                  read by check_required_dirs and print_environment_summary).
# PYTHON_VERSION — full venv Python version (set by check_python3, read
#                  by print_environment_summary).
# TEMP_FILES     — registered temporary files for EXIT-trap cleanup
#                  (populated by check_python_modules and
#                  check_required_dirs, consumed by cleanup_temp_files).
resolved_venv=""
PYTHON=""
RESOLVED_ROOT=""
PYTHON_VERSION=""
TEMP_FILES=()

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
  4. Verify required Python modules are installed
  5. Verify required environment variables are set
  6. Verify required directories exist (create if missing)

Environment variables:
  PROJECT_ROOT      Absolute path to project root. Optional — if unset,
                    auto-detected as the parent of the directory
                    containing this script. Set explicitly to override.
  VIRTUAL_ENV       Set automatically by Python venv activation. Must
                    point to a directory inside PROJECT_ROOT.
  SNOMED_LOG_DIR    Required. Directory for log output.
  SNOMED_LOG_LEVEL  Required. Logging verbosity level.
  TNS_ADMIN         Optional. Presence signals an OCI/production
                    environment. If set, also requires:
                      SNOMED_DB_PASSWORD
                      SNOMED_STAGE_DB_PASSWORD

Notes:
  This is a local prerequisite gate only. It does not verify Oracle
  connectivity or schema reachability — a --real-db mode for that
  purpose is planned but not yet implemented (see docs/todo.md).
  A Python version below 3.12 produces a warning, not a failure.

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

# --- cleanup_temp_files ---
cleanup_temp_files() {
    # Remove all registered temporary files on script exit, without
    # changing the script's exit status. Installed as an EXIT trap in
    # main() so cleanup runs regardless of which check function exits
    # the script, or how.
    local exit_status=$?
    local temp_file
    for temp_file in "${TEMP_FILES[@]}"; do
        if [[ -n "${temp_file}" ]]; then
            rm -f -- "${temp_file}" || true
        fi
    done
    return "${exit_status}"
}
# --- end cleanup_temp_files ---

# --- resolve_project_root ---
resolve_project_root() {
    # Determine PROJECT_ROOT and export it.
    # If PROJECT_ROOT is already set in the environment, use it as-is
    # (override). Otherwise, auto-detect as the parent directory of
    # the directory containing this script.
    # Normalizes the resolved path via cd && pwd -P to canonicalize
    # symlinks and relative components.
    # Verifies the resolved path exists and is a directory.
    # Exports PROJECT_ROOT so all child processes inherit it, and sets
    # script-scoped RESOLVED_ROOT to the same canonicalized value for
    # reuse by check_required_dirs and print_environment_summary.
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

    if ! RESOLVED_ROOT="$(cd "${PROJECT_ROOT}" && pwd -P)"; then
        echo "bootstrap: failed to resolve canonical PROJECT_ROOT: ${PROJECT_ROOT}" >&2
        exit 1
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

    if [[ "${resolved_venv}" != "${RESOLVED_ROOT}/"* ]]; then
        echo "bootstrap: active venv is outside PROJECT_ROOT." >&2
        echo "bootstrap: active venv:  ${resolved_venv}" >&2
        echo "bootstrap: project root: ${RESOLVED_ROOT}" >&2
        echo "bootstrap: activate the project venv from inside: ${RESOLVED_ROOT}" >&2
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
    # Sets script-scoped PYTHON to the verified executable (as soon as
    # it is confirmed valid, so every subsequent query in this
    # function also goes through the verified executable rather than
    # bare python3) and PYTHON_VERSION to its full version, for reuse
    # by check_python_modules, check_required_dirs, and
    # print_environment_summary.
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

    PYTHON="${actual_python}"

    # Warn if Python version is below 3.12. ACE targets >= 3.12.
    local version
    version="$("${PYTHON}" -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))")"
    local major minor
    major="$("${PYTHON}" -c "import sys; print(sys.version_info.major)")"
    minor="$("${PYTHON}" -c "import sys; print(sys.version_info.minor)")"
    if [[ "${major}" -lt 3 ]] || { [[ "${major}" -eq 3 ]] && [[ "${minor}" -lt 12 ]]; }; then
        echo "  WARN     python3 version ${version} (ACE target: >= 3.12)" >&2
    fi

    PYTHON_VERSION="$("${PYTHON}" -c "import sys; print('{}.{}.{}'.format(*sys.version_info[:3]))")"
    echo "  OK       ${python_path} (${actual_python})"
}
# --- end check_python3 ---

# --- check_python_modules ---
check_python_modules() {
    # Verify that required Python packages are installed in the active venv.
    # Reads the (import_name, package_name) list from
    # config/required_modules.json via
    # src/common/read_required_modules.py — single source of truth,
    # shared with any other tool that needs the same list (e.g. a
    # future requirements.txt generator).
    #
    # Uses JSON, not YAML, deliberately: this function is what proves
    # PyYAML is installed in the first place, so it cannot depend on
    # PyYAML to read its own module list. json is Python stdlib and
    # carries no such circularity.
    #
    # Checks all modules and accumulates failures before reporting —
    # missing modules are independent of each other and knowing all
    # missing ones at once is more useful than stopping at the first.
    # Distinguishes two independent failure modes:
    #   MISSING       — the module (or a required dotted-path parent
    #                   component of it) is genuinely not installed.
    #   IMPORT FAILED — the module is present but raised an error, or
    #                   exited abnormally, during import (e.g. a
    #                   broken install, a missing transitive
    #                   dependency, or a module that calls sys.exit()
    #                   at import time).
    # The module name is never interpolated into Python source: it is
    # passed as sys.argv[1] and looked up via importlib.import_module,
    # so a malformed or malicious import_name value in the registry
    # can only ever be looked up as a module name, never executed as
    # code.
    # An empty record from the helper is treated as a protocol
    # violation and fails loudly rather than being silently skipped —
    # the helpers are expected to prevent this, but bootstrap does not
    # rely on that alone.
    # Exits 1 if the module list cannot be read, or if any module is
    # missing or fails to import (listing all such modules).
    echo "Checking required Python modules..."

    local read_required_modules
    local records
    local helper_err
    local module package
    local missing=()
    local import_failed=()

    read_required_modules="${PROJECT_ROOT}/src/common/read_required_modules.py"

    if [[ ! -f "${read_required_modules}" ]]; then
        echo "bootstrap: helper script not found: ${read_required_modules}" >&2
        echo "bootstrap: ensure the repository is complete and PROJECT_ROOT is correct." >&2
        exit 1
    fi

    if ! helper_err="$(mktemp)"; then
        echo "bootstrap: unable to create temporary file for helper stderr." >&2
        exit 1
    fi
    TEMP_FILES+=("${helper_err}")

    if ! records=$("${PYTHON}" "${read_required_modules}" 2>"${helper_err}"); then
        echo "bootstrap: failed to read required modules:" >&2
        cat "${helper_err}" >&2
        exit 1
    fi

    if [[ -z "${records}" ]]; then
        echo "bootstrap: required module list is empty." >&2
        echo "bootstrap: check config/required_modules.json and read_required_modules.py." >&2
        exit 1
    fi

    while IFS=',' read -r module package; do
        if [[ -z "${module}" ]]; then
            echo "bootstrap: read_required_modules.py produced an empty record." >&2
            echo "bootstrap: this indicates a helper protocol violation." >&2
            exit 1
        fi

        local rc=0
        # Exit codes 10/20 are internal classification codes, chosen to
        # not collide with any exit status a module's own init code
        # might plausibly produce. BaseException (not Exception) is
        # caught deliberately so SystemExit during import (e.g. a
        # module calling sys.exit() at import time) is classified as
        # IMPORT FAILED rather than misread as our own exit-1 status.
        # This also catches KeyboardInterrupt; an interrupt during this
        # sub-second import check is treated as IMPORT FAILED.
        "${PYTHON}" -c '
import importlib
import sys
requested = sys.argv[1]
try:
    importlib.import_module(requested)
except ModuleNotFoundError as exc:
    missing_name = exc.name or ""
    if (
        missing_name == requested
        or requested.startswith(missing_name + ".")
    ):
        sys.exit(10)
    sys.exit(20)
except BaseException:
    sys.exit(20)
sys.exit(0)
' "${module}" 2>/dev/null || rc=$?

        if [[ "${rc}" -eq 0 ]]; then
            echo "  OK            ${module}"
        elif [[ "${rc}" -eq 10 ]]; then
            echo "  MISSING       ${module} (package: ${package})"
            missing+=("${module}")
        else
            echo "  IMPORT FAILED ${module} (package: ${package})"
            import_failed+=("${module}")
        fi
    done <<< "${records}"

    if [[ "${#missing[@]}" -gt 0 ]] ||
       [[ "${#import_failed[@]}" -gt 0 ]]; then
        echo "" >&2
        if [[ "${#missing[@]}" -gt 0 ]]; then
            echo "bootstrap: missing Python modules: ${missing[*]}" >&2
            echo "bootstrap: install with: ${PYTHON} -m pip install -r requirements.txt" >&2
        fi
        if [[ "${#import_failed[@]}" -gt 0 ]]; then
            echo "bootstrap: modules present but failed to import: ${import_failed[*]}" >&2
            echo "bootstrap: the installation may be broken — try reinstalling." >&2
        fi
        exit 1
    fi
}
# --- end check_python_modules ---

# --- check_env_vars ---
check_env_vars() {
    # Verify required environment variables are set and non-empty.
    # Always checks: SNOMED_LOG_DIR, SNOMED_LOG_LEVEL.
    # If TNS_ADMIN is set (OCI), also checks: TNS_ADMIN,
    # SNOMED_DB_PASSWORD, SNOMED_STAGE_DB_PASSWORD.
    # Accumulates all failures before reporting — missing vars are
    # independent and knowing all of them at once is more useful than
    # stopping at the first.
    # Exits 1 if any required variable is missing, listing all.
    #
    # NOTE (pending, tracked as a required follow-up): this list is
    # still a hardcoded bash array. Under the single-source-of-truth
    # rule agreed for this project, it should move to a YAML config
    # read via a new src/common/read_required_env_vars.py, mirroring
    # check_required_dirs. This is safe to do with YAML (not JSON):
    # check_env_vars already runs after check_python_modules, so
    # PyYAML is proven present by the time this would read a YAML
    # file. Not yet done — deferred to repository maintenance
    # (todo.md §6.2), not scheduled immediately after this revision.
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

# --- resolve_nearest_existing_ancestor ---
resolve_nearest_existing_ancestor() {
    # Walk up from the given path until an existing directory is
    # found. PROJECT_ROOT itself is guaranteed to exist (verified in
    # resolve_project_root), so this always terminates there at the
    # latest.
    local path="$1"
    while [[ ! -d "${path}" ]]; do
        path="$(dirname "${path}")"
    done
    echo "${path}"
}
# --- end resolve_nearest_existing_ancestor ---

# --- check_required_dirs ---
check_required_dirs() {
    # Ensure all required directories exist, creating any that are
    # missing. Reads the directory list from
    # config/directory_structure.yaml via src/common/read_required_dirs.py.
    #
    # Validates each returned path against traversal and symlink-escape
    # attacks before and after creation (defense in depth — the helper
    # already validates path safety on the string, but this function
    # must not rely on that validation alone):
    #   1. Literal-string checks: no leading "/", no trailing "/", no
    #      repeated "//", and no exact "." or ".." path component.
    #      Checked component-by-component after the structural checks,
    #      not via substring matching, so a legitimate name like
    #      "archive..old" is not rejected.
    #   2. Pre-creation containment check: the nearest existing
    #      ancestor of the target path must resolve inside
    #      PROJECT_ROOT. This runs BEFORE mkdir -p, because mkdir -p
    #      would otherwise create directories through an
    #      outside-pointing symlink before any escape could be
    #      detected.
    #   3. Post-creation containment check: the final resolved
    #      directory must still resolve inside PROJECT_ROOT, catching
    #      a symlink introduced within the newly created path itself.
    #      CREATED is only printed after this check passes, so
    #      bootstrap never announces success for a directory that
    #      turns out to violate containment.
    #
    # An empty record from the helper is treated as a protocol
    # violation and fails loudly rather than being silently skipped.
    #
    # Exits 1 if the directory list cannot be read, is empty, contains
    # unsafe paths, escapes PROJECT_ROOT via a symlink, or a directory
    # cannot be created.
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
    TEMP_FILES+=("${helper_err}")

    if ! dirs=$("${PYTHON}" "${read_required_dirs}" 2>"${helper_err}"); then
        echo "bootstrap: failed to read required directories:" >&2
        cat "${helper_err}" >&2
        exit 1
    fi

    if [[ -z "${dirs}" ]]; then
        echo "bootstrap: required directory list is empty." >&2
        echo "bootstrap: check config/directory_structure.yaml and read_required_dirs.py." >&2
        exit 1
    fi

    while IFS= read -r dir; do
        if [[ -z "${dir}" ]]; then
            echo "bootstrap: read_required_dirs.py produced an empty record." >&2
            echo "bootstrap: this indicates a helper protocol violation." >&2
            exit 1
        fi

        # Structural literal-string checks.
        if [[ "${dir}" = /* ]]; then
            echo "bootstrap: unsafe absolute path from helper: ${dir}" >&2
            exit 1
        fi
        if [[ "${dir}" = */ ]]; then
            echo "bootstrap: unsafe trailing slash in path from helper: ${dir}" >&2
            exit 1
        fi
        if [[ "${dir}" == *//* ]]; then
            echo "bootstrap: unsafe repeated slash in path from helper: ${dir}" >&2
            exit 1
        fi

        # Exact-component checks (not substring matching — a name like
        # "archive..old" must not be rejected).
        local dir_parts part
        IFS='/' read -ra dir_parts <<< "${dir}"
        for part in "${dir_parts[@]}"; do
            if [[ "${part}" == "." ]] || [[ "${part}" == ".." ]] || [[ -z "${part}" ]]; then
                echo "bootstrap: unsafe path component in: ${dir}" >&2
                exit 1
            fi
        done

        full_path="${PROJECT_ROOT}/${dir}"

        # Pre-creation containment check.
        local ancestor resolved_ancestor
        ancestor="$(resolve_nearest_existing_ancestor "${full_path}")"
        if ! resolved_ancestor="$(cd "${ancestor}" && pwd -P)"; then
            echo "bootstrap: failed to resolve ancestor of: ${full_path}" >&2
            exit 1
        fi
        if [[ "${resolved_ancestor}" != "${RESOLVED_ROOT}" ]] \
            && [[ "${resolved_ancestor}" != "${RESOLVED_ROOT}/"* ]]; then
            echo "bootstrap: refusing to create — an existing ancestor" >&2
            echo "bootstrap: escapes PROJECT_ROOT via symlink: ${dir}" >&2
            echo "bootstrap: ancestor resolves to: ${resolved_ancestor}" >&2
            exit 1
        fi

        local created=0
        if [[ -d "${full_path}" ]]; then
            :
        else
            if ! mkdir -p "${full_path}"; then
                echo "bootstrap: failed to create directory: ${full_path}" >&2
                echo "bootstrap: check permissions on: ${PROJECT_ROOT}" >&2
                exit 1
            fi
            created=1
        fi

        # Post-creation containment check — must pass before announcing
        # success (see function docstring).
        local resolved_full_path
        if ! resolved_full_path="$(cd "${full_path}" && pwd -P)"; then
            echo "bootstrap: failed to resolve created directory: ${full_path}" >&2
            exit 1
        fi
        if [[ "${resolved_full_path}" != "${RESOLVED_ROOT}" ]] \
            && [[ "${resolved_full_path}" != "${RESOLVED_ROOT}/"* ]]; then
            echo "bootstrap: directory escapes PROJECT_ROOT via symlink: ${dir}" >&2
            echo "bootstrap: resolved to: ${resolved_full_path}" >&2
            exit 1
        fi

        if [[ "${created}" -eq 1 ]]; then
            echo "  CREATED  ${dir}"
        else
            echo "  OK       ${dir}"
        fi
    done <<< "${dirs}"
}
# --- end check_required_dirs ---

# --- print_environment_summary ---
print_environment_summary() {
    # Print a concise summary of resolved environment values and
    # check results. Called only after every check has passed — each
    # check function exits immediately on failure, so reaching this
    # point means all listed results are OK.
    echo ""
    echo "=== Environment summary ==="
    echo "Project root: ${RESOLVED_ROOT}"
    echo "Virtual environment: ${resolved_venv}"
    echo "Python executable: ${PYTHON}"
    echo "Python version: ${PYTHON_VERSION}"
    echo "Mode: local"
    echo "Check results:"
    echo "  Project root: OK"
    echo "  Virtual environment: OK"
    echo "  Python executable: OK"
    echo "  Required modules: OK"
    echo "  Environment variables: OK"
    echo "  Required directories: OK"
}
# --- end print_environment_summary ---

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

    trap cleanup_temp_files EXIT

    resolve_project_root
    check_venv
    check_python3
    check_python_modules
    check_env_vars
    check_required_dirs

    print_environment_summary
    echo "bootstrap: all checks passed. Environment is ready."
}
# --- end main ---

main "$@"
