# ARC_FILE: docs/dev_workflow.md

# ACE — Development Workflow

# Version: 2.2

# Status: Approved

## 1. Purpose

This document defines the general development workflow for ACE.

The workflow requires:

* Verification against the live repository.
* Agreement before implementation.
* Explicit recording of decisions and plan changes.
* Preservation of existing work.
* Appropriate testing.
* Small, coherent commits.
* Formal session opening and close-out.

## 2. Sources of authority

The live repository is the primary source of truth for files,
implementation state, Git state, and recorded test evidence.

Project-control documents, conversation summaries, and human or AI
memory provide context, but they do not override verifiable repository
state.

When two sources disagree:

1. Verify the claim against the applicable files, Git history,
   configuration, tests, or runtime environment.
2. State the discrepancy explicitly.
3. Do not silently choose one account.
4. If verification does not resolve the issue, record it as unresolved
   and ask Jan before acting.

A material claim that can reasonably be checked must be checked before
it is used as the basis for a decision or change.

## 3. Project-control documents

ACE uses exactly two project-control documents:

* `docs/project_summary.md`
* `docs/todo.md`

No other project-control document may be used unless this workflow is
explicitly revised and approved first.

### 3.1 `docs/project_summary.md`

`docs/project_summary.md` records the outcome and resulting state of
the most recently closed substantial session.

It must contain:

* Material work completed.
* Decisions approved.
* Verification performed.
* Repository state at session close.
* Preserved working-tree changes.
* Unresolved issues.
* The immediate next step.

The project summary normally remains unchanged during active work. It
is updated during session close-out from verified repository state,
not from conversational memory alone.

### 3.2 `docs/todo.md`

`docs/todo.md` records the present and near future.

It must contain:

* The current work plan.
* Work status.
* Current decisions.
* Blockers and unresolved questions.
* Approved next actions.
* Deferred work and backlog items.
* Rejected and superseded items that must remain recorded.
* Material changes to the agreed plan.

It must be updated after a logical work unit whenever the project
state or plan has materially changed. It must be brought fully up to
date during session close-out.

Both control documents are tracked in Git. Both must be updated,
reviewed, committed, and pushed before a substantial session is
declared closed.

## 4. Session opening

At the beginning of a substantial session:

1. Read `docs/dev_workflow.md`.
2. Read `docs/project_summary.md`.
3. Confirm the live repository state, including:

   * repository path,
   * current branch,
   * `git status`,
   * recent Git history,
   * relationship between `HEAD` and `origin/main`.
4. Read `docs/todo.md`.
5. Compare the control documents with the verified repository state.
6. State every material discrepancy.
7. Agree on the session objective and immediate work units.

Additional files and directory structure must be inspected when
required by the agreed work. A full recursive directory listing is not
required at every session opening.

## 5. Planning and work status

Work must proceed in logical units with a clear intended outcome.

The normal progression is:

* `Proposed` — suggested but not approved.
* `Agreed` — approved but not yet applied.
* `Applied` — changed in the working tree.
* `Tested` — required verification has passed.
* `Committed` — included in a reviewed local commit.
* `Pushed` — present on the approved remote branch.

The terminal outcomes are:

* `Rejected` — considered and explicitly not accepted.
* `Superseded` — replaced by a later approved decision or work item.

The status modifiers are:

* `Blocked` — cannot proceed because of an unresolved obstacle or
  dependency.
* `Deferred` — deliberately postponed although it could proceed.

`Blocked` and `Deferred` do not replace the work item’s current
lifecycle state.

A document may be described as `Reviewed` or `Approved` when those
terms are more accurate than `Tested`.

No work is complete merely because it was discussed or written.
Agreement, application, verification, commit, and push are separate
events.

Rejected and superseded items must be recorded in `docs/todo.md`.
Material outcomes must also be preserved in
`docs/project_summary.md` during session close-out.

## 6. Decisions and changes of plan

Material decisions must be recorded when they are made rather than
reconstructed only at session close.

A material departure from the agreed plan must be stated when it
occurs and recorded in `docs/todo.md`. This includes:

* Starting an unplanned task.
* Expanding a task substantially beyond its agreed scope.
* Postponing or replacing an agreed work unit.
* Discovering a blocker that changes the planned order.

