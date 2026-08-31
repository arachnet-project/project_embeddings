# ARC_FILE: docs/todo.md

# ACE — Todo

# Version: 2.0

# Updated: 2026-08-30

# Status: Approved

## Document use

This document records the present and near future of ACE.

It contains active work, approved next actions, decisions in force,
blockers, unresolved questions, deferred work, backlog, and material
rejected or superseded items.

Completed work is transferred to `docs/project_summary.md` during
session close-out and then removed from this document after its
material outcome has been preserved.

Active work remains near the beginning of this document. Deferred,
rejected, and superseded material remains below active work.

Within active work, items are ordered by intended execution order.
Within backlog and historical sections, newer or more relevant items
normally appear first.

Old entries must be condensed when their full detail is available in
the applicable technical document, `docs/project_summary.md`, or Git
history.

## Field definitions

### Current focus

The current focus is the highest-priority outcome guiding the order of
active work.

It is not a project objective, phase exit criterion, or record of
completed work. It must be updated when the project’s immediate
priority changes.

### Work unit

A work unit is a logically related body of work with a clear intended
outcome.

### Owner

The owner is the person accountable for ensuring that a work unit is
resolved.

Ownership does not mean that the owner must personally prepare every
draft, perform every analysis, or execute every command.

### Support

Support identifies a person or functional role that assists the owner
with preparation, analysis, verification, or review but is not
accountable for the final outcome.

`Current assistant` means whichever AI assistant is participating in
the active session. It does not refer permanently to Claude, GPT, or
any particular model.

### Inherited responsibility

Checklist items inherit the owner and support assignments of their
work unit unless an item states an exception.

### Approved next action

An approved next action is an agreed action that may proceed when its
required predecessor work and safety checks are complete.

Lifecycle statuses and status modifiers have the meanings defined in
`docs/dev_workflow.md`.

## 1. Current focus

Decide the proper non-control destination, if any, for legitimate
architectural and communications material in
`docs/project_memory.md`.

After the project-memory disposition is resolved, resume Step 0.6
bootstrap close-out.

The broader documentation consistency review remains deferred to
Step 0.7.

## 2. Active work units

### 2.1 Project-memory disposition

Lifecycle status: `Agreed`

Owner: Jan

Support: Current assistant

Intended outcome:

Preserve any legitimate architectural or communications material from
`docs/project_memory.md` without retaining a model-specific parallel
project-control document.

Current state:

* `docs/project_memory.md` is preserved and untracked on Ubuntu.
* It identifies itself as a “GPT track.”
* It records decisions, designs, discussions, drafts, and conclusions.
* Its current purpose conflicts with the approved two-document
  project-control model.
* It must not become a third project-control document.
* It must not remain dependent on GPT, Claude, or another particular
  model.

Material requiring disposition:

* The four-layer conceptual model:

  * Source of Truth.
  * Rulebook.
  * Learning Engine.
  * Search and Reasoning.
* The acute-appendicitis conceptual walkthrough.
* Attribute-propagation concepts.
* Governance and explainability principles.
* Intellectual-property disclosure guidance.
* LinkedIn-post material.

Approved next actions:

1. Inspect `docs/infrastructure.md` only to determine whether its scope
   overlaps with the four-layer model.
2. Decide whether the theoretical material belongs in:

   * a legitimate ACE architecture document;
   * ANTHEA;
   * communications or outreach documentation;
   * or no continuing project document.
3. Decide whether the LinkedIn material requires preservation.
4. Transfer only material with an approved continuing purpose.
5. Delete or explicitly repurpose `docs/project_memory.md` after
   preservation is complete.
6. Ensure that any resulting document has a clear non-control purpose.

## 3. Decisions in force

### 3.1 Project-control model

Owner: Jan

* ACE uses exactly two project-control documents:

  * `docs/project_summary.md`;
  * `docs/todo.md`.
* Both control documents remain tracked in Git.
* Both must be updated, reviewed, committed, and pushed before a
  substantial session is formally closed.
* No separate decision log will be introduced.
* Rejected and superseded items that must remain recorded belong in
  `docs/todo.md`.
* Material session outcomes belong in `docs/project_summary.md`.
* No additional project-control document may be used unless
  `docs/dev_workflow.md` is explicitly revised and approved.

### 3.2 Development workflow

Owner: Jan

* `docs/dev_workflow.md` version 2.2 is approved.
* Ubuntu is the primary development and sole push machine.
* OCI Frankfurt and macOS remain pull-only.
* The live repository remains the primary verifiable source of truth.

### 3.3 Bash requirements

Review status: `Reviewed`

Owner: Jan

Support: Current assistant

* Section 10 of `docs/dev_workflow.md` and the Bash requirements in
  `docs/conventions.md` have no substantive conflict.
* For a managed repository Bash file, the mandatory `ARC_FILE:` marker
  remains on line 1.
* The requirement to place `set -euo pipefail` “at the top” means
  before operational commands. It does not prohibit the required
  `ARC_FILE:` marker or introductory comments.
