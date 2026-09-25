# ARC_FILE: docs/todo.md

# ACE — Todo

# Version: 2.3

# Updated: 2026-09-24

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
completed work. It must be updated when the project's immediate
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

Decide and record the remaining scope of Step 0.6 (§2.1). The
local-mode bootstrap revision is pushed and verified on Ubuntu and OCI,
but Step 0.6 is not complete: items that `docs/phase0_foundation.md`
still lists as open have not been planned.

## 2. Active work units

### 2.1 Step 0.6 — remaining scope after the local-mode revision

Lifecycle status: `Proposed`

Owner: Jan

Support: Current assistant

The reviewed local-mode revision (`scripts/bootstrap.sh` v1.10,
`src/common/read_required_modules.py` v2.0,
`src/common/read_required_dirs.py` v2.0, `config/required_modules.json`,
and the revised tests) is pushed in `ccb04f9` and `bcf74ae` and passed
all six suites on OCI. Its outcome is recorded in
`docs/project_summary.md`.

Step 0.6 itself remains `In progress` in `docs/phase0_foundation.md`.
This unit records what that document still lists as open, so that scope
is decided explicitly rather than by omission. No item below is
approved yet.

Open items:

1. `--real-db` and the Phase 0 exit criteria — resolved. Exit
   criterion 3 requires Step 0.6 to implement the approved `--real-db`
   behavior. This is satisfied by design, implementation, and isolated
   testing of both the unprovisioned-schema path (bootstrap explains
   that the Phase 1 Oracle setup procedure must run first) and the
   provisioned-schema connectivity path, verified against isolated
   fixtures simulating successful connections and Oracle failures.
   None of this requires real Oracle schemas to exist, and it can
   proceed now.

   Isolated tests demonstrate only that bootstrap handles simulated
   outcomes correctly. They are not evidence that real application
   schemas are reachable. Actual execution of `--real-db` against the
   `snomed` and `snomed_stage` schemas occurs after those schemas are
   provisioned by the approved Phase 1 setup procedure and is not
   required to satisfy exit criterion 3.

   Phase 0 exit criterion 7 separately concerns the available
   real-Oracle evidence for the applicable Phase 0 components,
   including explicit use of `SNOMED_TEST_REAL_DB=true` where
   applicable; see §5.

   Schema/user creation (`sys`, `CREATE USER`) stays out of Phase 0
   and out of bootstrap in every case, per §3.5 and
   `docs/phase0_foundation.md`'s Excluded Phase 0 Work list.

   `docs/road_map.md` v1.3 confirms this boundary and the runtime
   order agree with `docs/phase0_foundation.md`.
2. Bootstrap verification protocol. `docs/phase0_foundation.md` lists
   it under Step 0.6 "Approved Outputs in Progress". It has not been
   written and had no todo entry before this unit.
3. Environment summary.
   * Test coverage: only the `Mode:` line (`tests/test_bootstrap_r4_py.py`)
     and the `Python version:` line
     (`tests/test_bootstrap_r_py3_sh.sh`) are asserted. No test covers
     the summary block as a whole, including the check-result lines
     and the specification's rule that it must never display
     passwords. Earlier sessions called this work "Round 5".
   * Specification conformance: `docs/phase0_foundation.md` lists the
     active configuration profile and the log directory among the
     summary's example items. The current summary shows project root,
     virtual environment, Python executable and version, mode, and
     check results, but neither of those two.
4. `docs/phase0_foundation.md` Step 0.6 section is out of date. Its
   "Approved Outputs in Progress" still lists
   `config/required_modules.json` and
   `src/common/read_required_modules.py`, which are now committed. Its
   "Current Outputs" does not list `tests/test_read_required_dirs_py.py`.
5. §6.8 (isolated fixture-root redesign) remains deferred. Until it is
   done, the bootstrap-level directory-safety checks (absolute path,
   `..` component, symlink escape) are exercised only at the helper
   level, not by a bootstrap-level test.

Required action:

* [x] Decide item 1 — resolved above.
* [ ] For items 2 and 3, decide whether to do the work within Step 0.6
  or defer it explicitly under §6.
* [ ] Update the Step 0.6 section of `docs/phase0_foundation.md` to
  match the decisions (item 4).

Approved next actions: none until the scope decision is made.

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
* The requirement to place `set -euo pipefail` "at the top" means
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
* This boundary was actively violated by the inherited
  `scripts/bootstrap.sh`'s `TNS_ADMIN`-triggered
  `SNOMED_SYS_DB_PASSWORD` check. The check was removed in
  `scripts/bootstrap.sh` v1.9 (`ccb04f9`), and
  `tests/test_bootstrap_r4_py.py` carries a regression guard
  (`oci_sys_db_password_not_required`).

## 4. Blockers and unresolved questions

### 4.1 `--real-db` mode design

Lifecycle status: `Agreed`

Status modifier: `Blocked` only for real-schema verification

Owner: Jan

Support: Current assistant

`--real-db` remains unimplemented in `scripts/bootstrap.sh`. Design
requires reviewing the approved `db_connection.py` interface first.

Design, implementation, and isolated testing of `--real-db` are not
blocked and may proceed now against isolated fixtures simulating
successful connections and Oracle failures.

Real-schema verification: `Blocked` pending Phase 1 provisioning of
the `snomed` and `snomed_stage` schemas as nonprivileged accounts.

* `--real-db` verification must confirm each account connects and
  executes a read-only query — nothing more privileged.
* Isolated-fixture testing does not constitute evidence that real
  schemas are reachable; only execution against real Oracle
  schemas does.
