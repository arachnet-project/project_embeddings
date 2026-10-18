# ARC_FILE: docs/todo.md

# ACE — Todo

# Version: 2.6

# Updated: 2026-10-09

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

Resume the interrupted session of 2026-10-09: finish deciding the
`--real-db` design in §2.2 (decisions A–C, D3–D8), then implement it
with its isolated tests.

Session state: the 2026-10-09 session was interrupted, not closed
(`docs/dev_workflow.md` §11). `docs/project_summary.md` therefore
still describes the last closed session (2026-09-26, `5d652db`) and
was deliberately not updated. No code was changed. The only commit of
the interrupted session is the one containing this version of
`docs/todo.md`.

On resumption: run the normal session opening (`dev_workflow.md` §4),
then read §2.2 in full before continuing.

## 2. Active work units

### 2.1 Step 0.6 — remaining scope after the local-mode revision

Lifecycle status: `Agreed`

Owner: Jan

Support: Current assistant

The reviewed local-mode revision (`scripts/bootstrap.sh` v1.10,
`src/common/read_required_modules.py` v2.0,
`src/common/read_required_dirs.py` v2.0, `config/required_modules.json`,
and the revised tests) is pushed in `ccb04f9` and `bcf74ae` and passed
all six suites on OCI. Its outcome is recorded in
`docs/project_summary.md`.

Step 0.6 itself remains `In progress` in `docs/phase0_foundation.md`.
All scope items below were decided in the 2026-09-26 session.

Items:

1. `--real-db` and the Phase 0 exit criteria — resolved. Exit
   criterion 3 requires Step 0.6 to implement the approved `--real-db`
   behavior. This is satisfied by design, implementation, and isolated
   testing of both the unprovisioned-schema path and the
   provisioned-schema connectivity path, verified against isolated
   fixtures simulating successful connections and Oracle failures.
   None of this requires real Oracle schemas to exist, and it can
   proceed now.

   Pending rewording (§2.2 decision C): Oracle returns ORA-01017 both
   for a nonexistent user and for a wrong password, so bootstrap
   cannot assert that a schema is unprovisioned. The requirement here
   and in `docs/phase0_foundation.md` ("bootstrap explains that the
   Phase 1 Oracle setup procedure must run first") must become "logon
   denied — schema not yet provisioned (run the Phase 1 setup) or
   password incorrect".

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
2. Bootstrap verification protocol — stays within Step 0.6, sequenced
   after `--real-db` implementation is complete.
3. Environment summary — test coverage ("Round 5") stays within
   Step 0.6 and must cover the summary block as a whole, including the
   check-result lines, and verify that credential values are never
   displayed. Local-mode coverage may proceed independently;
   real-database-mode summary coverage is included with the isolated
   `--real-db` tests. Specification conformance (active configuration
   profile, log directory) is deferred to §6.1.
4. `docs/phase0_foundation.md` Step 0.6 section — updated (v1.10).
5. §6.8 (isolated fixture-root redesign) remains deferred. Until it is
   done, the bootstrap-level directory-safety checks are exercised
   only at the helper level.

Approved next actions, in order:

1. Review the approved `db_connection.py` interface, then design and
   implement `--real-db` in `scripts/bootstrap.sh` with its isolated
   tests (item 1). In progress: review performed, design under
   decision in §2.2.
2. Add environment-summary test coverage, local mode and
   real-database mode ("Round 5") (item 3).
3. Write the bootstrap verification protocol (item 2).
4. Proceed to §6.1 (Step 0.7) once Step 0.6 closes.

### 2.2 `--real-db` design — session 2026-10-09 (interrupted)

Lifecycle status: `Proposed` (per-decision statuses below)

Owner: Jan

Support: Current assistant

#### 2.2.1 Session-opening verification (2026-10-09)

Repository `/home/jan/project_embeddings` on Ubuntu, branch `main`,
`HEAD` `5d652db` (the 2026-09-26 close-out commit), clean, aligned
with `origin/main` (0 ahead, 0 behind). Matches
`docs/project_summary.md`. `docs/git_workflow.md` v1.2 (2026-04-10)
still exists; its relationship to the closed commit-prefix set
remains deferred per §3.4.

Files reviewed this session: `docs/dev_workflow.md` v2.2,
`docs/project_summary.md`, `docs/conventions.md` v1.6,
`docs/todo.md` v2.5, `src/common/db_connection.py` v1.6,
`config/database.yaml` (config_version 1.4),
`scripts/bootstrap.sh` v1.10, `docs/phase0_foundation.md` Step 0.6
section, `src/common/read_required_modules.py` v2.0,
`src/common/exceptions.py`, `src/common/logger.py`,
`src/common/config_loader.py` 0.4.0, `tests/test_bootstrap_r4_py.py`
v1.3.

#### 2.2.2 Material departure from plan

Decision D1 expands approved next action 1 beyond "implement
`--real-db`": it also corrects local-mode behavior and rewrites the
Round 4 OCI tests. Recorded per `dev_workflow.md` §6.

#### 2.2.3 Review findings — `db_connection.py` (WU1, review applied)

1. `test_connection(cfg, schema)` fits §4.1 unchanged: connects with
   autocommit off, runs `SELECT 1 FROM DUAL`, no commit or DML,
   closes. Raises `SnomedConfigError` or `SnomedDBConnectionError`.
2. It accepts `"sys"` and silently switches to SYSDBA. The bootstrap
   helper must hardcode exactly `snomed` and `snomed_stage` and never
   take a schema name from input; a test must guard this.
3. ORA-01017 is returned for both a nonexistent user and a wrong
   password, so "unprovisioned" cannot be distinguished (see
   decision C).
4. `get_connection` does not chain its final exception (no
   `from last_exc`), contrary to `docs/conventions.md`. The Oracle
   code is available only in `exc.detail` text, which by the
   `exceptions.py` convention carries it (e.g. `ORA-12541`).
5. Every connection is retried once after 2 seconds. A wrong password
   causes two failed logons per schema per run
   (`FAILED_LOGIN_ATTEMPTS` lockout risk); an unreachable host costs
   tens of seconds per schema.
6. Credential safety is sound: passwords are never logged or put in
   exception detail.
7. Thin mode resolves `tns_alias` through `$TNS_ADMIN/tnsnames.ora`.
   Jan verified (2026-10-09) that python-oracledb 2.1.2 supports
   `TNS_ADMIN` in Thin mode; the earlier hypothesis that it did not
   was wrong and is withdrawn. It does not explain the §5 evidence
   gap.
8. Isolated testing is feasible with a fake `oracledb` package first
   on `PYTHONPATH` in a temporary directory.

Further facts from the other reviewed files:

* `logger.py`: importing `db_connection` attaches root handlers to
  stdout and to `$SNOMED_LOG_DIR/snomed.log`. `db_connection`'s INFO
  and WARNING lines therefore appear on the helper's stdout, and every
  run appends to the real log (tests must use a temporary
  `SNOMED_LOG_DIR`).
* `exceptions.py`: `SnomedDBConnectionError.exit_code` is 2; bootstrap
  must map every failure to exit 1 (spec allows only 0 and 1).
* `config_loader.py`: raises plain `FileNotFoundError`, `ValueError`,
  `IOError`, `KeyError` and OmegaConf errors, not `SnomedConfigError`.
  The helper must catch configuration failures broadly. No
  import-time side effects.
* `tests/test_bootstrap_r4_py.py`: currently asserts that local mode
  with `TNS_ADMIN` set requires both application passwords and prints
  "Mode: OCI/production". Affected by D1.

#### 2.2.4 Decision ledger

A — Use `test_connection` unchanged; no edits to `db_connection.py`;
extract the ORA/DPY code from `exc.detail`; record the missing
exception chaining in §6.1. Status: `Proposed`, awaiting Jan.

B — Accept the retry's lockout and timeout behavior; document it in
the bootstrap verification protocol rather than change it. Status:
`Proposed`, awaiting Jan.

C — Reword the "unprovisioned schema" requirement in §2.1 item 1 and
in `docs/phase0_foundation.md` per finding 3. Status: `Proposed`,
awaiting Jan.

D1 — Mode model aligned with the spec. Exactly two bootstrap modes:
local (default) and real-db (`--real-db`). `TNS_ADMIN` no longer
changes what local mode checks; it becomes a real-db precondition.
Summary prints "Mode: local" or "Mode: real-db". Fixes the current
violation of the spec rule that local mode must not require
application-schema passwords. Round 4 OCI tests to be rewritten; a new
test guards that local mode passes with `TNS_ADMIN` set and no
passwords. Status: `Agreed` (2026-10-09).

D2 — Flow. All local checks run first, unchanged; then
`check_real_db`. Bash requires `TNS_ADMIN` set to an existing
directory and `$TNS_ADMIN/tnsnames.ora` readable; client `sqlnet.ora`
is not required (Thin mode does not read it). New helper
`src/common/check_db_connectivity.py`:

* hardcoded `SCHEMAS = ("snomed", "snomed_stage")`, no schema
  argument;
* load configuration; any failure reports CONFIG FAILED, exit 1;
* before any connection, check both schemas' password variables
  (names from `database.yaml` `password_env_var`), reporting all
  missing at once;
* call `test_connection` per schema, continuing after a failure;
* return the TNS alias for the summary.

The `database.yaml` comment is to be corrected (in the D8 `docs:`
commit) to: "`tnsnames.ora` is required for ACE's python-oracledb
Thin-mode alias resolution. Thin mode does not read `sqlnet.ora`; that
file may still be used by Oracle Client/Thick-mode tools involved in
Phase 1 provisioning." Status: `Agreed` (2026-10-09, as amended by
Jan).