* A temporary script presented in conversation is not a managed
  repository file and therefore does not require an `ARC_FILE:` line.
* No change to `docs/conventions.md` is required to resolve the Bash
  review.

### 3.4 Documentation scope

Owner: Jan

* Broad documentation review remains deferred to Step 0.7 unless a
  documentation issue directly blocks current work.
* The inconsistent Python file-header example in
  `docs/conventions.md` is deferred to Step 0.7.
* Possible conflict between `docs/git_workflow.md` and the closed
  commit-prefix set in `docs/dev_workflow.md` is deferred to Step 0.7
  unless it blocks a commit before then.
* Automation of session opening and close-out remains deferred until
  it is separately designed, reviewed, and approved.

### 3.5 Phase 0 and Phase 1 Oracle boundary

Owner: Jan

* Phase 0 establishes the staging-schema pattern.
* Phase 0 does not provision Oracle application schemas.
* Creation and use of `snomed` and `snomed_stage` belong to Phase 1.
* `db_connection.py` recognizes `sys` only for privileged Oracle
  provisioning.
* Neither local nor real-database bootstrap may use `sys` or require
  SYSDBA credentials.
* The approved Phase 1 setup procedure determines privileged access.

## 4. Current implementation work

### 4.1 Step 0.6 bootstrap close-out

Lifecycle status: `Applied`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

Reason for deferral:

Step 0.6 could proceed, but it remains deliberately postponed until
the project-memory disposition is resolved.

Current preserved working-tree files:

* `scripts/bootstrap.sh`
* `tests/test_bootstrap_r3_sh.sh`
* `config/required_modules.json`
* `src/common/read_required_modules.py`

Existing test evidence:

Earlier records report that the five existing bootstrap test files
passed on Ubuntu and OCI.

Those results remain historical evidence for the versions tested, but
they do not verify the current working tree. Changes to
`scripts/bootstrap.sh` and `tests/test_bootstrap_r3_sh.sh`, together
with the new dependency registry and helper, require current local and
OCI verification after the Step 0.6 implementation and isolated
fixtures are finalized.

Required work:

* [ ] Review and validate `config/required_modules.json`.

* [ ] Strengthen validation in
  `src/common/read_required_modules.py`.

* [ ] Replace tests that modify repository configuration with isolated
  fixtures.

* [ ] Confirm that default bootstrap reports missing or broken
  prerequisites without requiring those prerequisites to operate
  successfully.

* [ ] Verify that dependency failures identify the actual failing
  prerequisite.

* [ ] Verify that diagnostics do not expose credentials.

* [ ] Confirm the approved local bootstrap behavior.

* [ ] Verify that local mode does not require Oracle connectivity,
  application schemas, application-schema passwords, or SYSDBA
  credentials.

* [ ] Verify that any directory creation is restricted to explicitly
  approved runtime directories.

* [ ] Confirm the approved `--real-db` interface.

* [ ] Verify that `--real-db` uses the approved database-connection
  interface to test Oracle reachability.

* [ ] Verify that `--real-db` checks both:

  ```
  snomed
  snomed_stage
  ```

* [ ] Verify that an unavailable or unprovisioned application schema
  causes a safe failure with an accurate diagnostic.

* [ ] Verify that `--real-db` explains that Phase 1 setup must precede
  verification when application schemas do not exist.

* [ ] Verify that real-database mode does not create or modify Oracle
  objects.

* [ ] Verify that neither bootstrap mode requires SYSDBA credentials.

* [ ] Complete the concise environment summary.

* [ ] Create the bootstrap verification protocol.

* [ ] Run all required local bootstrap tests.

* [ ] Run the applicable real-database verification on OCI.

### 4.2 Step 0.5 verification evidence

Lifecycle status: `Deferred`

Owner: Jan

Support: Current assistant

Step 0.5 implementation remains complete.

Required evidence review:

* [ ] Determine whether preserved evidence confirms execution with:

  ```
  SNOMED_TEST_REAL_DB=true
  ```

* [ ] Repeat the applicable real-Oracle verification during Phase 0
  close-out if the evidence is insufficient.

Repeating this verification does not reopen Step 0.5 implementation.

## 5. Blockers and unresolved questions

### 5.1 OCI virtual environment

Lifecycle status: `Agreed`

Status modifier: `Blocked`

Owner: Jan

Earlier operational information identifies the OCI virtual environment
as:

```text
wenv
```

The production configuration reportedly identifies it as:

```text
venv
```

Required action:

* [ ] Verify the actual OCI virtual-environment name and path before
  changing configuration or documentation.

### 5.2 UZIS correspondence

Lifecycle status: `Agreed`

Status modifier: `Blocked`

Owner: Jan

* `docs/uzis_correspondence.md` version 1.1 contains a draft email to
  MUDr. Molinari that was not sent.
* Her email address remains unknown.
* Any statement that ACE is awaiting her response must be verified and
  corrected if necessary.
* The key requests in `docs/uzis_meeting_prep.md` do not appear to be
  answered in the available meeting notes.
