# ARC_FILE: tests/test_bootstrap_r3_sh.sh
# tests/test_bootstrap_r3_sh.sh
# Round 3 tests for scripts/bootstrap.sh — Python module check.
#
# Tests that bootstrap.sh:
#   - reports OK for all required modules when present
#   - reports MISSING for absent modules and accumulates all failures
#   - reports IMPORT FAILED for modules present but broken on import,
#     distinct from MISSING, and accumulates both independently
#   - exits 1 listing all missing/import-failed modules when any occur
#   - shows pip install hint on MISSING, reinstall hint on IMPORT FAILED
#   - exits 1 if required_modules.json is missing or malformed
#   - cleans up its own temporary stderr file on both a successful run
#     and a failure exit
#   - correctly classifies MISSING itself via the actual embedded
#     Python classifier (not a shell-level "exit 10" stand-in) for
#     both a plain nonexistent module name and a dotted name whose
#     required parent package is missing
#   - correctly classifies two real (not shell-faked) import failure
#     shapes via the actual embedded Python classifier: a genuinely
#     missing transitive dependency, and a module that calls
#     sys.exit() during import
#   - rejects a malicious import_name end-to-end (registry -> helper
#     validation -> bootstrap) without ever executing it and without
#     ever reaching the import-check step, and fails closed
#
# As of bootstrap.sh v1.9, check_python_modules reads its module list
# from config/required_modules.json via
# src/common/read_required_modules.py (single source of truth), and
# checks each module via a fixed importlib-based Python one-liner that
# receives the module name as sys.argv[1] rather than interpolating it
# into -c source. This distinguishes two independent failure codes:
# MISSING (module genuinely absent) and IMPORT FAILED (module present
# but raised/exited during import). This file's fakes and assertions
# target that v1.9 interface; they are not compatible with pre-v1.9
# bootstrap.sh.
#
# Scope note: this file covers check_python_modules only. The removal
# of the TNS_ADMIN-triggered SNOMED_SYS_DB_PASSWORD requirement in
# check_env_vars (also part of v1.9) belongs to the Round 4 (env vars)
# test file, not this one.
#
# Isolation architecture (dev_workflow.md §8):
#   Every test builds a fresh, disposable ISO_ROOT via build_iso_root
#   (plain mktemp -d, not nested under the real repository) containing
#   its own copies of src/common/read_required_modules.py and
#   src/common/read_required_dirs.py, its own config/, and its own
#   SNOMED_LOG_DIR. Nothing in this file ever reads, writes, renames,
#   or otherwise touches the real, tracked
#   config/required_modules.json. Each test gets its own ISO_ROOT from
#   scratch rather than sharing or resetting one, so no test can
#   influence another's fixture state.
#
#   The copies must be real file copies, not symlinks: both helpers
#   compute their default config path via
#   Path(__file__).resolve().parent.parent.parent, and .resolve()
#   follows symlinks back to the real file's location, which would
#   silently defeat the isolation.
#
#   build_iso_root must be called as a plain statement, never inside
#   command substitution — it sets the script-scoped ISO_ROOT variable
#   and registers it for cleanup directly in the suite's own shell.
#   Calling it as iso="$(build_iso_root)" would run it in a subshell,
#   silently losing its CLEANUP_PATHS registration and leaking the
#   fixture in /tmp.
#
#   PROJECT_ROOT is set to ISO_ROOT for every bootstrap invocation in
#   this file, so a venv fixture must exist inside ISO_ROOT too
#   (check_venv enforces containment). make_fake_venv builds this
#   fixture; its python3 delegates every call it is not specifically
#   simulating a failure for to REAL_PYTHON3 (the already-active,
#   already-verified ${VIRTUAL_ENV}/bin/python3 — this file does not
#   scan for or guess a venv directory).
#
#   check_env_vars is satisfied deterministically for every test by
#   pointing SNOMED_LOG_DIR at ISO_ROOT/log and setting
#   SNOMED_LOG_LEVEL explicitly, with TNS_ADMIN explicitly unset via
#   `env -u`, regardless of what the invoking shell has set. Any
#   directory check_required_dirs creates on a successful run lands
#   inside ISO_ROOT and is removed with it — never in the real tree.
#
#   All cleanup (ISO_ROOTs, the results file, and any other temporary
#   path) is tracked in the CLEANUP_PATHS array and removed by a
#   single suite-wide `trap cleanup_all EXIT`, installed as the first
#   executable statement in this script — before RESULTS_FILE or any
#   fixture is created — so a failure or interrupt at any point still
#   cleans up everything registered so far. This covers normal exit
#   and ordinary failure paths, including this script's own
#   `set -e`; it is not a guarantee against uncatchable termination
#   (e.g. SIGKILL).
#
# Usage:
#   bash tests/test_bootstrap_r3_sh.sh
#
# Preconditions:
#   A project venv is active (VIRTUAL_ENV set) with oracledb,
#   omegaconf, and PyYAML installed in it. This file uses that venv's
#   python3 directly as the real interpreter; it does not search for
#   or infer a venv directory.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.5
# Last modified: 2026-09-07
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Suite-wide cleanup — installed before any fixture exists
# ---------------------------------------------------------------------------

