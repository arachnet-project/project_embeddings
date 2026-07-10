# ARC_FILE: tests/test_bootstrap_r2_sh.sh
# tests/test_bootstrap_r2_sh.sh
# Round 2 tests for scripts/bootstrap.sh — venv check.
#
# Tests that bootstrap.sh:
#   - fails clearly if VIRTUAL_ENV is not set
#   - fails clearly if VIRTUAL_ENV is set but does not exist on disk
#   - fails clearly if VIRTUAL_ENV is outside PROJECT_ROOT
#   - succeeds when a valid venv inside PROJECT_ROOT is active
#   - venv check runs before the directory check (ordering)
#   - accepts any venv name (not hardcoded to "venv")
#
# Failure tests use a temp PROJECT_ROOT in /tmp — they stop before
# check_python3 so sys.executable is never called.
# Happy-path tests use REAL_PROJECT_ROOT as PROJECT_ROOT so the real
# venv is genuinely inside PROJECT_ROOT.
#
# The outside-PROJECT_ROOT fixture includes a bin/activate file so it
# passes bootstrap.sh's structural venv-validity check (added v1.7)
# and correctly falls through to the PROJECT_ROOT containment check
# this test is actually exercising.
#
# Usage:
#   bash tests/test_bootstrap_r2_sh.sh
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.5
# Last modified: 2026-07-10
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
RESULTS_FILE="$(mktemp)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# --- detect_venv_dir ---
detect_venv_dir() {
    # Find whichever immediate subdirectory of REAL_PROJECT_ROOT contains
    # bin/activate. Returns the path without trailing slash.
    # Exits 1 with a message if none found.
    local d
    for d in "${REAL_PROJECT_ROOT}"/*/; do
        [[ -f "${d}bin/activate" ]] && echo "${d%/}" && return 0
    done
    echo "bootstrap test: no venv found under ${REAL_PROJECT_ROOT}" >&2
    return 1
}
# --- end detect_venv_dir ---

REAL_VENV="$(detect_venv_dir)"

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

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_fails_when_virtual_env_not_set ---
test_fails_when_virtual_env_not_set() {
    # Uses /tmp project — stops at check_venv before python3 is needed.
    local fake_root
    fake_root=$(mktemp -d)

    local rc=0
    local output
    output=$(
        env -u VIRTUAL_ENV \
        PROJECT_ROOT="${fake_root}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "no virtual environment is active"; then
        report "fails when VIRTUAL_ENV not set" "${PASS}"
    else
        report "fails when VIRTUAL_ENV not set" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_fails_when_virtual_env_not_set ---

# --- test_fails_when_virtual_env_does_not_exist_on_disk ---
test_fails_when_virtual_env_does_not_exist_on_disk() {
    local fake_root
    fake_root=$(mktemp -d)

    local bogus_venv="${fake_root}/nonexistent_venv"

    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${bogus_venv}" \
        PROJECT_ROOT="${fake_root}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "does not exist"; then
        report "fails when VIRTUAL_ENV does not exist on disk" "${PASS}"
    else
        report "fails when VIRTUAL_ENV does not exist on disk" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_fails_when_virtual_env_does_not_exist_on_disk ---

# --- test_fails_when_venv_outside_project_root ---
test_fails_when_venv_outside_project_root() {
    local fake_root
    fake_root=$(mktemp -d)

    local outside_venv
    outside_venv=$(mktemp -d)
    mkdir -p "${outside_venv}/bin"
    # bin/activate must exist so the fixture passes bootstrap.sh's
    # structural venv-validity check and falls through to the
    # PROJECT_ROOT containment check this test actually targets.
    touch "${outside_venv}/bin/activate"

    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${outside_venv}" \
        PROJECT_ROOT="${fake_root}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "active venv is outside PROJECT_ROOT"; then
        report "fails when venv outside PROJECT_ROOT" "${PASS}"
    else
        report "fails when venv outside PROJECT_ROOT" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}" "${outside_venv}"
}
# --- end test_fails_when_venv_outside_project_root ---

# --- test_succeeds_when_valid_venv_inside_project_root ---
test_succeeds_when_valid_venv_inside_project_root() {
    # Use REAL_PROJECT_ROOT so venv IS inside PROJECT_ROOT and
    # sys.executable passes check_python3. Uses REAL_VENV (discovered
    # via detect_venv_dir) rather than a hardcoded name, since the venv
    # is named "venv" on Ubuntu and "wenv" on OCI.
    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${REAL_VENV}" \
        PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 0 ]] \
        && echo "${output}" | grep -q "OK       ${REAL_VENV}"; then
        report "succeeds when valid venv inside PROJECT_ROOT" "${PASS}"
    else
        report "succeeds when valid venv inside PROJECT_ROOT" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_succeeds_when_valid_venv_inside_project_root ---

# --- test_accepts_non_standard_venv_name ---
test_accepts_non_standard_venv_name() {
    # Symlink the real venv (REAL_VENV, whatever it's actually named)
    # under a clearly artificial alternate name, so both check_venv
    # and check_python3 pass regardless of the real venv's own name.
    # The alternate name is deliberately distinct from both "venv" and
    # "wenv" so it can never collide with the real venv directory on
    # either Ubuntu or OCI — a previous version hardcoded "wenv" as
    # the alternate name, which collided with OCI's real venv
    # (already named "wenv") and crashed the whole test run when
    # cleanup tried to `rm -f` a real directory.
    local alt_venv="${REAL_PROJECT_ROOT}/alt_venv_link_test"
    ln -sfn "${REAL_VENV}" "${alt_venv}"

    local rc=0
    local output
    output=$(
        VIRTUAL_ENV="${alt_venv}" \
        PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    rm -f "${alt_venv}"

    if [[ "${rc}" -eq 0 ]] \
        && echo "${output}" | grep -q "OK       ${alt_venv}"; then
        report "accepts non-standard venv name (alt_venv_link_test)" "${PASS}"
    else
        report "accepts non-standard venv name (alt_venv_link_test)" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_accepts_non_standard_venv_name ---

# --- test_venv_check_runs_before_directory_check ---
test_venv_check_runs_before_directory_check() {
    # With no venv active, output must not reach directory check.
    local fake_root
    fake_root=$(mktemp -d)

    local rc=0
    local output
    output=$(
        env -u VIRTUAL_ENV \
        PROJECT_ROOT="${fake_root}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "no virtual environment is active" \
        && ! echo "${output}" | grep -q "Checking required directories"; then
        report "venv check runs before directory check" "${PASS}"
    else
        report "venv check runs before directory check" "${FAIL}" "rc=${rc} output=${output}"
    fi

    rm -rf "${fake_root}"
}
# --- end test_venv_check_runs_before_directory_check ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r2_sh.sh -- Round 2 (venv) ==="
    echo ""

    test_fails_when_virtual_env_not_set
    test_fails_when_virtual_env_does_not_exist_on_disk
    test_fails_when_venv_outside_project_root
    test_succeeds_when_valid_venv_inside_project_root
    test_accepts_non_standard_venv_name
    test_venv_check_runs_before_directory_check

    echo ""
    local total passed failed
    total=$(wc -l < "${RESULTS_FILE}")
    passed=$(grep -c "${PASS}" "${RESULTS_FILE}" || true)
    failed=$(grep -c "${FAIL}" "${RESULTS_FILE}" || true)
    rm -f "${RESULTS_FILE}"

    echo "Results: ${passed} passed, ${failed} failed, ${total} total."

    if [[ "${failed}" -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}
# --- end main ---

main "$@"