* The possible follow-up gap remains unresolved.

## 6. Deferred work and backlog

### 6.1 Step 0.7 integration and conformance audit

Lifecycle status: `Deferred`

Owner: Jan

Support: Current assistant

Begin only after Step 0.6 is complete.

* [ ] Verify integration and conformance across completed Phase 0
  components.
* [ ] Perform the broader documentation consistency review.
* [ ] Review directory-structure or document-index documentation.
* [ ] Decide whether the repository requires a revised root
  `README.md`.
* [ ] Check cross-document terminology, scope, and stale references.
* [ ] Verify the actual contents and intended use of
  `sql/ddl/tables/`.
* [ ] Resolve privileged Oracle credential-name inconsistencies.
* [ ] Review `scripts/common/run.sh` and corresponding documentation
  claims.
* [ ] Correct the inconsistent Python file-header example in
  `docs/conventions.md`.
* [ ] Check `docs/git_workflow.md` against the closed commit-prefix set
  in `docs/dev_workflow.md`.

### 6.2 Repository maintenance

Lifecycle status: `Deferred`

Owner: Jan

Support: Current assistant

The following items require verification before they are applied or
removed:

* [ ] Review `docs/claude_chat_howto.md` and determine whether it
  should be deleted.
* [ ] Decide whether `docs/patch_26ai.md` should move to the canonical
  `docs/runbooks/` location, creating that directory if required.
  Do not recreate the obsolete singular `docs/runbook/` path.
* [ ] Remove the root `.pytest_cache/` and verify the applicable
  `.gitignore` rule.
* [ ] Remove unneeded `.DS_Store` files without staging unrelated
  filesystem changes.
* [ ] Review the proposed YAML migration of `check_env_vars`.

### 6.3 Environment maintenance

Lifecycle status: `Deferred`

Owner: Jan

Support: Current assistant

#### Ubuntu Python

* [ ] Determine whether and when Ubuntu should be upgraded to
  Python 3.12.
* [ ] Define and run the required compatibility verification before
  changing the approved Python environment.

#### OCI Oracle Database

* [ ] Verify the current Oracle Database version and patch level on
  OCI.

* [ ] Review the evidence from the earlier unsuccessful 26ai upgrade
  or patch attempt.

* [ ] Distinguish whether the unresolved work is:

  * an upgrade to Oracle Database 26ai;
  * a patch for an existing 26ai installation;
  * or recovery from a partially completed attempt.

* [ ] Agree on a safe update or recovery procedure before retrying.

* [ ] Record any continuing dependency on Oracle Support.

### 6.4 Contacts

Lifecycle status: `Deferred`

Owner: Jan

Support: Current assistant

* Viktor Němec remains recorded in `docs/contacts.md` as Jan’s
  original Oracle contact. No change is required.
* [ ] Identify the new person responsible for Jan’s OCI environment
  and add their contact details to `docs/contacts.md` once
  confirmed.

### 6.5 Claude Code evaluation

Lifecycle status: `Deferred`

Owner: Jan

Support: Current assistant

Begin after Phase 0 is complete.

* [ ] Evaluate Claude Code screen-reader accessibility on Ubuntu.
* [ ] Learn and test its behavior in a disposable repository outside
  ACE.
* [ ] Define permissions and agreement-before-change rules.
* [ ] Decide whether any generic, model-independent repository
  guidance is required.
* [ ] Revise `docs/dev_workflow.md` explicitly before Claude Code
  becomes part of the approved ACE workflow.

### 6.6 dev_workflow.md revision — explicit prefix statement

Lifecycle status: `Agreed`

Owner: Jan

Support: Current assistant

Add an explicit step to `dev_workflow.md` §7 requiring the assistant to
state which approved commit-message prefix applies and why, before
presenting any commit message. This applies as a general rule to any
LLM acting as "Current assistant," not to a specific model.

This is a revision to an `Approved` document and requires its own
review-and-approval cycle per `dev_workflow.md` §12, not a same-session
fold-in.

Approved next actions:

1. Draft the specific wording as a new step in §7's "Before committing"
   list.
2. Review and approve the revision.
3. Bump `docs/dev_workflow.md` to the next version.
4. Commit and push the revised workflow document.

## 7. Rejected and superseded items

### 7.1 Separate decision log

Outcome: `Rejected`

Owner: Jan

* A separate `docs/decisions.md` will not be introduced.
* Decisions are recorded in `docs/todo.md`.
* Material outcomes are transferred to `docs/project_summary.md`
  during session close-out.

### 7.2 Previous control-document restructuring order

Outcome: `Superseded`

Owner: Jan

The plan to inspect and classify all parallel control files before
designing the permanent todo structure was replaced by the approved
todo-format-first approach.

### 7.3 Separate session-plan control document

Outcome: `Superseded`

Owner: Jan

The `wrk/session_plan.md` mechanism was replaced by the approved
two-document project-control model.

Current work planning belongs in `docs/todo.md`.
