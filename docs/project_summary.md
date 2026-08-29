# ARC_FILE: docs/project_summary.md

# ACE — Project Summary

**Updated:** 2026-08-29
**Session closed:** 2026-08-29
**Prepared by:** GPT, reviewed by Jan Mura
**Current phase:** Phase 0 — Foundation and Infrastructure
**Phase status:** In progress

---

## Project context

Arachnet Clinical Embeddings is a SNOMED CT clinical terminology
embedding and semantic-search project using Oracle, Python, and Bash.

It is owned by Arachnet Project z.s. and developed by Jan Mura.

ANTHEA is the parallel theoretical and research project.

The current objective is to complete and formally close Phase 0 before
beginning Phase 1 implementation.

## State inherited at session start

The authoritative development repository was:

```
/home/jan/project_embeddings
```

The branch was:

```
main
```

Ubuntu remained the primary development and sole push machine. OCI
Frankfurt remained the pull-only real-Oracle verification environment.
macOS remained pull-only and auxiliary.

At session start, local `HEAD` and `origin/main` were aligned at:

```
61dc21c docs: Revise Phase 0 scope and Roundmap boundary
```

Existing documentation and bootstrap changes had to be preserved.

## Work completed this session

### Development workflow

`docs/dev_workflow.md` was revised and approved as version 2.2.

The approved workflow:

* Defines the live repository as the primary verifiable source of
  truth.
* Requires discrepancies to be stated rather than silently resolved.
* Establishes exactly two project-control documents:

  * `docs/project_summary.md`;
  * `docs/todo.md`.
* Prohibits any additional project-control document unless the
  workflow is explicitly revised and approved.
* Defines formal session-opening and session-close procedures.
* Defines the normal lifecycle:

  * `Proposed`;
  * `Agreed`;
  * `Applied`;
  * `Tested`;
  * `Committed`;
  * `Pushed`.
* Defines `Rejected` and `Superseded` as terminal outcomes.
* Defines `Blocked` and `Deferred` as status modifiers.
* Requires material decisions and plan changes to be recorded when
  they occur.
* Requires existing work to be inspected and preserved before files
  are modified.
* Defines a closed set of permitted commit-message prefixes:

  * `docs:`;
  * `fix:`;
  * `test:`;
  * `chore:`;
  * `feat:`.
* Requires isolated test fixtures unless an exception is discussed and
  approved before testing.
* Preserves strict, non-symmetric machine roles.
* Requires related shell-command sequences to be presented as complete
  Bash scripts conforming to `docs/conventions.md`.
* Requires every Bash script to state its purpose, machine, and working
  directory.
* Requires both control documents to be updated, committed, and pushed
  before a substantial session is declared closed.
* Allows automation only after separate design, review, and approval.

### Review of Claude’s objections

The following decisions were made:

* The fuller lifecycle vocabulary was restored.
* No separate `docs/decisions.md` will be introduced.
* Rejected and superseded items belong in `docs/todo.md`.
* Material outcomes are preserved in `docs/project_summary.md`.
* Historical retirement details do not belong in the permanent
  workflow.
* The workflow defines exactly two control documents without naming
  obsolete mechanisms.
* No AI-specific versus human-specific document categories will be
  introduced.
* Project documents should remain authoritative for humans and AI
  assistants without depending on a particular model.
* Phase-specific document references do not belong in the general
  workflow.
* Document discovery will be handled separately through the applicable
  directory-structure document, document index, or README.
* Test-isolation exceptions require advance discussion and approval.
* A machine-role change requires an approved revision of the workflow
  because the roles are defined by that workflow.
* A redundant conditional rule about recording rejected approaches
  was removed.

### Repository investigation

A macOS investigation found no current or historical
`docs/decisions.md` in the available repository references.

The investigation was partially limited because `rg` was not installed
on macOS. Direct Git checks for the exact file path succeeded and found
no tracked file or history.

### Stored workflow verification

The stored Ubuntu `docs/dev_workflow.md` was inspected against the
approved version.

Verification confirmed:

