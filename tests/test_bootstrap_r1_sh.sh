# ARC_FILE: tests/test_bootstrap_r1_sh.sh
# tests/test_bootstrap_r1_sh.sh
# Round 1 tests for scripts/bootstrap.sh — required directory check.
#
# Tests that bootstrap.sh:
#   - reports existing directories as OK
#   - creates missing directories
#   - exits 0 on success
#   - fails clearly if PROJECT_ROOT is set but does not exist
#   - fails clearly if read_required_dirs.py is missing
#   - prints usage with -h/--help
#   - rejects unknown arguments
#   - auto-detects PROJECT_ROOT when unset
#   - uses PROJECT_ROOT as override when set
#
# Happy-path tests use REAL_PROJECT_ROOT as PROJECT_ROOT so the real
# venv is inside PROJECT_ROOT and all checks pass. A temporary
# directory_structure.yaml override is not possible without patching,
# so these tests accept that real project dirs are checked/created.
# This remains a stated, accepted limitation, not an oversight — an
# isolated-fixture-root redesign that would lift it, and matching
# coverage of bootstrap's own independent directory-safety checks
# (absolute path / ".." / symlink-escape rejection), are recorded as a
# deferred backlog item (todo.md §6) rather than folded into this
# revision.
#
# Every successful bootstrap invocation may create any currently
# missing directory from the production registry
# (config/directory_structure.yaml), not just the ones the two
# deliberately mutating tests below touch. A suite preflight
# (verify_all_required_dirs_exist) therefore confirms every
# production-required directory already exists before any ordinary
# test runs, and fails the whole suite immediately if not — so
# test_creates_missing_directory remains the only intentional
# directory-removal/recreation case, and no other test can silently
# create a real directory that merely happened to be absent.
#
# Two tests still deliberately mutate the real project tree for the
# duration of a single check (renaming src/common/read_required_dirs.py;
# removing sql/ddl/tables). Both verify the specific file/directory
# they are about to touch is present, a regular file/directory, and
# not a symlink before mutating — not merely that a backup path is
# absent — restore immediately in the normal path, and are backed by
# a single suite-level EXIT trap (cleanup_suite) that idempotently
# restores the real tree and removes every suite-owned temporary
# file/directory on any exit — normal, failed, or interrupted.
#
# This suite assumes exclusive access to the real repository tree for
# its duration: no other process should modify
# src/common/read_required_dirs.py or sql/ddl/tables while it runs.
# Real-tree mutation cannot be made concurrency-safe without the
# isolated-root redesign referenced above, which will remove this
# requirement entirely.
#
# All bootstrap invocations set SNOMED_LOG_DIR/SNOMED_LOG_LEVEL
# explicitly and unset any inherited TNS_ADMIN, so results depend on
# this fixture, not on the caller's shell environment.
#
# Usage:
#   bash tests/test_bootstrap_r1_sh.sh
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.9
# Last modified: 2026-09-14
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REAL_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${REAL_PROJECT_ROOT}/scripts/bootstrap.sh"

PASS="PASS"
FAIL="FAIL"