Minor investigation within an agreed work unit does not require a
separate deviation record unless it changes scope, risk, affected
files, or expected results.

## 7. File changes

Before modifying a file:

1. Read the current file.
2. Check its Git status.
3. Identify existing changes that must be preserved.
4. Confirm that the modification belongs to the agreed work unit.

Existing work must not be overwritten, discarded, staged, or committed
without review.

Changes must be grouped into small, coherent commits. Unrelated
documentation, implementation, tests, generated files, and cleanup
must not be combined merely because they are present in the working
tree.

Before committing:

1. Review the exact files to be included.
2. Review the staged diff.
3. Check for unintended files, whitespace damage, permission changes,
   and secrets.
4. Run verification appropriate to the change.
5. Ensure that only approved files are included.

Commit messages must begin with exactly one of these approved prefixes:

* `docs:` — documentation-only changes.
* `fix:` — correction of defective implementation behavior.
* `test:` — test or verification changes without a corresponding
  implementation change.
* `chore:` — repository maintenance that does not change product
  behavior.
* `feat:` — new or materially expanded product behavior.

No other commit-message prefix may be used.

If a change does not fit one of these categories, work must stop until
the correct classification is agreed. Adding or changing a prefix
requires an explicit revision of this workflow.

Published Git history must not be rewritten merely to correct a
harmless commit-message typo.

## 8. Testing and evidence

Testing must match the scope and risk of the change.

A work unit may be marked `Tested` only after its required verification
has passed.

Tests requiring an external service or specialized environment must
be distinguished from local or simulated tests. Claims about such
testing must be supported by recorded evidence.

Tests must use isolated fixtures. They must not modify real project
configuration or user data unless the exception is explicitly
discussed and approved before the test is run.

Commands, results, environments, and failures must be recorded when
they have lasting value for later verification or development.

## 9. Machine roles

ACE machine roles are strict and non-symmetric:

* Ubuntu is the primary development machine and the sole push machine.
* OCI Frankfurt is the pull-only real-database verification
  environment.
* macOS machines are pull-only and auxiliary.

Machine roles may change only through an explicit, approved revision of
this workflow.

Work produced on a pull-only machine must follow the approved transfer
route to Ubuntu before it is committed or pushed.

Machine-specific paths, environments, and configuration must be
verified rather than assumed.

## 10. Shell-command and Bash-script handling

A single independent shell command may be presented as an individual
command.

Two or more related shell commands intended to be run in sequence must
be presented as one Bash script. The commands must not be distributed
across prose or multiple command blocks.

Every Bash script must conform to `docs/conventions.md`.

The script must:

* Include a brief description of its purpose.
* Identify the intended machine and working directory.
* Execute commands in the required order.
* Stop safely when a prerequisite or verification fails.
* Avoid destructive operations unless their exact targets and effects
  have been verified and explicitly approved.
* Display enough information for its result to be reviewed.

Command output must be evaluated before any dependent script is
prepared or run.

When a response contains a Bash script that has not yet been run, the
script must appear at the end of the response as the complete pending
command sequence. Commands already run must not be included in it.

## 11. Session close-out

A substantial session is not formally closed until its work and
repository state have been reconciled.

Session close-out must:

1. Review the agreed work units and set their current statuses.
2. Confirm the repository path, branch, status, recent history, and
   relationship to `origin/main`.
3. Verify the files and tests relevant to the completed work.
4. Update `docs/todo.md` with completed work, unfinished work,
   blockers, unresolved issues, backlog, and the next intended work.
5. Update `docs/project_summary.md` from verified repository evidence.
6. Review the changes to both control documents.
7. Commit both control documents, together or in an approved sequence
   of coherent commits.
8. Push the approved commits from Ubuntu to `origin/main`.
9. Verify the final relationship between local `HEAD` and
   `origin/main`.
10. Record every preserved uncommitted working-tree change explicitly.

If the control documents cannot be updated, committed, and pushed, the
session is interrupted or awaiting close-out rather than closed.

## 12. Automation

Automation of session opening and close-out may be introduced only
after its behavior has been separately designed, reviewed, and
approved.

Automation must preserve:

* Verification against live repository state.
* Explicit handling of discrepancies.
* Existing working-tree changes.
* Explicit control over committed files.
* Machine roles.
* The two-document control model.

Automation must support the workflow. It must not make project
decisions silently.
