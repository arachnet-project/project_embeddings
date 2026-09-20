# ARC_FILE: docs/project_summary.md

# ACE — Project Summary

**Updated:** 2026-09-20
**Session closed:** 2026-09-20, when the commit containing this summary is pushed
**Prepared by:** Claude, reviewed by Jan Mura before commit
**Current phase:** Phase 0 — Foundation and Infrastructure
**Phase status:** In progress

---

## Project context

Arachnet Clinical Embeddings is a SNOMED CT clinical terminology
embedding and semantic-search project using Oracle, Python, and Bash.

It is owned by Arachnet Project z.s. and developed by Jan Mura.

ANTHEA is the parallel theoretical and research project.

The current project objective remains completion and formal close-out
of Phase 0 before Phase 1 implementation begins.

## Scope of this summary

The previous formal close-out was commit `49b56cb` (2026-09-03). The
sessions after it (2026-09-06 to 2026-09-19) were interrupted, not
closed, and no control document was updated. This summary covers those
sessions together with the session of 2026-09-19/20 that completed the
Step 0.6 local-mode revision.

Statements about the interrupted sessions come from session records.
Only the items under "Verification performed" are verified evidence.

## State inherited at session start

Repository: `/home/jan/project_embeddings` on Ubuntu, branch `main`.
Ubuntu is the primary development and sole push machine. OCI Frankfurt
and macOS are pull-only.

The last pushed commit was `49b56cb`. The reviewed Step 0.6 revisions
existed as drafts and partly applied working-tree changes, and nothing
had been committed since the previous close-out.

## Work completed

### Step 0.6 local-mode revision — applied, tested, committed, pushed

Commit `ccb04f9`, `feat:`, committed 2026-09-19 03:07 (-0400):

* `scripts/bootstrap.sh` v1.9. Removes the `TNS_ADMIN`-triggered
  `SNOMED_SYS_DB_PASSWORD` requirement (it conflicted with the Phase
  0/1 Oracle boundary, `docs/todo.md` §3.5). Closes a shell
  code-injection vector in `check_python_modules` by passing the module
  name as `sys.argv[1]` and importing with `importlib`. Distinguishes
  `MISSING` from `IMPORT FAILED`. Hardens directory-path validation
  (exact `..` component check, pre- and post-creation symlink-escape
  containment checks, `CREATED` output deferred until containment
  passes). Resolves `PYTHON` once from `sys.executable`. Cleans up
  temporary files through a single `EXIT` trap. Adds the environment
  summary.
* `src/common/read_required_modules.py` v2.0 and
  `config/required_modules.json` (new). `--config PATH` for test
  isolation, dotted-identifier validation of `import_name`, duplicate
  and malformed-value rejection, validation of the whole registry
  before any output.
* `src/common/read_required_dirs.py` v2.0. `--config PATH`, path-safety
  checks on the literal string (the earlier `PurePosixPath` check
  silently normalized away the components it claimed to reject),
  control-character and duplicate rejection.
* Tests: `test_bootstrap_r1_sh.sh` v1.9, `test_bootstrap_r3_sh.sh`
  v1.5, `test_bootstrap_r4_py.py` v1.2, `test_read_required_dirs_py.py`
  v2.0. The Round 3 and helper tests use isolated fixtures. Round 1
  still runs against the real project tree with hardened restoration
  (deferred redesign: `docs/todo.md` §6.8).

The former `docs/todo.md` §2.2 (coverage of `read_required_dirs.py`
was split across two partly stale test files) was resolved by updating
both files within this pass.

### Defects found by OCI verification — corrected

Commit `bcf74ae`, `fix:`, committed 2026-09-20 00:01 (-0400):

* `scripts/bootstrap.sh` v1.10. `print_environment_summary` printed
  `Mode: local` unconditionally, even when `check_env_vars` had taken
  the `TNS_ADMIN`/OCI branch. Mode is now derived from the same
  `TNS_ADMIN` condition.
* `tests/test_bootstrap_r4_py.py` v1.3. Asserts the exact `Mode:` line
  in the Ubuntu and OCI cases. The earlier return-code-only checks are
  why the defect was not caught on Ubuntu.
* `tests/test_bootstrap_r_py3_sh.sh` v1.2. The below-3.12 warning test
  used a PATH-shadowed fake `python3`. v1.9 resolves `PYTHON` once from
  `sys.executable`, which bypassed the fake, so the test stopped
  simulating Python 3.9 and depended on the real interpreter's version.
  On OCI (real 3.12.12) it failed. The fixture is now an isolated fake
  virtual environment, a hidden directory under `PROJECT_ROOT`, whose
  fake interpreter reports itself as `sys.executable`. Whether the
  earlier Ubuntu pass ever exercised the simulated version cannot be
  established.