declare -a CLEANUP_PATHS=()

# --- cleanup_all ---
cleanup_all() {
    # Remove every registered path on script exit, without disturbing
    # the script's exit status. Installed as an EXIT trap as the very
    # first executable statement below, so it covers every fixture
    # created anywhere in this file. Runs on normal exit and ordinary
    # failure paths (including this script's own set -e); it is not a
    # guarantee against uncatchable termination such as SIGKILL.
    local exit_status=$?
    local path
    for path in "${CLEANUP_PATHS[@]:-}"; do
        [[ -n "${path}" ]] && rm -rf -- "${path}" || true
    done
    return "${exit_status}"
}
# --- end cleanup_all ---

trap cleanup_all EXIT

# --- register_cleanup ---
register_cleanup() {
    # Register a path for removal by cleanup_all. Callers must invoke
    # this immediately after a successful mktemp/mktemp -d, before
    # writing anything into the path, so a failure partway through
    # fixture construction still gets cleaned up.
    CLEANUP_PATHS+=("$1")
}
# --- end register_cleanup ---

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REAL_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${REAL_PROJECT_ROOT}/scripts/bootstrap.sh"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "test_bootstrap_r3_sh: VIRTUAL_ENV is not set." >&2
    echo "test_bootstrap_r3_sh: activate the project venv before running this suite." >&2
    exit 1
fi
REAL_VENV="${VIRTUAL_ENV}"
REAL_PYTHON3="${REAL_VENV}/bin/python3"
if [[ ! -x "${REAL_PYTHON3}" ]]; then
    echo "test_bootstrap_r3_sh: no python3 executable at ${REAL_PYTHON3}" >&2
    exit 1
fi

PASS="PASS"
FAIL="FAIL"
RESULTS_FILE="$(mktemp)"
register_cleanup "${RESULTS_FILE}"

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

# --- build_iso_root ---
ISO_ROOT=""
build_iso_root() {
    # Build a fresh, disposable isolated project root and set the
    # script-scoped ISO_ROOT to it. Must be called as a plain
    # statement (not inside command substitution) so register_cleanup
    # modifies CLEANUP_PATHS in the actual suite shell, not a subshell
    # copy that vanishes on return.
    #
    # Contains real copies (never symlinks) of both helper scripts, a
    # default valid required_modules.json (the three real project
    # modules — genuinely installed in REAL_VENV, so a passthrough
    # fake venv reports them all OK with no faking needed), a minimal
    # directory_structure.yaml, and a log/ directory for
    # SNOMED_LOG_DIR to point at.
    #
    # Callers that need different fixture content overwrite the
    # relevant file after this returns; each call produces a fresh
    # root, so no test's overwrite can affect another test.
    local root
    root="$(mktemp -d)"
    register_cleanup "${root}"
    ISO_ROOT="${root}"

    mkdir -p "${root}/src/common"
    cp "${REAL_PROJECT_ROOT}/src/common/read_required_modules.py" \
        "${root}/src/common/read_required_modules.py"
    cp "${REAL_PROJECT_ROOT}/src/common/read_required_dirs.py" \
        "${root}/src/common/read_required_dirs.py"

    mkdir -p "${root}/config"
    cat > "${root}/config/required_modules.json" << 'JSONEOF'
{
  "required_modules": [
    {"import_name": "oracledb", "package_name": "oracledb"},
    {"import_name": "omegaconf", "package_name": "omegaconf"},
    {"import_name": "yaml", "package_name": "PyYAML"}
  ]
}
JSONEOF

    cat > "${root}/config/directory_structure.yaml" << 'YAMLEOF'
required_directories:
  - wrk
YAMLEOF

    mkdir -p "${root}/log"
}
# --- end build_iso_root ---

