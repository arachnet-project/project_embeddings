# ARC_FILE: docs/project_summary.md

# ACE — Project Summary

**Updated:** 2026-08-30
**Session closed:** Pending final close-out commit
**Prepared by:** GPT, pending review by Jan Mura
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
8bcc4cb97666883bcaf1888407f2e40dd618a341
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

The approved `docs/dev_workflow.md` version 2.2 and the inherited
project summary were read.

The live Ubuntu repository was verified as:

```text
/home/jan/project_embeddings
branch: main
```

`HEAD` and `origin/main` were aligned at the inherited commit.

The complete transitional `docs/todo.md` and
`docs/conventions.md` were reviewed.

### Bash-conventions review

Section 10 of `docs/dev_workflow.md` was compared with the Bash
requirements in `docs/conventions.md`.

No substantive conflict was found.

The approved interpretation is:

* A managed repository Bash file retains the mandatory `ARC_FILE:`
  marker on line 1.
* `set -euo pipefail` appears before operational commands.
* Required introductory comments may precede it.
* Temporary conversational scripts are not managed repository files
  and do not require an `ARC_FILE:` marker.
* No conventions change is required for this issue.

The inconsistent Python file-header example remains deferred to
Step 0.7.

### Permanent todo format

A permanent structure for `docs/todo.md` version 2.0 was designed,
reviewed, and approved.

The approved format:

* Keeps current focus and active work near the beginning.
* Defines work units, owners, support, inherited responsibility, and
  approved next actions.
* Uses model-independent `Current assistant` responsibility.
* Separates decisions, implementation work, blockers, deferred work,
  backlog, and rejected or superseded items.
* Removes completed work after its material outcome has been preserved
  in the project summary.
* Condenses old detail when an applicable technical document or Git
  history preserves it.

### Obsolete project-control documents

The following files were read and classified:

```text
docs/todo_step_0_4.md
docs/todo_step_0_5.md
wrk/session_plan.md
docs/project_memory.md
```

`docs/todo_step_0_4.md` contained completed Step 0.4 history and no
unfinished material requiring transfer.

`docs/todo_step_0_5.md` contained completed Step 0.5 history, stale
checklist entries, and technical decisions now preserved in
`docs/phase0_foundation.md`.

The unresolved Step 0.5 real-Oracle evidence requirement was preserved
in `docs/todo.md`.

The untracked and ignored `wrk/session_plan.md` was obsolete. It was
removed from Ubuntu after a temporary backup was created at:

```text
/tmp/ace_session_plan_2026-08-29.md
```

Its remaining bootstrap-duplicate reminder was resolved because:

```text
scripts/bootstrap_v1.8.sh
```

no longer exists.

The two tracked step-specific todo files were deleted in:

```text
437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
docs: Remove obsolete project-control files
```

### Project-memory classification

`docs/project_memory.md` remains preserved and untracked.

Its present model-specific project-memory purpose is incompatible with
the approved two-document control model.

It contains potentially legitimate theoretical, architectural, and
communications material that must be classified before the file is
deleted or repurposed.

No replacement document may operate as a third project-control
document or depend on a particular AI model.

### Bootstrap planning

Step 0.6 remains applied but deferred until the current
control-document work is resolved.

The todo now distinguishes earlier historical bootstrap test results
from verification of the current working tree.

It explicitly preserves the remaining requirements for:

* Dependency-registry validation.
* Stronger helper validation.
* Isolated test fixtures.
* Accurate prerequisite diagnostics.
* Credential-safe failures.
* Approved runtime-directory creation only.
* Local operation without Oracle.
* Oracle reachability in `--real-db` mode.
* Verification of both application schemas.
* Safe handling of unprovisioned schemas.
* No Oracle-object modification.
* No SYSDBA requirement.
* Environment-summary completion.
* Local and OCI verification.

### Additional deferred work

The todo records:

* Ubuntu Python 3.12 evaluation.
* Verification and resolution of the OCI Oracle Database 26ai update
  or patch state.
* Identification of the new person responsible for Jan’s OCI
  environment.
* Claude Code evaluation after Phase 0.
* Repository-maintenance and Step 0.7 documentation work.

