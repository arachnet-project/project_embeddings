# ARC_FILE: docs/project_summary.md

# ACE — Project Summary

**Updated:** 2026-09-02
**Session closed:** 2026-09-02
**Prepared by:** Claude, reviewed by Jan Mura
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

## State inherited at session start

The authoritative development repository was:

```text
/home/jan/project_embeddings
```

The branch was:

```text
main
```

Ubuntu remained the primary development and sole push machine. OCI
Frankfurt and macOS remained pull-only.

At session start, local `HEAD` and `origin/main` were aligned at:

```text
51a912e
```

The preserved working tree contained:

```text
 M scripts/bootstrap.sh
 M tests/test_bootstrap_r3_sh.sh
?? config/required_modules.json
?? docs/project_memory.md
?? src/common/read_required_modules.py
```

## Work completed this session

### Session opening and repository verification

`docs/dev_workflow.md` v2.2 was read. The inherited
`docs/project_summary.md` was read and a material discrepancy was
identified: it described a "Prepared by: GPT, pending review by Jan
Mura" state and a different Git history than the live repository. Live
`git status`/`git log` output was used to resolve the discrepancy: the
correct `HEAD` was `51a912e`, and the pasted `project_summary.md` and
`docs/todo.md` were confirmed as its actual committed content.

### Project-memory disposition (`docs/todo.md` former §2.1)

`docs/infrastructure.md` was inspected and confirmed to have no scope
overlap with the theoretical material in `docs/project_memory.md`.

`docs/project_memory.md` was read in full and reviewed with Jan. The
following disposition was agreed and applied:

* The four-layer conceptual model, the acute-appendicitis walkthrough,
  and the attribute-propagation discussion were preserved in a new
  file, `docs/ace_architecture.md`.
* The LinkedIn post drafts and intellectual-property disclosure
  discussion were reviewed and discarded — no continuing
  organizational or ANTHEA value was identified.
* The bootstrap-script discussion (referencing `bootstrap.sh` v1.2,
  `read_required_dirs.py`, `directory_structure.yaml`) was reviewed
  and discarded as superseded by the current Step 0.6 implementation.
* `docs/project_memory.md` was deleted (untracked; plain `rm`).

`docs/ace_architecture.md` is intended for eventual transfer into the
ANTHEA repository after `v0.1.0-phase0` is tagged, per Jan's
instruction. It is committed to ACE temporarily in the meantime.

### Corrections to the todo/workflow-process documents

Jan reviewed a draft revision of `docs/todo.md` and raised eight
objections (through a GPT review pass). All eight were addressed:

1. Current-focus wording was corrected to not prematurely claim Step
   0.6 was resumed before the project-memory work was committed.
2. A new corrective work unit was added recording the stale
   `Prepared by`/`Session closed` wording left in the previous
   `docs/project_summary.md` by commit `51a912e`.
3. `Lifecycle status: Deferred` was corrected to
   `Lifecycle status: Agreed` with `Status modifier: Deferred` across
   six sections that had misused `Deferred` as a lifecycle state,
   contrary to `dev_workflow.md` §5.
4. The claim that `docs/ace_architecture.md` and the `project_memory.md`
   deletion were already applied was corrected to reflect they were
   only agreed at that point — corrected once the actions were
   actually verified via `git status`.
5. Vague "non-project-control content" wording for discarded material
   was replaced with a specific account of what was discarded and why.
6. An incorrect citation of `dev_workflow.md` §12 (automation) was
   corrected to reference the workflow's actual revision requirements
   (§§3, 7, 9).
7. The document's `Updated` date was corrected to the actual session
   date.
8. The ANTHEA-transfer decision was confirmed as Jan's explicit
   instruction, not an assistant-originated proposal, and the
   temporary-ACE-commit approach was confirmed as intentional given
   ANTHEA's repository status is not yet confirmed.

### Step 0.6 bootstrap — reviewed and revised (not yet applied)

`config/required_modules.json`, `src/common/read_required_modules.py`,
`scripts/bootstrap.sh`, `config/directory_structure.yaml`, and
`src/common/read_required_dirs.py` were read and reviewed in detail,
including two rounds of review (via GPT) surfacing 6 objections on the
modules helper and 8 objections on `bootstrap.sh` and the directory
helper.

Revised versions were drafted addressing all raised objections,
including:

* A real code-injection vector in `check_python_modules`
  (`"${PYTHON}" -c "import ${module}"` with unsafe shell interpolation
  of registry-sourced data) was identified and fixed by passing the
  module name as `sys.argv[1]` and importing via `importlib`.
* A conflict between `check_env_vars`'s `TNS_ADMIN`-triggered
  `SNOMED_SYS_DB_PASSWORD` requirement and the approved Phase 0/1
  Oracle boundary (`docs/todo.md` §3.5 — no SYS/SYSDBA credentials in
  either bootstrap mode) was identified and the offending block
  removed.