# --- make_fake_venv ---
make_fake_venv() {
    # Build a venv fixture inside the given ISO_ROOT so check_venv's
    # containment check passes against that ISO_ROOT. Its python3
    # reports its own path for sys.executable (so bootstrap's PYTHON
    # variable resolves to this fixture), and for the module-import
    # check (detected by "importlib.import_module" appearing in "$*",
    # matching the actual text of bootstrap's fixed one-liner) touches
    # a fixture-local marker file (ISO_ROOT/.classifier_invoked) the
    # instant it enters that branch — before evaluating any
    # simulate-rule — so callers can independently observe whether the
    # classifier was ever reached at all, not just infer it from
    # bootstrap's exit code or error text. It then applies any
    # simulate-rules given, in order, before falling through to
    # REAL_PYTHON3. Every other invocation (including running
    # read_required_modules.py or read_required_dirs.py, which are
    # file-path invocations and never match either special-cased
    # pattern) delegates straight to REAL_PYTHON3.
    #
    # Args:
    #   $1        — ISO_ROOT to build the fixture inside
    #   $2, $3...  — optional "import_name:exit_code" rules, e.g.
    #                "oracledb:10" to simulate MISSING,
    #                "omegaconf:20" to simulate IMPORT FAILED.
    #                With no rules, every import delegates to the real
    #                interpreter (passthrough).
    #
    # Prints the fake venv directory path to stdout.
    local iso_root="$1"
    shift
    local rules=("$@")

    local venv="${iso_root}/.venv_fixture"
    mkdir -p "${venv}/bin"
    touch "${venv}/bin/activate"
    local fake_python="${venv}/bin/python3"
    local marker="${iso_root}/.classifier_invoked"

    {
        echo '#!/bin/bash'
        printf 'REAL_PYTHON3=%q\n' "${REAL_PYTHON3}"
        printf 'MARKER=%q\n' "${marker}"
        echo 'if [[ "$*" == *"print(sys.executable)"* ]]; then'
        printf '    echo %q\n' "${fake_python}"
        echo '    exit 0'
        echo 'fi'
        echo 'if [[ "$*" == *"importlib.import_module"* ]]; then'
        echo '    touch "${MARKER}"'
        echo '    requested="${@: -1}"'
        local rule name code
        for rule in "${rules[@]}"; do
            name="${rule%%:*}"
            code="${rule##*:}"
            printf '    if [[ "${requested}" == %q ]]; then exit %q; fi\n' \
                "${name}" "${code}"
        done
        echo '    exec "${REAL_PYTHON3}" "$@"'
        echo 'fi'
        echo 'exec "${REAL_PYTHON3}" "$@"'
    } > "${fake_python}"
    chmod +x "${fake_python}"

    echo "${venv}"
}
# --- end make_fake_venv ---

