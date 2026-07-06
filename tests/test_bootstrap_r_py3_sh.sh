# ARC_FILE: tests/test_bootstrap_r_py3_sh.sh
# tests/test_bootstrap_r_py3_sh.sh
# Inserted tests for scripts/bootstrap.sh — check_python3.
#
# Not numbered as a Round (Rounds 1-4 numbering is preserved). This
# function sits between check_venv (Round 2) and check_python_modules
# (Round 3) in main's call order and had no dedicated coverage.
#
# Tests that bootstrap.sh:
#   - succeeds and reports OK when the active venv python3 is valid
#   - runs check_python3 only after check_venv has passed (ordering)
#   - fails clearly if python3 is not found on PATH
#   - fails clearly if `python3 -c "import sys; print(sys.executable)"` errors
#   - fails clearly if sys.executable reports an empty path
#   - fails clearly if the reported python3 is outside the active venv
#   - warns but does NOT fail if the Python version is below 3.12
#
# All tests use REAL_PROJECT_ROOT as PROJECT_ROOT so the real venv is
# inside PROJECT_ROOT and check_venv passes before check_python3 runs.
# Failure/warning cases inject a fake python3 via PATH that matches on
# the exact `-c` code string check_python3 invokes, delegating anything
# unmatched to the real python3.
#
# Usage:
#   bash tests/test_bootstrap_r_py3_sh.sh
#
# Preconditions:
#   venv active with oracledb, omegaconf, pyyaml installed (so tests
#   that fall through to later checks don't fail for unrelated reasons).
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.0
# Last modified: 2026-07-05
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REAL_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${REAL_PROJECT_ROOT}/scripts/bootstrap.sh"
REAL_PYTHON3="$(command -v python3)"

PASS="PASS"
FAIL="FAIL"
RESULTS_FILE="$(mktemp)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    # Run bootstrap with real PROJECT_ROOT and venv.
    # Optional: prepend a directory to PATH for fake python3 injection.
    # Args:
    #   $1 — optional fake bin dir to prepend to PATH (or empty string)
    local fake_bin="${1:-}"

    local path_prefix=""
    if [[ -n "${fake_bin}" ]]; then
        path_prefix="${fake_bin}:"
    fi

    PATH="${path_prefix}${PATH}" \
    VIRTUAL_ENV="${REAL_PROJECT_ROOT}/venv" \
    PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
    bash "${BOOTSTRAP}" 2>&1
}
# --- end run_bootstrap ---