* Until real-schema verification is performed, any
  deployment-readiness claim requiring actual Oracle connectivity
  must be treated as unverified.

This item no longer conflicts with Phase 0 exit criterion 3; see
§2.1 item 1.

Required action:

* [ ] Review `db_connection.py`'s approved interface for Oracle
  reachability checks.
* [ ] Design `--real-db`'s check of both `snomed` and `snomed_stage`
  schemas, safe handling of unprovisioned schemas, and confirmation
  that no Oracle objects are modified — without requiring SYS/SYSDBA
  credentials, per §3.5.

### 4.2 OCI virtual environment

Lifecycle status: `Agreed`

Owner: Jan

Verification (2026-09-19): the precondition check of the OCI test
wrapper found exactly one virtual-environment candidate:

```text
./wenv/bin/activate
```

The actual OCI virtual environment is therefore `wenv`.

`config/project.yaml` still declares a path ending in `/venv` for both
the production environment (line 34) and the development environment
(line 50). No reference to those values was found in
`scripts/bootstrap.sh` or in `src/`, which identify the virtual
environment through `VIRTUAL_ENV`. Other possible consumers were not
checked.

Required action:

* [ ] Decide how to reconcile the difference (change the production
  configuration to `wenv`, rename the OCI virtual environment, or
  document the difference), then apply and record the outcome.
* [ ] Check for any other consumer of `paths.venv` before changing
  configuration.

### 4.3 UZIS correspondence

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

## 5. Step 0.5 verification evidence

Lifecycle status: `Agreed`

Status modifier: `Deferred`

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

## 6. Deferred work and backlog

### 6.1 Step 0.7 integration and conformance audit

Lifecycle status: `Agreed`

Status modifier: `Deferred`

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
* [ ] Resolve privileged Oracle credential-name inconsistencies (note:
  `docs/infrastructure.md` §5 uses `SNOMED_ADMIN_DB_PASSWORD`; the
  now-removed bootstrap check used `SNOMED_SYS_DB_PASSWORD` — these
  never matched).
* [ ] Review `scripts/common/run.sh` and corresponding documentation
  claims.
* [ ] Correct the inconsistent Python file-header example in
  `docs/conventions.md`.
* [ ] Add the Python test invocation convention to
  `docs/conventions.md`: run test files directly with
  `python3 tests/<file>.py`, no pytest. The document currently states
  the plain-python `_report`/`_summarise` pattern and "No pytest" but
  not the invocation.
* [ ] Check `docs/git_workflow.md` against the closed commit-prefix set
  in `docs/dev_workflow.md`.

### 6.2 Repository maintenance

Lifecycle status: `Agreed`

Status modifier: `Deferred`

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
* [ ] Review the proposed YAML migration of `check_env_vars` (moving
  the hardcoded bash array to a YAML config, mirroring
  `check_required_dirs`).

### 6.3 Environment maintenance

Lifecycle status: `Agreed`

Status modifier: `Deferred`

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

Lifecycle status: `Agreed`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

* Viktor Němec remains recorded in `docs/contacts.md` as Jan's
  original Oracle contact. No change is required.
* [ ] Remove Jakub Horák from the contacts plan.
* [ ] Identify the new person responsible for Jan's OCI environment
  and add their contact details to `docs/contacts.md` once
  confirmed.

### 6.5 Claude Code evaluation

Lifecycle status: `Agreed`

Status modifier: `Deferred`

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
review-and-approval cycle per `dev_workflow.md`'s explicit revision
requirements (§§3, 7, 9), not a same-session fold-in.

Approved next actions:

1. Draft the specific wording as a new step in §7's "Before committing"
   list.
2. Review and approve the revision.
3. Bump `docs/dev_workflow.md` to the next version.
4. Commit and push the revised workflow document.

### 6.7 ANTHEA transfer of ace_architecture.md

Lifecycle status: `Agreed`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

`docs/ace_architecture.md` is committed to ACE temporarily. Jan has
stated that after `v0.1.0-phase0` is tagged, it should be transferred
into the ANTHEA repository and then removed from ACE. ANTHEA's own
repository status is not yet confirmed; this is revisited when ANTHEA
work resumes after Phase 0.

Required action:

* [ ] After `v0.1.0-phase0` is tagged, commit `docs/ace_architecture.md`
  into the ANTHEA repository (once confirmed reachable).
* [ ] Remove `docs/ace_architecture.md` from the ACE repository once
  the ANTHEA transfer is confirmed.

### 6.8 Isolated fixture-root redesign for bootstrap Round tests

Lifecycle status: `Agreed`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

`tests/test_bootstrap_r1_sh.sh` (and potentially other Round files) currently run against the real project tree because a temporary `config/directory_structure.yaml` override is not possible without patching. This is accepted for now, with real-tree mutations hardened (state-verified before mutating, restored immediately, backed by a suite-level EXIT trap) rather than eliminated.

Deferred work:

* [ ] Design and build an isolated fixture-root harness: a fresh temporary directory per test/fixture group, with `scripts/`, `src/common/`, and a controllable `config/` copied or symlinked in, so `directory_structure.yaml` can be overridden per test without touching the real repository at all.
* [ ] Once the harness exists, extend Round 1 coverage to bootstrap's own independent directory-safety checks (not just the helper's): rejection of an absolute directory path, a `..` component, and a directory that resolves through a symlink escaping `PROJECT_ROOT` — security-relevant behavior introduced in the Step 0.6 revision that is not currently exercised at the bootstrap level, only at the helper level.
* [ ] Once the harness exists, revisit whether the same isolation should extend to the other Round files still running against the real tree.

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