* Version 2.2 and status `Approved`.
* All approved substantive wording is present.
* File permissions are `100644`.
* The Git whitespace check passes.
* The file contains UTF-8 text.
* The only differences from the displayed GPT version are harmless
  Markdown formatting differences:

  * `*` instead of `-` for unordered lists;
  * additional blank lines between the opening metadata headings.

The stored Ubuntu file was accepted as the authoritative final version.

Its verified metadata was:

```
Lines: 323
Bytes: 10544
SHA-256:
bb753f1a7f58ddc15b2fafe2bcd4b59d60d8ff9b34bfe4c3a0c18a70a8bc3936
```

## Decisions approved this session

* `docs/dev_workflow.md` version 2.2 is approved.
* ACE uses exactly two project-control documents.
* `docs/project_summary.md` and `docs/todo.md` remain tracked in Git.
* Both control documents must be committed and pushed at session
  close.
* The permanent `docs/todo.md` format remains to be designed and
  approved.
* The current todo revision is transitional.
* Existing parallel planning documents must be inspected before
  deletion.
* Relevant unfinished content must be transferred before an obsolete
  planning document is removed.
* Broad documentation work remains deferred to Step 0.7 unless it
  directly blocks current work.
* The Bash requirements in `docs/conventions.md` must be inspected
  before other control-document restructuring continues.
* The conventions review will begin in a new session.

## Verification performed

The Ubuntu repository reported:

```
/home/jan/project_embeddings
branch: main
```

Before the session close-out commit:

```
HEAD:        61dc21c91813f2130a331e70fe1dc33a990c3498
origin/main: 61dc21c91813f2130a331e70fe1dc33a990c3498
behind/ahead: 0 0
```

The following checks passed for `docs/dev_workflow.md`:

* Complete-file review.
* Difference from `HEAD`.
* Git whitespace verification.
* File-permission verification.
* UTF-8 file-type verification.
* SHA-256 calculation.

## Repository state at session close

The close-out commit contains:

* `docs/dev_workflow.md`
* `docs/project_summary.md`
* `docs/todo.md`

At formal session close, local `HEAD` and `origin/main` must be aligned
at the commit containing this summary.

The following existing bootstrap changes remain preserved and
uncommitted:

```
scripts/bootstrap.sh
tests/test_bootstrap_r3_sh.sh
config/required_modules.json
src/common/read_required_modules.py
```

The untracked file:

```
docs/project_memory.md
```

also remains preserved pending review.

No preserved bootstrap or project-memory file is included in the
workflow/control-document commit.

## Unresolved issues

### Todo format and obsolete control files

The permanent structure of `docs/todo.md` is not yet approved.

Existing session plans, step-specific todo documents, and
`docs/project_memory.md` must be inspected. Relevant unfinished
material must be preserved before obsolete control documents are
deleted.

### Conventions

The Bash-script requirements in `docs/conventions.md` must be checked
against Section 10 of the approved workflow.

### OCI virtual environment

Earlier operational information identifies the OCI environment as:

```
wenv
```

The production configuration reportedly identifies it as:

```
venv
```

The actual OCI path must be verified before configuration or
documentation is changed.

### Step 0.6 bootstrap

Bootstrap remains in progress.

Remaining work includes:

* Validate `config/required_modules.json`.
* Strengthen `src/common/read_required_modules.py`.
* Introduce isolated test fixtures.
* Confirm local and `--real-db` behavior.
* Ensure neither mode requires SYSDBA credentials.
* Complete the environment summary.
* Create the bootstrap verification protocol.
* Run the required local and real-database verification.

### Step 0.5 evidence

Step 0.5 implementation remains complete.

If preserved evidence does not confirm execution with:

```
SNOMED_TEST_REAL_DB=true
```

the applicable real-Oracle verification must be repeated during Phase
0 close-out.

## Immediate next step

Start a new session.

The next session should:

1. Read the approved `docs/dev_workflow.md`.
2. Read this project summary.
3. Confirm the minimal live repository state.
4. Read `docs/todo.md`.
5. Inspect the Bash-script requirements in `docs/conventions.md`.
6. Resolve any conflict with Section 10 of the workflow.
7. Begin the todo-format and obsolete-control-document review.