# --- run_bootstrap_iso ---
run_bootstrap_iso() {
    # Run bootstrap fully isolated: PROJECT_ROOT and VIRTUAL_ENV point
    # into the given ISO_ROOT/venv fixture, SNOMED_LOG_DIR and
    # SNOMED_LOG_LEVEL are set explicitly (satisfying check_env_vars
    # deterministically), and TNS_ADMIN is explicitly unset via `env
    # -u` regardless of what the invoking shell has set — never
    # inherits real-environment state.
    # Args:
    #   $1 — ISO_ROOT
    #   $2 — venv fixture path (from make_fake_venv)
    local iso_root="$1"
    local venv="$2"

    env -u TNS_ADMIN \
        PATH="${venv}/bin:${PATH}" \
        VIRTUAL_ENV="${venv}" \
        PROJECT_ROOT="${iso_root}" \
        SNOMED_LOG_DIR="${iso_root}/log" \
        SNOMED_LOG_LEVEL="INFO" \
        bash "${BOOTSTRAP}" 2>&1
}
# --- end run_bootstrap_iso ---

# ---------------------------------------------------------------------------
# Tests — MISSING / IMPORT FAILED reporting (shell-level fakes)
# ---------------------------------------------------------------------------

# --- test_all_modules_present_reports_ok ---
test_all_modules_present_reports_ok() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 0 ]] \
        && grep -Fq "  OK            oracledb" <<< "${output}" \
        && grep -Fq "  OK            omegaconf" <<< "${output}" \
        && grep -Fq "  OK            yaml" <<< "${output}"; then
        report "all modules present reports OK" "${PASS}"
    else
        report "all modules present reports OK" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_all_modules_present_reports_ok ---

# --- test_missing_module_reported_and_exits_1 ---
test_missing_module_reported_and_exits_1() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}" "oracledb:10")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  MISSING       oracledb" <<< "${output}" \
        && grep -Fq "missing Python modules" <<< "${output}"; then
        report "missing module reported and exits 1" "${PASS}"
    else
        report "missing module reported and exits 1" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_module_reported_and_exits_1 ---

# --- test_all_missing_modules_accumulated ---
test_all_missing_modules_accumulated() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}" "oracledb:10" "omegaconf:10" "yaml:10")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  MISSING       oracledb" <<< "${output}" \
        && grep -Fq "  MISSING       omegaconf" <<< "${output}" \
        && grep -Fq "  MISSING       yaml" <<< "${output}"; then
        report "all missing modules accumulated before exit" "${PASS}"
    else
        report "all missing modules accumulated before exit" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_all_missing_modules_accumulated ---

# --- test_install_hint_shown_on_failure ---
test_install_hint_shown_on_failure() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}" "oracledb:10")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "pip install -r requirements.txt" <<< "${output}"; then
        report "install hint shown on failure" "${PASS}"
    else
        report "install hint shown on failure" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_install_hint_shown_on_failure ---

# --- test_import_failed_reported_and_exits_1 ---
test_import_failed_reported_and_exits_1() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}" "omegaconf:20")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  IMPORT FAILED omegaconf" <<< "${output}" \
        && grep -Fq "modules present but failed to import" <<< "${output}" \
        && grep -Fq "try reinstalling" <<< "${output}"; then
        report "import-failed module reported and exits 1" "${PASS}"
    else
        report "import-failed module reported and exits 1" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_import_failed_reported_and_exits_1 ---

# --- test_missing_and_import_failed_distinguished ---
test_missing_and_import_failed_distinguished() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}" "oracledb:10" "omegaconf:20")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  MISSING       oracledb" <<< "${output}" \
        && grep -Fq "  IMPORT FAILED omegaconf" <<< "${output}" \
        && grep -Fq "missing Python modules" <<< "${output}" \
        && grep -Fq "modules present but failed to import" <<< "${output}"; then
        report "MISSING and IMPORT FAILED distinguished when both occur" "${PASS}"
    else
        report "MISSING and IMPORT FAILED distinguished when both occur" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_and_import_failed_distinguished ---

# ---------------------------------------------------------------------------
# Tests — required_modules.json failure surface (isolated, never the
# real config)
# ---------------------------------------------------------------------------

# --- test_missing_modules_config_exits_1 ---
test_missing_modules_config_exits_1() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    rm -f "${iso}/config/required_modules.json"
    venv="$(make_fake_venv "${iso}")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] && grep -Fq "failed to read required modules" <<< "${output}"; then
        report "missing required_modules.json exits 1" "${PASS}"
    else
        report "missing required_modules.json exits 1" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_modules_config_exits_1 ---

