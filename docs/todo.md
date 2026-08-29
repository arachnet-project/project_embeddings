# ARC_FILE: docs/todo.md

# ACE — Todo

# Updated: 2026-08-29

# Status: Transitional — permanent format not yet approved

## Current work unit

### Development workflow

Status: `Approved`, `Applied`

* `docs/dev_workflow.md` version 2.2 was reviewed and approved.

* The stored Ubuntu file was verified against the approved text.

* Whitespace verification passed.

* The stored file has SHA-256:

  ```
  bb753f1a7f58ddc15b2fafe2bcd4b59d60d8ff9b34bfe4c3a0c18a70a8bc3936
  ```

* Commit and push the workflow together with the updated project
  summary and todo document during session close-out.

## Immediate next work

1. Inspect the Bash-script requirements in `docs/conventions.md`.
2. Resolve any conflict between those requirements and Section 10 of
   `docs/dev_workflow.md`.
3. Inspect the existing planning and control files, including:

   * `wrk/session_plan.md`, if present;
   * step-specific todo documents;
   * `docs/project_memory.md`.
4. Classify their contents as:

   * current work;
   * backlog;
   * unresolved decision;
   * completed history;
   * obsolete material.
5. Design and approve the permanent `docs/todo.md` structure.
6. Transfer all relevant unfinished material into `docs/todo.md`.
7. Delete obsolete parallel project-control documents only after their
   relevant contents have been preserved.
8. Resume Step 0.6 bootstrap close-out.

## Current decisions

* ACE uses exactly two project-control documents:

  * `docs/project_summary.md`;
  * `docs/todo.md`.
* Both control documents remain tracked in Git.
* Both must be updated, reviewed, committed, and pushed before a
  substantial session is closed.
* No separate decision log will be introduced.
* Rejected and superseded items are recorded in `docs/todo.md`.
* Material session outcomes are preserved in
  `docs/project_summary.md`.
* Broad documentation review is deferred to Step 0.7 unless a
  document directly blocks current work.
* Automation of session opening and close-out remains deferred until
  it is separately designed, reviewed, and approved.

## Step 0.6 bootstrap close-out

Status: `Applied`, `Blocked` pending review and verification

* [ ] Review and validate `config/required_modules.json`.
* [ ] Strengthen validation in
  `src/common/read_required_modules.py`.
* [ ] Replace tests that modify repository configuration with isolated
  fixtures.
* [ ] Confirm the approved local bootstrap behavior.
* [ ] Confirm the approved `--real-db` bootstrap interface.
* [ ] Verify that neither bootstrap mode requires SYSDBA credentials.
* [ ] Complete the concise environment summary.
* [ ] Create the bootstrap verification protocol.
* [ ] Run all required local bootstrap tests.
* [ ] Run the applicable real-database verification on OCI.

## Step 0.5 verification evidence

Status: `Deferred`

* [ ] Determine whether preserved evidence confirms execution with:

  ```
  SNOMED_TEST_REAL_DB=true
  ```

* [ ] Repeat the applicable real-Oracle verification during Phase 0
  close-out if the evidence is insufficient.

Step 0.5 implementation remains complete.

## Step 0.7 integration and conformance audit

Status: `Deferred`

Begin only after Step 0.6 is complete.

* [ ] Verify integration and conformance across the completed Phase 0
  components.
* [ ] Perform the broader documentation consistency review.
* [ ] Review the directory-structure or document-index documentation.
* [ ] Decide whether the repository requires a revised root
  `README.md`.
* [ ] Check cross-document terminology, scope, and stale references.
* [ ] Verify the actual contents and intended use of
  `sql/ddl/tables/`.
* [ ] Resolve privileged Oracle credential-name inconsistencies.
* [ ] Verify the actual OCI virtual-environment name and path.
* [ ] Review `scripts/common/run.sh` and the corresponding
  documentation claims.

## Repository-maintenance backlog

Status: `Deferred`

The following older items require verification before they are applied
or removed from the backlog:

* [ ] Determine whether `scripts/bootstrap_v1.8.sh` still exists and
  whether any relevant content remains.
* [ ] Review `docs/claude_chat_howto.md` and confirm whether it should
  be deleted.
* [ ] Review the proposed move of `docs/patch_26ai.md` to
  `docs/runbooks/patch_26ai.md`.
* [ ] Check the singular `docs/runbook/` and plural
  `docs/runbooks/` directories.
* [ ] Remove the root `.pytest_cache/` and verify the applicable
  `.gitignore` rule.
* [ ] Remove unneeded `.DS_Store` files without staging unrelated
  filesystem changes.
* [ ] Decide whether `docs/project_memory.md` has any non-control
  purpose. It must not become a third project-control document.
* [ ] Review the proposed YAML migration of `check_env_vars`.
* [ ] Consider the Python 3.12 upgrade on Ubuntu.

## Contacts backlog

Status: `Deferred`

* [ ] Update `docs/contacts.md` with Jakub Horak’s role in the Oracle
  26ai patch correspondence.
* [ ] Add Viktor Nemec after his details are confirmed.

## Open correspondence conflicts

Status: `Blocked`

* `docs/uzis_correspondence.md` version 1.1 contains a draft email to
  MUDr. Molinari that was not sent. Her email address remains unknown.
  Any statement that ACE is awaiting her response must be verified and
  corrected if necessary.
* The key requests recorded in `docs/uzis_meeting_prep.md` do not
  appear to be answered in the available meeting notes. The possible
  follow-up gap remains unresolved.