D3 — Output channel. Helper writes result records to a
`--result-file` (mktemp, registered in `TEMP_FILES`); helper
stdout/stderr (log lines) captured to another temporary file and
shown only on failure. Alternative considered: prefixed record lines
on stdout. Status: `Proposed`, awaiting Jan.

D4 — Per-schema classification, printing only the code plus a fixed
hint, never raw Oracle text:

* OK — schema and alias.
* LOGON DENIED (ORA-01017) — "schema not provisioned (run the Phase 1
  Oracle setup first) or password incorrect".
* ACCOUNT LOCKED (ORA-28000).
* ENCRYPTION REQUIRED (DPY-3001) — database requires Oracle Native
  Network Encryption, unsupported by ACE's Thin-mode driver; TLS
  (TCPS) or a server-side change needed.
* CONNECTION FAILED (DPY-4011, DPY-6000) — network, listener or TNS
  problem, or required NNE.
* UNREACHABLE (ORA-12xxx, other DPY-6xxx) — network, TNS or listener.
* FAILED — anything else, with its code.

Any failure exits 1. Revised 2026-10-09 after Jan's NNE objection.
Jan's message specifying what the DPY-6000 hint should mention was
cut off and must be completed on resumption. Status: `Proposed`.

D5 — Real-db summary adds "Oracle connection identifier: ARADB",
"Oracle schema snomed: OK", "Oracle schema snomed_stage: OK". No
credential values. Status: `Proposed`, awaiting Jan.

D6 — Isolated tests at two levels. Helper-level: direct invocation
with `--config-dir` fixtures. Bootstrap-level: fake `oracledb`
package in a mkdtemp directory first on `PYTHONPATH`, behavior per
schema set by a control variable (OK, 01017, 28000, 3001, 6000,
12541, other); the fake provides `connect`, `DatabaseError`,
`AUTH_MODE_SYSDBA` and a `Connection` class, and records every call
so tests assert: only `snomed` and `snomed_stage` connected, SYSDBA
never requested, only `SELECT 1 FROM DUAL` executed, nothing
committed. `SNOMED_LOG_DIR` is a mkdtemp directory. Sentinel password
values must never appear in stdout or stderr. Status: `Proposed`,
awaiting Jan.

D7 — Round numbering. Open question: `--real-db` tests as
`tests/test_bootstrap_r6_py.py` (keeping "Round 5" for the summary
coverage), or as r5 with summary coverage moved to r6. Status:
`Proposed`, awaiting Jan.

D8 — Commits, in order: (1) `fix:` D1 local-mode correction plus
rewritten Round 4; (2) `feat:` `--real-db`, `bootstrap.sh` v1.11, the
helper and its tests; (3) `docs:` decision C wording,
`database.yaml` comment, new §6.1 items. Before the first of these,
check `docs/git_workflow.md` against the closed prefix set. Status:
`Proposed`, awaiting Jan.

#### 2.2.5 `bootstrap.sh` changes implied by D1–D5

* `main`: accept `--real-db` alongside `-h`/`--help`; a script-scoped
  mode variable replaces `TNS_ADMIN` as the source of truth for mode
  (the existing code comment says the opposite and must be
  rewritten).
* `check_env_vars`: remove the `TNS_ADMIN`-triggered branch.
* New `check_real_db`, run only with `--real-db` after all local
  checks.
* `print_environment_summary`: mode line and real-db lines per D5.
* `print_usage`: rewrite environment-variable and notes sections.
* Header: v1.11.

Undecided details, to settle while drafting: repeated or combined
flags (e.g. `--real-db --help`); whether an unreadable `tnsnames.ora`
has its own message; exact output-line wording.

#### 2.2.6 Pending OCI evidence (not blocking)

A read-only evidence script was proposed for OCI Frankfurt: installed
python-oracledb version, files in `$TNS_ADMIN` (names only), the
`ARADB` entry in `tnsnames.ora` (protocol TCP or TCPS), non-comment
lines of client `sqlnet.ora`, and server-side `ENCRYPTION` /
`CRYPTO_CHECKSUM` settings if readable. Not yet run. Its main purpose
is now §4.4.

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
  (`oci_sys_db_password_not_required`). Under D1 this guard must be
  preserved in the rewritten tests.

## 4. Blockers and unresolved questions

### 4.1 `--real-db` mode design

Lifecycle status: `Agreed`

Status modifier: `Blocked` only for real-schema verification

Owner: Jan

Support: Current assistant

`--real-db` remains unimplemented in `scripts/bootstrap.sh`. Design is
in progress in §2.2.