# --- test_malformed_modules_config_exits_1 ---
test_malformed_modules_config_exits_1() {
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    echo "{ not valid json" > "${iso}/config/required_modules.json"
    venv="$(make_fake_venv "${iso}")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] && grep -Fq "failed to read required modules" <<< "${output}"; then
        report "malformed required_modules.json exits 1" "${PASS}"
    else
        report "malformed required_modules.json exits 1" "${FAIL}" "rc=${rc} output=${output}"
    fi
}
# --- end test_malformed_modules_config_exits_1 ---

# ---------------------------------------------------------------------------
# Tests — temp stderr file cleanup, success and failure
# ---------------------------------------------------------------------------

# --- test_bootstrap_cleans_up_temp_stderr_file_on_failure ---
test_bootstrap_cleans_up_temp_stderr_file_on_failure() {
    # Uses the missing-config failure path (which still creates and
    # registers a helper_err temp file before failing) with an
    # isolated TMPDIR, so any leftover file from bootstrap's own
    # mktemp is directly observable afterward.
    local iso venv scratch rc=0 output leftover
    build_iso_root
    iso="${ISO_ROOT}"
    rm -f "${iso}/config/required_modules.json"
    venv="$(make_fake_venv "${iso}")"

    scratch="$(mktemp -d)"
    register_cleanup "${scratch}"

    output=$(TMPDIR="${scratch}" run_bootstrap_iso "${iso}" "${venv}") || rc=$?
    leftover=$(find "${scratch}" -mindepth 1 2>/dev/null || true)

    if [[ "${rc}" -eq 1 ]] && [[ -z "${leftover}" ]]; then
        report "bootstrap cleans up its temp stderr file on failure" "${PASS}"
    else
        report "bootstrap cleans up its temp stderr file on failure" "${FAIL}" \
            "rc=${rc} leftover=${leftover} output=${output}"
    fi
}
# --- end test_bootstrap_cleans_up_temp_stderr_file_on_failure ---

# --- test_bootstrap_cleans_up_temp_stderr_file_on_success ---
test_bootstrap_cleans_up_temp_stderr_file_on_success() {
    # A fully successful bootstrap run still creates helper stderr
    # temp files for both check_python_modules and
    # check_required_dirs (mktemp is called before the helper runs,
    # regardless of whether the helper succeeds). With an isolated,
    # initially empty TMPDIR, the directory must be empty again once
    # bootstrap exits 0.
    local iso venv scratch rc=0 output leftover
    build_iso_root
    iso="${ISO_ROOT}"
    venv="$(make_fake_venv "${iso}")"

    scratch="$(mktemp -d)"
    register_cleanup "${scratch}"

    output=$(TMPDIR="${scratch}" run_bootstrap_iso "${iso}" "${venv}") || rc=$?
    leftover=$(find "${scratch}" -mindepth 1 2>/dev/null || true)

    if [[ "${rc}" -eq 0 ]] && [[ -z "${leftover}" ]]; then
        report "bootstrap cleans up its temp stderr files on success" "${PASS}"
    else
        report "bootstrap cleans up its temp stderr files on success" "${FAIL}" \
            "rc=${rc} leftover=${leftover} output=${output}"
    fi
}
# --- end test_bootstrap_cleans_up_temp_stderr_file_on_success ---

# ---------------------------------------------------------------------------
# Tests — real classifier behavior (no shell-level faking; genuine
# Python fixtures exercise the actual importlib-based one-liner)
# ---------------------------------------------------------------------------