# --- make_bin_dir_without_python3 ---
make_bin_dir_without_python3() {
    # Build a bin dir containing symlinks to every command currently
    # reachable on PATH, EXCEPT python3, preserving PATH-order
    # precedence (first match wins). Used to simulate python3 being
    # absent without breaking the coreutils bootstrap.sh itself needs.
    # Args:
    #   $1 — bin dir to populate
    local bin_dir="$1"
    local dir cmd_path cmd

    IFS=':' read -ra dirs <<< "${PATH}"
    for dir in "${dirs[@]}"; do
        [[ -d "${dir}" ]] || continue
        for cmd_path in "${dir}"/*; do
            [[ -f "${cmd_path}" && -x "${cmd_path}" ]] || continue
            cmd="$(basename "${cmd_path}")"
            [[ "${cmd}" == "python3" ]] && continue
            [[ -e "${bin_dir}/${cmd}" ]] && continue
            ln -sf "${cmd_path}" "${bin_dir}/${cmd}"
        done
    done
}
# --- end make_bin_dir_without_python3 ---

# --- run_bootstrap_with_path ---
run_bootstrap_with_path() {
    # Run bootstrap with a fully overridden PATH (no prefixing).
    # Args:
    #   $1 — full PATH value to use
    local full_path="$1"

    PATH="${full_path}" \
    VIRTUAL_ENV="${REAL_PROJECT_ROOT}/venv" \
    PROJECT_ROOT="${REAL_PROJECT_ROOT}" \
    bash "${BOOTSTRAP}" 2>&1
}
# --- end run_bootstrap_with_path ---

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- test_succeeds_with_valid_venv_python3 ---
test_succeeds_with_valid_venv_python3() {
    local rc=0
    local output
    output=$(run_bootstrap "") || rc=$?

    if [[ "${rc}" -eq 0 ]] && echo "${output}" | grep -q "OK       .*python3"; then
        report "succeeds with valid venv python3" "${PASS}"
    else
        report "succeeds with valid venv python3" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_succeeds_with_valid_venv_python3 ---

# --- test_python3_check_runs_after_venv_check ---
test_python3_check_runs_after_venv_check() {
    # No venv active — should fail in check_venv and never reach
    # check_python3's "Checking python3..." heading.
    local fake_root
    fake_root=$(mktemp -d)

    local rc=0
    local output
    output=$(
        env -u VIRTUAL_ENV \
        PROJECT_ROOT="${fake_root}" \
        bash "${BOOTSTRAP}" 2>&1
    ) || rc=$?

    rm -rf "${fake_root}"

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "no virtual environment is active" \
        && ! echo "${output}" | grep -q "Checking python3"; then
        report "python3 check runs after venv check" "${PASS}"
    else
        report "python3 check runs after venv check" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_python3_check_runs_after_venv_check ---

# --- test_fails_when_python3_not_on_path ---
test_fails_when_python3_not_on_path() {
    local fake_bin
    fake_bin=$(mktemp -d)
    make_bin_dir_without_python3 "${fake_bin}"

    local rc=0
    local output
    output=$(run_bootstrap_with_path "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] && echo "${output}" | grep -q "python3 not found on PATH"; then
        report "fails when python3 not found on PATH" "${PASS}"
    else
        report "fails when python3 not found on PATH" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_python3_not_on_path ---

# --- test_fails_when_sys_executable_command_fails ---
test_fails_when_sys_executable_command_fails() {
    local fake_bin
    fake_bin=$(mktemp -d)

    cat > "${fake_bin}/python3" << PYSCRIPT
#!/bin/bash
# Fails the sys.executable query, delegates everything else.
if [[ "\$*" == *"print(sys.executable)"* ]]; then
    echo "RuntimeError: simulated failure" >&2
    exit 1
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_bin}/python3"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "python3 failed to report its executable path"; then
        report "fails when sys.executable command fails" "${PASS}"
    else
        report "fails when sys.executable command fails" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_sys_executable_command_fails ---

# --- test_fails_when_sys_executable_empty ---
test_fails_when_sys_executable_empty() {
    local fake_bin
    fake_bin=$(mktemp -d)

    cat > "${fake_bin}/python3" << PYSCRIPT
#!/bin/bash
# Returns an empty string for the sys.executable query, delegates rest.
if [[ "\$*" == *"print(sys.executable)"* ]]; then
    echo ""
    exit 0
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_bin}/python3"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "python3 returned an empty executable path"; then
        report "fails when sys.executable is empty" "${PASS}"
    else
        report "fails when sys.executable is empty" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_sys_executable_empty ---

# --- test_fails_when_python3_outside_venv ---
test_fails_when_python3_outside_venv() {
    local fake_bin
    fake_bin=$(mktemp -d)

    cat > "${fake_bin}/python3" << PYSCRIPT
#!/bin/bash
# Reports a fixed path outside any venv for sys.executable, delegates rest.
if [[ "\$*" == *"print(sys.executable)"* ]]; then
    echo "/opt/not-a-venv/bin/python3"
    exit 0
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_bin}/python3"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 1 ]] \
        && echo "${output}" | grep -q "python3 is not from the active venv" \
        && echo "${output}" | grep -q "python3 reports: /opt/not-a-venv/bin/python3" \
        && echo "${output}" | grep -q "expected inside: ${REAL_PROJECT_ROOT}/venv"; then
        report "fails when python3 is outside the active venv" "${PASS}"
    else
        report "fails when python3 is outside the active venv" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_fails_when_python3_outside_venv ---

# --- test_warns_but_succeeds_when_version_below_3_12 ---
test_warns_but_succeeds_when_version_below_3_12() {
    # Delegate sys.executable to the real venv python (so the venv
    # check passes) but fake the version queries as 3.9.
    local fake_bin
    fake_bin=$(mktemp -d)

    cat > "${fake_bin}/python3" << PYSCRIPT
#!/bin/bash
if [[ "\$*" == *"version_info[:2]"* ]]; then
    echo "3.9"
    exit 0
elif [[ "\$*" == *"version_info.major"* ]]; then
    echo "3"
    exit 0
elif [[ "\$*" == *"version_info.minor"* ]]; then
    echo "9"
    exit 0
fi
exec "${REAL_PYTHON3}" "\$@"
PYSCRIPT
    chmod +x "${fake_bin}/python3"

    local rc=0
    local output
    output=$(run_bootstrap "${fake_bin}") || rc=$?

    rm -rf "${fake_bin}"

    if [[ "${rc}" -eq 0 ]] \
        && echo "${output}" | grep -q "WARN     python3 version 3.9 (ACE target: >= 3.12)"; then
        report "warns but succeeds on version below 3.12" "${PASS}"
    else
        report "warns but succeeds on version below 3.12" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_warns_but_succeeds_when_version_below_3_12 ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r_py3_sh.sh -- check_python3 (inserted, no round number) ==="
    echo ""

    test_succeeds_with_valid_venv_python3
    test_python3_check_runs_after_venv_check
    test_fails_when_python3_not_on_path
    test_fails_when_sys_executable_command_fails
    test_fails_when_sys_executable_empty
    test_fails_when_python3_outside_venv
    test_warns_but_succeeds_when_version_below_3_12

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