The message of this commit was amended before it was pushed (tree
verified unchanged) to remove an unverified assertion count. Its
earlier local hash `31f968f` no longer exists. Nothing pushed was
rewritten.

## Decisions approved

* Commits are grouped by kind: `feat:` for code and tests, `fix:` for
  the OCI-found correction, `docs:` for the control documents, pushed
  from Ubuntu only. The first commit excluded `docs/todo.md`.
* The Phase 0/1 Oracle boundary stays in force: no `SNOMED_SYS_DB_PASSWORD`
  requirement in either bootstrap mode.
* Bootstrap-level coverage of the directory-safety checks waits for the
  isolated fixture-root harness (`docs/todo.md` §6.8).

## Verification performed

Verified against a fresh clone of `origin/main` on 2026-09-20:

* `origin/main` was at `bcf74ae`, following `ccb04f9` and `49b56cb`.
* File headers: `bootstrap.sh` 1.10, `read_required_modules.py` 2.0,
  `read_required_dirs.py` 2.0, `test_bootstrap_r1_sh.sh` 1.9,
  `test_bootstrap_r2_sh.sh` 1.5, `test_bootstrap_r3_sh.sh` 1.5,
  `test_bootstrap_r4_py.py` 1.3, `test_bootstrap_r_py3_sh.sh` 1.2,
  `test_read_required_dirs_py.py` 2.0.
* The header of `read_required_modules.py` describes the actual
  `sys.argv[1]`/`importlib` mechanism (the stale-header correction is
  confirmed).

OCI (pulled at `bcf74ae`, clean working tree), test wrapper output
pasted by Jan on 2026-09-20:

* Precondition check found one virtual-environment candidate,
  `./wenv/bin/activate`.
* All six suites exited 0: Round 1 (9 tests), Round 2 (6), Round py3
  (7), Round 3 (15), Round 4 py (11), `read_required_dirs.py` (20). The
  total is 68 passed, 0 failed.

Ubuntu: all six suites passed before commit `bcf74ae` (output reported
by Jan). Ubuntu `git status` before the close-out commit showed
`main...origin/main` aligned with only `docs/todo.md` modified.

Not verified:

* `scripts/bootstrap.sh` itself was not run on OCI in the recorded
  output. Only the six test suites were.
* No real Oracle connection was tested. `--real-db` does not exist.
* The macOS machine was not checked after `bcf74ae`.

## Repository state at session close

Before this close-out commit, local `HEAD` and `origin/main` were both
`bcf74ae19fb8b8dd8792fef54988bee0135080df` on Ubuntu, and OCI was
clean at `bcf74ae`.

The close-out commit contains exactly:

```text
docs/project_summary.md
docs/todo.md
```

At formal session close, local `HEAD` and `origin/main` must be aligned
at the commit containing this summary.

## Preserved working-tree changes

Before the close-out commit, the only uncommitted change on Ubuntu was
` M docs/todo.md`. It held the edits made in the interrupted sessions
(the former §2.1 and §2.2 status text, the `--real-db` sequencing in
§4.1, and §6.8). This commit supersedes it and carries those edits
forward. No untracked files were reported. After the push, no
uncommitted change is intended to remain.

## Unresolved issues

### Step 0.6 is not complete

The local-mode revision is done. `docs/phase0_foundation.md` still
lists other Step 0.6 work as open, recorded in `docs/todo.md` §2.1 as
`Proposed`:

* The `--real-db` sequencing (waits on Phase 1 provisioning) conflicts
  with Phase 0 exit criterion 3 (Step 0.6 implements `--real-db`).
* The bootstrap verification protocol has not been written.
* The environment summary has only partial test coverage and omits the
  active configuration profile and the log directory that the
  specification lists as example items.
* The Step 0.6 section of `docs/phase0_foundation.md` is out of date.

### OCI virtual-environment name

Verified as `wenv`. `config/project.yaml` still declares `venv` for the
production and development environments (`docs/todo.md` §4.2).

### Other open items, unchanged

`--real-db` design (`docs/todo.md` §4.1, Blocked), UZIS correspondence
(§4.3), Step 0.5 real-Oracle evidence (§5), and the deferred items in
§6, including the Oracle Database 26ai patch state and contacts.

## Immediate next step

Start a new session.

The next session should:

1. Read `docs/dev_workflow.md`.
2. Read this project summary.
3. Verify the live Ubuntu repository state, and pull on macOS.
4. Read `docs/todo.md`.
5. Decide the remaining Step 0.6 scope (`docs/todo.md` §2.1), starting
   with the `--real-db` versus Phase 0 exit criterion conflict.