# Suite-owned temporary/mutation-tracking state. Declared empty/zero
# here, before cleanup_suite is defined and installed as the EXIT
# trap, and before any of them is actually populated (mktemp, venv
# detection, etc. below) — so if any step that populates one of these
# fails partway through, the trap is already active and its
# ${var:-}/"${var}" guards correctly clean up whatever was created so
# far, rather than leaking a resource created before the trap existed.
RESULTS_FILE=""
SUITE_LOG_DIR=""
SUITE_LOG_LEVEL="INFO"
HELPER="${REAL_PROJECT_ROOT}/src/common/read_required_dirs.py"
HELPER_BACKUP="${HELPER}.bak"
TEST_DIR="${REAL_PROJECT_ROOT}/sql/ddl/tables"
TEST_DIR_GITKEEP="${TEST_DIR}/.gitkeep"
# Set to 1 by test_creates_missing_directory immediately before it
# removes TEST_DIR, if a .gitkeep was present at that point. Read by
# cleanup_suite. Left at 0 otherwise, so the trap is a no-op with
# respect to the .gitkeep question for the rest of the run.
TEST_DIR_HAD_GITKEEP=0
# Set by test_fails_when_project_root_does_not_exist to its
# process-owned temp directory, so cleanup_suite can remove it if the
# test's own cleanup doesn't run. Empty otherwise.
BOGUS_ROOT_DIR=""
REAL_VENV=""
# Armed (set to 1) immediately before the corresponding mutating
# command in each mutating test, and disarmed (set back to 0) right
# after that test's own normal-path restore completes. Gates
# cleanup_suite's real-tree restoration so the trap only acts on state
# this suite itself mutated -- never on pre-existing repository state
# it merely observed (e.g. a stray .bak left by something unrelated,
# or TEST_DIR already missing when the preflight below checks it).
HELPER_MOVED=0
TEST_DIR_REMOVED=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# --- detect_venv_dir ---
detect_venv_dir() {
    # Find the single immediate subdirectory of REAL_PROJECT_ROOT that
    # contains bin/activate. Returns its path without trailing slash.
    # Refuses to guess: exits 1 with a message if none is found, or if
    # more than one candidate is found (ambiguous — remove or rename
    # the extra one(s) rather than silently picking the first match).
    local d
    local -a candidates=()
    for d in "${REAL_PROJECT_ROOT}"/*/; do
        [[ -f "${d}bin/activate" ]] && candidates+=("${d%/}")
    done

    if [[ "${#candidates[@]}" -eq 0 ]]; then
        echo "bootstrap test: no venv found under ${REAL_PROJECT_ROOT}" >&2
        return 1
    fi
    if [[ "${#candidates[@]}" -gt 1 ]]; then
        echo "bootstrap test: multiple candidate venvs found under ${REAL_PROJECT_ROOT}: ${candidates[*]}" >&2
        echo "bootstrap test: refusing to guess which is active -- remove or rename the extra one(s)." >&2
        return 1
    fi

    echo "${candidates[0]}"
}
# --- end detect_venv_dir ---

# --- cleanup_suite ---
cleanup_suite() {
    # EXIT trap: idempotently restore any real-tree mutation this
    # suite ever performs, and remove every suite-owned temporary
    # file/directory, regardless of why or when the script is exiting.
    # Safe to run even when the corresponding normal-path restore
    # already completed -- each action is guarded by a check of
    # current state, so a second call is a no-op. Also safe to run
    # when some of these were never populated (e.g. an early failure
    # before they were created) -- every reference is guarded.
    if [[ "${HELPER_MOVED}" -eq 1 ]]; then
        if [[ ! -f "${HELPER}" ]] && [[ -f "${HELPER_BACKUP}" ]]; then
            mv -- "${HELPER_BACKUP}" "${HELPER}" || true
        fi
    fi

    if [[ "${TEST_DIR_REMOVED}" -eq 1 ]]; then
        if [[ ! -d "${TEST_DIR}" ]]; then
            mkdir -p "${TEST_DIR}" || true
        fi
        if [[ "${TEST_DIR_HAD_GITKEEP}" -eq 1 ]] && [[ ! -f "${TEST_DIR_GITKEEP}" ]]; then
            touch "${TEST_DIR_GITKEEP}" || true
        fi
    fi

    if [[ -n "${RESULTS_FILE}" ]]; then
        rm -f -- "${RESULTS_FILE}"
    fi
    if [[ -n "${SUITE_LOG_DIR}" ]]; then
        rm -rf -- "${SUITE_LOG_DIR}"
    fi
    if [[ -n "${BOGUS_ROOT_DIR}" ]]; then
        rm -rf -- "${BOGUS_ROOT_DIR}"
    fi

    # Explicit success return regardless of which branches above were
    # taken. Under set -e, if this trap's last executed command has a
    # nonzero exit status, that status silently overrides the actual
    # exit 0/1 from main() -- confirmed by direct reproduction. The
    # three guards above are written as if/fi specifically so a false
    # condition contributes status 0, not a short-circuited nonzero
    # status; this return 0 is a second, independent safeguard against
    # the same class of bug being reintroduced by a future edit.
    return 0
}
# --- end cleanup_suite ---

trap cleanup_suite EXIT

# Resource creation happens only after the trap above is installed,
# per the ordering rationale in the Constants block comment.
RESULTS_FILE="$(mktemp)"
SUITE_LOG_DIR="$(mktemp -d)"
REAL_VENV="$(detect_venv_dir)"

# --- verify_all_required_dirs_exist ---
verify_all_required_dirs_exist() {
    # Suite preflight, not an individual test: confirm every directory
    # the production registry currently requires already exists,
    # before any ordinary (non-mutating) bootstrap test runs. Every
    # successful bootstrap invocation may silently create any missing
    # required directory from config/directory_structure.yaml, so
    # without this check, any test that merely runs bootstrap could
    # itself mutate the real tree.
    #
    # Reads the required list via the real, current helper script
    # itself (not a hardcoded copy in this test file), so this check
    # cannot silently drift out of sync with
    # config/directory_structure.yaml.
    #
    # Exits 1 immediately, not via report(), because this is a
    # precondition for running the suite at all, not an individual
    # test outcome: create the missing directories manually, or run
    # bootstrap once outside this suite, then re-run.
    local python_bin="${REAL_VENV}/bin/python3"
    local read_required_dirs="${REAL_PROJECT_ROOT}/src/common/read_required_dirs.py"
    local dirs
    local dir
    local -a missing=()

    if ! dirs="$("${python_bin}" "${read_required_dirs}" 2>&1)"; then
        echo "bootstrap test: preflight failed to read required directories:" >&2
        echo "${dirs}" >&2
        exit 1
    fi

    while IFS= read -r dir; do
        [[ -z "${dir}" ]] && continue
        if [[ ! -d "${REAL_PROJECT_ROOT}/${dir}" ]]; then
            missing+=("${dir}")
        fi
    done <<< "${dirs}"

    if [[ "${#missing[@]}" -gt 0 ]]; then
        echo "bootstrap test: required directories missing before suite start: ${missing[*]}" >&2
        echo "bootstrap test: create them manually, or run bootstrap.sh once outside this suite, then re-run." >&2
        exit 1
    fi
}
# --- end verify_all_required_dirs_exist ---

verify_all_required_dirs_exist

# --- report ---
report() {
    local name="$1"
    local result="$2"
    local detail="${3:-}"
    if [[ -n "${detail}" ]]; then
        echo "${result}: ${name} -- ${detail}"
    else
        echo "${result}: ${name}"
    fi
    echo "${result}" >> "${RESULTS_FILE}"
}
# --- end report ---

# --- run_bootstrap ---
run_bootstrap() {
    # Run bootstrap against REAL_PROJECT_ROOT with the real venv
    # active and isolated, explicit values for every environment
    # variable check_env_vars reads -- so results depend on this
    # fixture, not on the caller's shell. TNS_ADMIN is explicitly
    # unset so an inherited value cannot silently switch bootstrap
    # into OCI mode and demand database password variables this
    # fixture does not provide.
    # Args:
    #   $@ — arguments passed to bootstrap
    VIRTUAL_ENV="${REAL_VENV}" \
    PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
    SNOMED_LOG_DIR="${SUITE_LOG_DIR}" \
    SNOMED_LOG_LEVEL="${SUITE_LOG_LEVEL}" \
    env -u TNS_ADMIN \
    bash "${BOOTSTRAP}" "$@" 2>&1
}
# --- end run_bootstrap ---

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_exits_zero_on_success ---
test_exits_zero_on_success() {
    local rc=0
    run_bootstrap > /dev/null || rc=$?

    if [[ "${rc}" -eq 0 ]]; then
        report "exits zero on success" "${PASS}"
    else
        report "exits zero on success" "${FAIL}" "exit code=${rc}"
    fi
}
# --- end test_exits_zero_on_success ---

# --- test_reports_existing_directories_as_ok ---
test_reports_existing_directories_as_ok() {
    local rc=0
    local output
    output=$(run_bootstrap) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -Fq "OK       log"; then
        report "reports existing directories as OK" "${PASS}"
    else
        report "reports existing directories as OK" "${FAIL}" "rc=${rc}"
    fi
}
# --- end test_reports_existing_directories_as_ok ---

# --- test_creates_missing_directory ---
test_creates_missing_directory() {
    # Temporarily remove a required dir, run bootstrap, verify it
    # recreates it. Uses sql/ddl/tables.
    #
    # Preconditions, checked before any mutation: TEST_DIR must exist,
    # be a real directory, and not a symlink; if TEST_DIR_GITKEEP
    # exists, it must be a regular file and not a symlink. On failure
    # of either, the test reports a controlled failure and returns
    # without touching anything -- rather than letting `find` on a
    # missing/unreadable TEST_DIR abort the whole suite under
    # set -euo pipefail, or acting on an unexpected symlink.
    #
    # Also verifies TEST_DIR's actual contents before removing it,
    # rather than assuming it holds nothing but .gitkeep: if anything
    # else is present, the test refuses to touch the directory and
    # fails loudly instead of silently deleting unexpected real
    # content.
    #
    # Restores unconditionally on current state afterward (not gated
    # on the run having succeeded), so a bootstrap failure here does
    # not leave the real tree permanently altered. The top-level
    # cleanup_suite EXIT trap is an additional safety net for
    # interruption between the verified rm and this point.
    if [[ ! -d "${TEST_DIR}" ]] || [[ -L "${TEST_DIR}" ]]; then
        report "creates missing directory" "${FAIL}" \
            "precondition failed: ${TEST_DIR} is not a plain existing directory"
        return
    fi
    if [[ -e "${TEST_DIR_GITKEEP}" ]]; then
        if [[ ! -f "${TEST_DIR_GITKEEP}" ]] || [[ -L "${TEST_DIR_GITKEEP}" ]]; then
            report "creates missing directory" "${FAIL}" \
                "precondition failed: ${TEST_DIR_GITKEEP} exists but is not a plain regular file"
            return
        fi
    fi

    local entry_count
    entry_count="$(find "${TEST_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l)"

    if [[ "${entry_count}" -gt 1 ]] || \
       { [[ "${entry_count}" -eq 1 ]] && [[ ! -f "${TEST_DIR_GITKEEP}" ]]; }; then
        report "creates missing directory" "${FAIL}" \
            "refusing to remove ${TEST_DIR}: contains unexpected content (entry_count=${entry_count})"
        return
    fi

    local had_gitkeep=0
    [[ -f "${TEST_DIR_GITKEEP}" ]] && had_gitkeep=1
    TEST_DIR_HAD_GITKEEP="${had_gitkeep}"

    TEST_DIR_REMOVED=1
    rm -rf -- "${TEST_DIR}"

    local rc=0
    run_bootstrap > /dev/null || rc=$?

    local dir_exists=0
    [[ -d "${TEST_DIR}" ]] && dir_exists=1

    # Unconditional restore: recreate the directory if bootstrap
    # didn't, and restore .gitkeep if it was present before the test.
    if [[ "${dir_exists}" -eq 0 ]]; then
        mkdir -p "${TEST_DIR}"
    fi
    if [[ "${had_gitkeep}" -eq 1 ]]; then
        touch "${TEST_DIR_GITKEEP}"
    fi
    TEST_DIR_HAD_GITKEEP=0
    TEST_DIR_REMOVED=0

    if [[ "${rc}" -eq 0 ]] && [[ "${dir_exists}" -eq 1 ]]; then
        report "creates missing directory" "${PASS}"
    else
        report "creates missing directory" "${FAIL}" "rc=${rc} dir_exists=${dir_exists}"
    fi
}
# --- end test_creates_missing_directory ---

# --- test_auto_detects_project_root_when_unset ---
test_auto_detects_project_root_when_unset() {
    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${REAL_VENV}" \
        SNOMED_LOG_DIR="${SUITE_LOG_DIR}" \
        SNOMED_LOG_LEVEL="${SUITE_LOG_LEVEL}" \
        env -u PROJECT_ROOT -u TNS_ADMIN \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -Fq "Auto-detected PROJECT_ROOT"; then
        report "auto-detects PROJECT_ROOT when unset" "${PASS}"
    else
        report "auto-detects PROJECT_ROOT when unset" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_auto_detects_project_root_when_unset ---

# --- test_override_used_when_project_root_set ---
test_override_used_when_project_root_set() {
    local rc=0
    local output
    output=$(run_bootstrap) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -Fq "Using PROJECT_ROOT (override)"; then
        report "override used when PROJECT_ROOT set" "${PASS}"
    else
        report "override used when PROJECT_ROOT set" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_override_used_when_project_root_set ---

# --- test_fails_when_project_root_does_not_exist ---
test_fails_when_project_root_does_not_exist() {
    # Uses a process-owned temporary directory with a nonexistent
    # child path, rather than a predictable, shared /tmp path that
    # could belong to another process or user. No rm -rf of a
    # predictable path is performed; the owned parent is registered in
    # BOGUS_ROOT_DIR for cleanup_suite to remove if this function's
    # own cleanup doesn't run.
    local owner_dir bogus
    owner_dir="$(mktemp -d)"
    BOGUS_ROOT_DIR="${owner_dir}"
    bogus="${owner_dir}/does-not-exist"

    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${REAL_VENV}" \
        PROJECT_ROOT="${bogus}" \
        SNOMED_LOG_DIR="${SUITE_LOG_DIR}" \
        SNOMED_LOG_LEVEL="${SUITE_LOG_LEVEL}" \
        env -u TNS_ADMIN \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    rm -rf -- "${owner_dir}"
    BOGUS_ROOT_DIR=""

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -Fq "PROJECT_ROOT does not exist"; then
        report "fails when PROJECT_ROOT does not exist" "${PASS}"
    else
        report "fails when PROJECT_ROOT does not exist" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_project_root_does_not_exist ---

# --- test_help_flag_prints_usage ---
test_help_flag_prints_usage() {
    local rc=0
    local output
    output=$(run_bootstrap --help) || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -Fq "Usage: bash scripts/bootstrap.sh"; then
        report "help flag prints usage" "${PASS}"
    else
        report "help flag prints usage" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_help_flag_prints_usage ---

# --- test_unknown_argument_rejected ---
test_unknown_argument_rejected() {
    local rc=0
    local output
    output=$(run_bootstrap --unknown-flag 2>&1) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -Fq "unknown argument"; then
        report "unknown argument rejected" "${PASS}"
    else
        report "unknown argument rejected" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_unknown_argument_rejected ---

# --- test_fails_when_helper_missing ---
test_fails_when_helper_missing() {
    # Temporarily rename the real helper, run bootstrap, restore it
    # immediately afterward.
    #
    # Preconditions, checked before any mutation: HELPER must exist,
    # be a regular file, and not a symlink; HELPER_BACKUP must not
    # already exist (a backup left by a previous interrupted run would
    # otherwise be silently overwritten by the mv below). On failure
    # of either, the test reports a controlled failure and returns
    # without touching anything.
    #
    # The top-level cleanup_suite EXIT trap is a safety net for the
    # case where the restore mv itself fails under set -e, or the
    # script is interrupted between the two mv calls -- previously
    # this left the real, tracked helper renamed to .bak on disk with
    # no restoration path.
    if [[ ! -f "${HELPER}" ]] || [[ -L "${HELPER}" ]]; then
        report "fails when helper script missing" "${FAIL}" \
            "precondition failed: ${HELPER} is not a plain existing regular file"
        return
    fi
    if [[ -e "${HELPER_BACKUP}" ]]; then
        report "fails when helper script missing" "${FAIL}" \
            "refusing to proceed: backup path already exists: ${HELPER_BACKUP}"
        return
    fi

    HELPER_MOVED=1
    mv -- "${HELPER}" "${HELPER_BACKUP}"

    local rc=0
    local output
    output=$(run_bootstrap 2>&1) || rc=$?

    mv -- "${HELPER_BACKUP}" "${HELPER}"
    HELPER_MOVED=0

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -Fq "helper script not found"; then
        report "fails when helper script missing" "${PASS}"
    else
        report "fails when helper script missing" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_helper_missing ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r1_sh.sh -- Round 1 (directories) ==="
    echo ""

    test_exits_zero_on_success
    test_reports_existing_directories_as_ok
    test_creates_missing_directory
    test_auto_detects_project_root_when_unset
    test_override_used_when_project_root_set
    test_fails_when_project_root_does_not_exist
    test_help_flag_prints_usage
    test_unknown_argument_rejected
    test_fails_when_helper_missing

    echo ""
    local total passed failed
    total=$(wc -l < "${RESULTS_FILE}")
    passed=$(grep -Fcx "${PASS}" "${RESULTS_FILE}" || true)
    failed=$(grep -Fcx "${FAIL}" "${RESULTS_FILE}" || true)

    echo "Results: ${passed} passed, ${failed} failed, ${total} total."

    if [[ "${failed}" -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}
# --- end main ---

main "$@"