# --- test_missing_module_real_classifier ---
test_missing_module_real_classifier() {
    # Real (non-faked) classifier test: a syntactically valid but
    # genuinely nonexistent module name, run through the passthrough
    # fake venv (no simulate-rules), so the actual importlib-based
    # one-liner — not a shell-level "exit 10" stand-in used by the
    # earlier shell-fake tests — is what produces the classification.
    # Guards against a defect that misclassified every
    # ModuleNotFoundError as IMPORT FAILED (rc 20) instead of MISSING
    # (rc 10); such a defect would still pass the shell-fake tests
    # above, since those hardcode rc 10 directly.
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    cat > "${iso}/config/required_modules.json" << 'JSONEOF'
{
  "required_modules": [
    {"import_name": "ace_test_module_that_does_not_exist", "package_name": "ace-test-module-that-does-not-exist"}
  ]
}
JSONEOF
    venv="$(make_fake_venv "${iso}")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  MISSING       ace_test_module_that_does_not_exist" <<< "${output}" \
        && ! grep -Fq "  IMPORT FAILED ace_test_module_that_does_not_exist" <<< "${output}"; then
        report "genuinely missing module classified as MISSING by real classifier" "${PASS}"
    else
        report "genuinely missing module classified as MISSING by real classifier" "${FAIL}" \
            "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_module_real_classifier ---

# --- test_missing_dotted_parent_real_classifier ---
test_missing_dotted_parent_real_classifier() {
    # Real classifier test for a dotted import_name whose required
    # parent package is itself missing (e.g. "pkg.submodule" where
    # "pkg" does not exist). The implementation explicitly promises
    # this case classifies as MISSING via the
    # requested.startswith(missing_name + ".") check in
    # check_python_modules — a distinct code path from the
    # exact-name-match branch exercised by the plain-name test above,
    # and worth covering separately since a defect could pass one
    # while failing the other.
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    cat > "${iso}/config/required_modules.json" << 'JSONEOF'
{
  "required_modules": [
    {"import_name": "ace_test_missing_parent.submodule", "package_name": "ace-test-missing-parent"}
  ]
}
JSONEOF
    venv="$(make_fake_venv "${iso}")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  MISSING       ace_test_missing_parent.submodule" <<< "${output}" \
        && ! grep -Fq "  IMPORT FAILED ace_test_missing_parent.submodule" <<< "${output}"; then
        report "missing dotted parent classified as MISSING by real classifier" "${PASS}"
    else
        report "missing dotted parent classified as MISSING by real classifier" "${FAIL}" \
            "rc=${rc} output=${output}"
    fi
}
# --- end test_missing_dotted_parent_real_classifier ---

# --- test_transitive_missing_dependency_real_classifier ---
test_transitive_missing_dependency_real_classifier() {
    # A fixture module that is itself present and syntactically valid,
    # but whose own import statement fails on a genuinely missing
    # DIFFERENT module — the real shape of a missing transitive
    # dependency. Must classify as IMPORT FAILED (rc 20), not MISSING
    # (rc 10), since the module requested ("badtransitive") is not the
    # one actually missing.
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    mkdir -p "${iso}/site_fixtures"
    cat > "${iso}/site_fixtures/badtransitive.py" << 'PYEOF'
# Fixture: imports fine syntactically, but its own import triggers
# ModuleNotFoundError for a different (nonexistent) name, simulating a
# genuinely missing transitive dependency.
import this_module_does_not_exist_anywhere  # noqa: F401
PYEOF
    cat > "${iso}/config/required_modules.json" << 'JSONEOF'
{
  "required_modules": [
    {"import_name": "badtransitive", "package_name": "badtransitive"}
  ]
}
JSONEOF
    venv="$(make_fake_venv "${iso}")"
    output=$(PYTHONPATH="${iso}/site_fixtures" run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  IMPORT FAILED badtransitive" <<< "${output}" \
        && ! grep -Fq "  MISSING       badtransitive" <<< "${output}"; then
        report "missing transitive dependency classified as IMPORT FAILED" "${PASS}"
    else
        report "missing transitive dependency classified as IMPORT FAILED" "${FAIL}" \
            "rc=${rc} output=${output}"
    fi
}
# --- end test_transitive_missing_dependency_real_classifier ---

# --- test_sys_exit_during_import_real_classifier ---
test_sys_exit_during_import_real_classifier() {
    # A fixture module that calls sys.exit() at import time. The
    # implementation explicitly promises (via catching BaseException,
    # not Exception) that this classifies as IMPORT FAILED, not a
    # silent crash of the check itself and not MISSING.
    local iso venv rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    mkdir -p "${iso}/site_fixtures"
    cat > "${iso}/site_fixtures/badsysexit.py" << 'PYEOF'
# Fixture: calls sys.exit() during import, simulating a module with
# broken init-time code.
import sys
sys.exit(3)
PYEOF
    cat > "${iso}/config/required_modules.json" << 'JSONEOF'
{
  "required_modules": [
    {"import_name": "badsysexit", "package_name": "badsysexit"}
  ]
}
JSONEOF
    venv="$(make_fake_venv "${iso}")"
    output=$(PYTHONPATH="${iso}/site_fixtures" run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "  IMPORT FAILED badsysexit" <<< "${output}" \
        && ! grep -Fq "  MISSING       badsysexit" <<< "${output}"; then
        report "sys.exit() during import classified as IMPORT FAILED" "${PASS}"
    else
        report "sys.exit() during import classified as IMPORT FAILED" "${FAIL}" \
            "rc=${rc} output=${output}"
    fi
}
# --- end test_sys_exit_during_import_real_classifier ---

# ---------------------------------------------------------------------------
# Test — injection resistance, end to end through bootstrap
# ---------------------------------------------------------------------------

# --- test_malicious_import_name_rejected_via_bootstrap ---
test_malicious_import_name_rejected_via_bootstrap() {
    # A registry entry with an import_name that is not a valid dotted
    # Python identifier must be rejected by read_required_modules.py's
    # own validation before bootstrap ever reaches the import-check
    # step — proving the full chain (registry -> helper validation ->
    # bootstrap) fails closed, not merely that bootstrap passes a
    # string through safely.
    #
    # Two independent, directly observed proofs of non-execution are
    # checked, not just the exit code and error message:
    #   1. canary: a fixed path inside the isolated root that the
    #      payload would touch if it ever executed as shell/Python
    #      code.
    #   2. classifier marker: make_fake_venv's fake python3 touches
    #      ISO_ROOT/.classifier_invoked the instant it sees an
    #      importlib.import_module invocation. Its absence proves the
    #      classifier step itself was never reached, independent of
    #      what bootstrap printed.
    local iso venv canary rc=0 output
    build_iso_root
    iso="${ISO_ROOT}"
    canary="${iso}/injection_canary"

    cat > "${iso}/config/required_modules.json" << JSONEOF
{
  "required_modules": [
    {"import_name": "os.system('touch ${canary}')", "package_name": "malicious"}
  ]
}
JSONEOF
    venv="$(make_fake_venv "${iso}")"
    output=$(run_bootstrap_iso "${iso}" "${venv}") || rc=$?

    if [[ "${rc}" -eq 1 ]] \
        && grep -Fq "failed to read required modules" <<< "${output}" \
        && [[ ! -e "${canary}" ]] \
        && [[ ! -e "${iso}/.classifier_invoked" ]]; then
        report "malicious import_name rejected end-to-end, nothing executed" "${PASS}"
    else
        report "malicious import_name rejected end-to-end, nothing executed" "${FAIL}" \
            "rc=${rc} canary_exists=$([[ -e "${canary}" ]] && echo yes || echo no) classifier_invoked=$([[ -e "${iso}/.classifier_invoked" ]] && echo yes || echo no) output=${output}"
    fi
}
# --- end test_malicious_import_name_rejected_via_bootstrap ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    echo "=== test_bootstrap_r3_sh.sh -- Round 3 (Python modules) ==="
    echo ""

    test_all_modules_present_reports_ok
    test_missing_module_reported_and_exits_1
    test_all_missing_modules_accumulated
    test_install_hint_shown_on_failure
    test_import_failed_reported_and_exits_1
    test_missing_and_import_failed_distinguished
    test_missing_modules_config_exits_1
    test_malformed_modules_config_exits_1
    test_bootstrap_cleans_up_temp_stderr_file_on_failure
    test_bootstrap_cleans_up_temp_stderr_file_on_success
    test_missing_module_real_classifier
    test_missing_dotted_parent_real_classifier
    test_transitive_missing_dependency_real_classifier
    test_sys_exit_during_import_real_classifier
    test_malicious_import_name_rejected_via_bootstrap

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