* `MISSING` vs `IMPORT FAILED` reporting was distinguished so genuine
  absence is not conflated with a broken installation.
* Directory-path validation was hardened: exact `..` component
  checking (replacing an overbroad substring check) plus a
  post-creation symlink-escape check against `PROJECT_ROOT`.
* `read_required_dirs.py`'s path-safety check was found to have a real
  defect during review — `PurePosixPath` silently normalizes away the
  empty/`.` components the check claimed to reject — and was corrected
  to split on the literal string instead.
* A concise environment summary (project root, venv, Python version,
  mode, check results) was added, addressing the missing requirement
  in `docs/todo.md` §4.1.
* Temp-file cleanup was made robust via an `EXIT` trap.

**These revisions exist only as reviewed drafts in this session. They
have not been written to the working tree, and no test has been run
against them.** `docs/todo.md` records this as the explicit next step.

Two items were explicitly identified as out of scope for this pass and
deferred:

* `--real-db` mode remains unimplemented; it requires reviewing the
  approved `db_connection.py` interface first, which was not done this
  session.
* Confirming that `read_required_dirs.py`'s returned list is
  specifically the approved runtime-directory set was completed
  (`config/directory_structure.yaml` was reviewed: `log`, `wrk`,
  `tests/results`, `sql/ddl/tables` — confirmed as the approved set).

## Decisions approved this session

* `docs/ace_architecture.md` is the approved destination for the
  four-layer model material, pending ANTHEA transfer after
  `v0.1.0-phase0`.
* Remaining `docs/project_memory.md` material has no continuing value
  and required no further preservation.
* The stale `project_summary.md` wording from `51a912e` is a recorded,
  deferred corrective item, resolved by this document's own rewrite.
* `Deferred` is a status modifier, never a lifecycle status, per
  `dev_workflow.md` §5; six todo sections were corrected accordingly.
* The revised bootstrap/helper code is reviewed and agreed in design,
  but must be applied to the working tree and tested before it may be
  committed. It is not committed this session.
* Given session length, this session is being closed now rather than
  continuing further code review, to keep close-out state clean for
  the next session.

## Verification performed

The project-memory disposition was verified via live `git status` and
staged `git diff` output (files: `docs/ace_architecture.md` added,
`docs/todo.md` modified; `scripts/bootstrap.sh`,
`tests/test_bootstrap_r3_sh.sh`, `config/required_modules.json`, and
`src/common/read_required_modules.py` correctly excluded from staging).

The bootstrap/helper revisions were reviewed for correctness in
conversation but have not been executed or tested. This is not
`Tested` evidence and must not be treated as such.

## Repository state at session close

The close-out commit is intended to contain exactly:

```text
docs/ace_architecture.md
docs/project_summary.md
docs/todo.md
```

At formal session close, local `HEAD` and `origin/main` must be
aligned at the commit containing this summary.

The following existing changes remain preserved and outside this
commit, pending application and testing of the reviewed drafts:

```text
 M scripts/bootstrap.sh
 M tests/test_bootstrap_r3_sh.sh
?? config/required_modules.json
?? src/common/read_required_modules.py
```

## Unresolved issues

### Step 0.6 bootstrap — drafts pending application and test

The reviewed revisions to `scripts/bootstrap.sh`,
`src/common/read_required_modules.py`, and
`src/common/read_required_dirs.py` must be applied to the working
tree, the affected test files updated to match the new interfaces
(`--config` flag, `IMPORT FAILED` vs `MISSING` exit codes, safe-import
mechanism), and all required local/OCI verification run, before any
of it may be committed.

### `--real-db` mode

Remains unimplemented. Requires review of the approved
`db_connection.py` interface before design can proceed.

### Step 0.5 evidence

Unchanged from prior sessions — preserved evidence must be checked for
explicit execution with `SNOMED_TEST_REAL_DB=true`.

### OCI environment

Unchanged — actual OCI virtual-environment name/path and current
Oracle Database version/patch state remain unverified.

### Contacts

Jakub Horák's removal from the contacts plan is agreed but not yet
applied to `docs/contacts.md`. The new OCI-responsible contact remains
unidentified.

## Immediate next step

Start a new session.

The next session should:

1. Read `docs/dev_workflow.md`.
2. Read this project summary.
3. Verify the live Ubuntu repository state.
4. Read `docs/todo.md`.
5. Apply the reviewed `bootstrap.sh`, `read_required_modules.py`, and
   `read_required_dirs.py` revisions to the working tree.
6. Update the affected bootstrap test files to match the new
   interfaces.
7. Run all required local bootstrap tests, then OCI verification.
8. Commit and push the Step 0.6 work once tested.