Jakub Horák was removed from the contacts plan because he no longer
holds the relevant role.

Viktor Němec remains Jan’s original Oracle contact.

## Decisions approved this session

* `docs/todo.md` version 2.0 is approved as the permanent todo format.
* Active work remains near the beginning of the todo.
* Completed work is removed from the todo after its material outcome
  is preserved in the project summary.
* Every work unit has an owner.
* Support is recorded where useful.
* `Current assistant` is functional and model-independent.
* Step 0.6 is `Applied` with modifier `Deferred`, not `Blocked`.
* Earlier bootstrap test results do not verify the current working
  tree.
* The current bootstrap changes require new local and OCI verification.
* `docs/todo_step_0_4.md` is obsolete and deleted.
* `docs/todo_step_0_5.md` is obsolete and deleted.
* `wrk/session_plan.md` is obsolete and removed.
* `docs/project_memory.md` remains preserved pending content
  disposition.
* Broad documentation work remains deferred to Step 0.7 unless it
  directly blocks current work.
* Claude Code integration is deferred until after Phase 0.
* Claude Code must not become part of the approved ACE workflow without
  an explicit workflow revision.
* The singular `docs/runbook/` path remains obsolete.
* A possible runbook location uses plural `docs/runbooks/`.

## Verification performed

### Ubuntu

Before the cleanup commit:

```text
HEAD:        8bcc4cb97666883bcaf1888407f2e40dd618a341
origin/main: 8bcc4cb97666883bcaf1888407f2e40dd618a341
behind/ahead: 0 0
```

The cleanup commit contained exactly:

```text
M  docs/todo.md
D  docs/todo_step_0_4.md
D  docs/todo_step_0_5.md
```

The commit was:

```text
437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
docs: Remove obsolete project-control files
```

After push:

```text
HEAD:        437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
origin/main: 437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
behind/ahead: 0 0
```

### OCI

OCI fast-forwarded from:

```text
0dfd4cf
```

to:

```text
437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
```

Final OCI verification reported:

```text
## main...origin/main
HEAD:        437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
origin/main: 437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
```

OCI was clean and aligned with `origin/main`.

## Repository state before final close-out commit

Ubuntu `HEAD` and `origin/main` are aligned at:

```text
437d29dcb1e46a9a0fc1f1270e34eabd1d7cb95d
```

The following bootstrap changes remain preserved and outside the
documentation cleanup:

```text
 M scripts/bootstrap.sh
 M tests/test_bootstrap_r3_sh.sh
?? config/required_modules.json
?? src/common/read_required_modules.py
```

The following untracked file also remains preserved:

```text
?? docs/project_memory.md
```

The final close-out commit must contain only:

```text
docs/project_summary.md
docs/todo.md
```

After that commit is pushed, Ubuntu `HEAD` and `origin/main` must again
be aligned.

## Unresolved issues

### Project-memory disposition

The four-layer theoretical model, appendicitis example, propagation
concepts, disclosure guidance, and LinkedIn material require
classification.

### Step 0.6 bootstrap

Bootstrap implementation, isolated fixtures, verification protocol,
local verification, and OCI real-database verification remain
unfinished.

### Step 0.5 evidence

Preserved evidence must be checked for explicit execution with:

```text
SNOMED_TEST_REAL_DB=true
```

### OCI environment

The actual OCI virtual-environment name and path remain unresolved.

The current Oracle Database version, patch level, and earlier failed
26ai update or patch state require verification.

### Contacts

The new person responsible for Jan’s OCI environment has not yet been
identified.

## Immediate next step

Start a new substantial session.

The next session should:

1. Read `docs/dev_workflow.md`.
2. Read this project summary.
3. Verify the live Ubuntu repository state.
4. Read `docs/todo.md`.
5. Inspect `docs/infrastructure.md` only for possible overlap with the
   theoretical material in `docs/project_memory.md`.
6. Decide the proper destination, if any, for that material.
7. Delete or repurpose `docs/project_memory.md` only after relevant
   content has been preserved.
8. Resume Step 0.6 bootstrap close-out after the control-document work
   is resolved.