Design, implementation, and isolated testing of `--real-db` are not
blocked and may proceed against isolated fixtures simulating
successful connections and Oracle failures.

Real-schema verification: `Blocked` pending Phase 1 provisioning of
the `snomed` and `snomed_stage` schemas as nonprivileged accounts,
and possibly by §4.4.

* `--real-db` verification must confirm each account connects and
  executes a read-only query — nothing more privileged.
* Isolated-fixture testing does not constitute evidence that real
  schemas are reachable; only execution against real Oracle
  schemas does.
* Until real-schema verification is performed, any
  deployment-readiness claim requiring actual Oracle connectivity
  must be treated as unverified.

Required action:

* [x] Review `db_connection.py`'s approved interface for Oracle
  reachability checks — performed 2026-10-09; findings in §2.2.3,
  outcome decisions A–C pending.
* [ ] Design `--real-db`'s check of both `snomed` and `snomed_stage`
  schemas, safe handling of unprovisioned schemas, and confirmation
  that no Oracle objects are modified — without requiring SYS/SYSDBA
  credentials, per §3.5. In progress, §2.2.4.

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

### 4.4 Oracle Native Network Encryption vs Thin mode

Lifecycle status: `Proposed`

Owner: Jan

Support: Current assistant

python-oracledb Thin mode does not support Oracle Native Network
Encryption (NNE) or native checksumming. Per Jan (2026-10-09), OCI
Base Database enables NNE as `REQUIRED` by default; a Thin connection
may then fail with `DPY-3001`, `DPY-4011`, `DPY-6000`, or a
corresponding Oracle error. Supported remedies are TLS (TCPS) or
Thick mode.

`db_connection.py` is Thin-only. If ACE's OCI database enforces NNE,
no ACE code can connect to it, which affects real-schema
verification and all of Phase 1 ingestion. This is a project-level
decision outside Step 0.6. It does not block isolated implementation
of `--real-db`.

Required action:

* [ ] Run the OCI evidence script (§2.2.6) to establish whether ACE's
  database enforces NNE and whether `ARADB` uses TCP or TCPS.
* [ ] If NNE is enforced, decide between TLS, Thick mode, or a
  server-side change, and record the decision.

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
§4.4 may bear on why evidence is missing; the `TNS_ADMIN` hypothesis
was rejected (§2.2.3 finding 7).

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
  `docs/infrastructure.md` §5 uses `SNOMED_ADMIN_DB_PASSWORD`;
  `config/database.yaml` and the now-removed bootstrap check use
  `SNOMED_SYS_DB_PASSWORD` — these never matched).
* [ ] Review `scripts/common/run.sh` and corresponding documentation
  claims.
* [ ] Correct the inconsistent Python file-header example in
  `docs/conventions.md`.
* [ ] Add the Python test invocation convention to
  `docs/conventions.md`: run test files directly with
  `python3 tests/<file>.py`, no pytest. The document currently says
  `python`, not `python3`.
* [ ] Correct the stale "master todo.md … TOOLING section" reference
  in `docs/conventions.md` (ACE's `docs/todo.md` has no such section;
  presumably the arc repository's todo is meant).
* [ ] Check `docs/git_workflow.md` against the closed commit-prefix set
  in `docs/dev_workflow.md`.
* [ ] Decide during the environment-summary conformance review
  whether the active configuration profile and log directory should
  be added to the summary.
* [ ] Spec lists "required project configuration" among local-mode
  checks; `scripts/bootstrap.sh` has no such check. Decide whether to
  add one or revise the spec.
* [ ] `src/common/db_connection.py` `get_connection` does not chain
  its final exception (`from last_exc`), contrary to
  `docs/conventions.md` (subject to decision A).
* [ ] `src/common/config_loader.py` raises plain built-in and
  OmegaConf exceptions, while `src/common/exceptions.py` documents
  `SnomedConfigError` as covering configuration loading.
* [ ] Missing `ARC_FILE:` first line: `config/database.yaml`,
  `src/common/config_loader.py`, `src/common/exceptions.py`,
  `src/common/logger.py`. Redundant old-style second path line in
  `scripts/bootstrap.sh` and `tests/test_bootstrap_r4_py.py`.

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
  `check_required_dirs`). After D1/D2 the array holds only
  `SNOMED_LOG_DIR` and `SNOMED_LOG_LEVEL`.

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
requirements (§§3, 7, 9), not a same-session fold-in. Until then, the
current assistant follows its intent informally.

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

### 7.4 Hypothesis: python-oracledb 2.1.2 Thin mode ignores `TNS_ADMIN`

Outcome: `Rejected` (2026-10-09)

Owner: Jan

Raised by the current assistant from a misreading of the 2.1.2
documentation; Jan verified that 2.1.2 supports `TNS_ADMIN` in Thin
mode. It does not explain the §5 evidence gap.
