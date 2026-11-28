# ARC_FILE: docs/todo.md

# ACE — Todo

# Version: 2.10

# Updated: 2026-11-28

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

Complete Phase 0 engineering in order:

1. Finish Step 0.6 (§2.1). D1 is committed and pushed in 4bc5823, and Round 4 passed on Ubuntu and OCI. Next, resume the --real-db design, settle the remaining applicable decisions, and implement D2 with its isolated tests.
2. Complete the Step 0.7 integration and conformance audit in §6.1 after Step 0.6 closes.
3. Review the Step 0.5 evidence and perform any real-Oracle verification required for Phase 0 close-out (§5).

UZIS follow-up in §4.3 and Phase 1 ingestion planning in §6.9 do not block Phase 0 engineering.

Session state: the post-workshop control-document close-out was committed and pushed in 2c54008. D1 was committed and pushed in 4bc5823. Round 4 passed 15/15 on Ubuntu and 15/15 on OCI. D2 and the remaining Step 0.6 work are not complete. At the latest reported Ubuntu status after the D1 push, main was aligned with origin/main and docs/todo.md remained modified and uncommitted; obtain fresh repository state during this close-out.
## 2. Active work units

### 2.1 Step 0.6 — remaining scope after the local-mode revision

Lifecycle status: `Agreed`

Owner: Jan

Support: Current assistant

The reviewed local-mode revision (`scripts/bootstrap.sh` v1.10,
`src/common/read_required_modules.py` v2.0,
`src/common/read_required_dirs.py` v2.0,
`config/required_modules.json`, and the revised tests) is pushed in
`ccb04f9` and `bcf74ae` and passed all six suites on OCI.
Its outcome is recorded in `docs/project_summary.md`.

Step 0.6 itself remains `In progress` in
`docs/phase0_foundation.md`. All scope items below were decided in
the 2026-09-26 session.

Items:

1. `--real-db` and the Phase 0 exit criteria — resolved. Exit
   criterion 3 requires Step 0.6 to implement the approved
   `--real-db` behavior. This is satisfied by design, implementation,
   and isolated testing of both the unprovisioned-schema path and the
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
   schemas are reachable. Actual execution of `--real-db` against
   the `snomed` and `snomed_stage` schemas occurs after those
   schemas are provisioned by the approved Phase 1 setup procedure and
   is not required to satisfy exit criterion 3.

   Phase 0 exit criterion 7 separately concerns the available
   real-Oracle evidence for the applicable Phase 0 components,
   including explicit use of `SNOMED_TEST_REAL_DB=true` where
   applicable; see §5.

   Schema/user creation (`sys`, `CREATE USER`) stays out of
   Phase 0 and out of bootstrap in every case, per §3.5 and
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
   `--real-db` tests. Specification conformance (active
   configuration profile, log directory) is deferred to §6.1.
4. `docs/phase0_foundation.md` Step 0.6 section — updated (v1.10).
5. §6.8 (isolated fixture-root redesign) remains deferred. Until it is
   done, the bootstrap-level directory-safety checks are exercised
   only at the helper level.

Approved next actions, in order:

1. Complete the --real-db design and implementation with isolated tests. D1 is complete in commit 4bc5823; resolve the remaining applicable decisions in §2.2 before D2 implementation.
2. Add environment-summary test coverage for local and real-database modes ("Round 5") after D2 (item 3).
3. Write the bootstrap verification protocol after D2 (item 2).
4. Proceed to §6.1 (Step 0.7) once Step 0.6 closes.

### 2.2 `--real-db` design — sessions 2026-10-09 (interrupted) and 2026-11-28

Lifecycle status: `Proposed` (per-decision statuses below; D1 work
unit in §2.2.8)

Owner: Jan

Support: Current assistant

#### 2.2.1 Session-opening verification (2026-10-09)

Repository `/home/jan/project_embeddings` on Ubuntu, branch
`main`, HEAD `5d652db` (the 2026-09-26 close-out commit),
clean, aligned with `origin/main` (0 ahead, 0 behind). Matches
`docs/project_summary.md`. `docs/git_workflow.md` v1.2
(2026-04-10) still exists; its relationship to the closed
commit-prefix set remains deferred per §3.4.

Files reviewed this session: `docs/dev_workflow.md` v2.2,
`docs/project_summary.md`, `docs/conventions.md` v1.6,
`docs/todo.md` v2.5, `src/common/db_connection.py` v1.6,
`config/database.yaml` (config_version 1.4),
`scripts/bootstrap.sh` v1.10, `docs/phase0_foundation.md`
Step 0.6 section, `src/common/read_required_modules.py` v2.0,
`src/common/exceptions.py`, `src/common/logger.py`,
`src/common/config_loader.py` 0.4.0,
`tests/test_bootstrap_r4_py.py` v1.3.

#### 2.2.2 Material departures from plan

1. (2026-10-09) Decision D1 expands approved next action 1 beyond
   "implement `--real-db`": it also corrects local-mode behavior and
   revises the Round 4 OCI tests. Recorded per `dev_workflow.md` §6.
2. (2026-11-28) D1 is implemented as an independent work unit
   (§2.2.8) before A, B, C and D3–D8 are settled. This matches the
   commit order proposed in D8, but implementation starts while D8 as
   a whole is still `Proposed`. Until D2 is implemented,
   `--real-db` fails immediately (D1 amendment 3). Recorded per
   `dev_workflow.md` §6.

#### 2.2.3 Review findings — `db_connection.py` (WU1, review applied)

1. `test_connection(cfg, schema)` fits §4.1 unchanged: connects with
   autocommit off, runs `SELECT 1 FROM DUAL`, no commit or DML,
   closes. Raises `SnomedConfigError` or
   `SnomedDBConnectionError`.
2. It accepts `sys` and silently switches to SYSDBA. The bootstrap
   helper must hardcode exactly `snomed` and `snomed_stage`
   and never take a schema name from input; a test must guard this.
3. ORA-01017 is returned for both a nonexistent user and a wrong
   password, so "unprovisioned" cannot be distinguished (see
   decision C).
4. `get_connection` does not chain its final exception (no
   `from last_exc`), contrary to `docs/conventions.md`. The
   Oracle code is available only in `exc.detail` text, which by
   the `exceptions.py` convention carries it (e.g. ORA-12541).
5. Every connection is retried once after 2 seconds. A wrong
   password causes two failed logons per schema per run
   (`FAILED_LOGIN_ATTEMPTS` lockout risk); an unreachable host costs
   tens of seconds per schema.
6. Credential safety is sound: passwords are never logged or put in
   exception detail.
7. Thin mode resolves `tns_alias` through
   `$TNS_ADMIN/tnsnames.ora`. Jan verified (2026-10-09) that
   python-oracledb 2.1.2 supports `TNS_ADMIN` in Thin mode; the
   earlier hypothesis that it did not was wrong and is withdrawn. It
   does not explain the §5 evidence gap.
8. Isolated testing is feasible with a fake `oracledb` package
   first on `PYTHONPATH` in a temporary directory.

Further facts from the other reviewed files:

* `logger.py`: importing `db_connection` attaches root
  handlers to stdout and to `$SNOMED_LOG_DIR/snomed.log`.
  `db_connection`'s INFO and WARNING lines therefore appear on the
  helper's stdout, and every run appends to the real log (tests must
  use a temporary `SNOMED_LOG_DIR`).
* `exceptions.py`: `SnomedDBConnectionError.exit_code` is 2;
  bootstrap must map every failure to exit 1 (spec allows only 0 and
  1).
* `config_loader.py`: raises plain `FileNotFoundError`, `ValueError`,
  `IOError`, `KeyError` and OmegaConf errors, not `SnomedConfigError`.
  The helper must catch configuration failures broadly. No import-time
  side effects.
* `tests/test_bootstrap_r4_py.py`: currently asserts that local mode
  with `TNS_ADMIN` set requires both application passwords and
  prints "Mode: OCI/production". Affected by D1.
* `scripts/bootstrap.sh` v1.10 (reported by Jan, 2026-11-28; to be
  re-verified when the file is read): already rejects unknown
  arguments with exit 1 before running any checks, but only refers
  the user to the help option and does not print usage.

#### 2.2.4 Decision ledger

A — Use `test_connection` unchanged; no edits to
`db_connection.py`; extract the ORA/DPY code from `exc.detail`;
record the missing exception chaining in §6.1. Status: `Proposed`,
awaiting Jan.

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
application-schema passwords. Round 4 OCI tests to be revised; a
new test guards that local mode passes with `TNS_ADMIN` set and no
passwords. Status: `Agreed` (2026-10-09; amended 2026-11-28 as
below).

D1 amendments (2026-11-28, agreed by Jan):

1. Round 4 is revised, not replaced: only tests asserting that
   `TNS_ADMIN` selects OCI mode, makes application passwords
   mandatory, or produces "Mode: OCI/production" are changed. The
   log-variable tests and the SYSDBA-credential guard are kept. The
   previous version remains in Git history.
2. Unknown arguments: keep the existing behavior (exit 1, no checks
   run) and additionally print usage to stderr. `-h` and `--help`
   print usage to stdout and exit 0.
3. Interim `--real-db` (until D2 is implemented): print exactly
   `bootstrap: --real-db is not implemented yet (Step 0.6, D2).`
   to stderr and exit 1 immediately — no checks run and no summary
   is printed. Once D2 is implemented, `--real-db` runs all local
   checks first and then `check_real_db`, as D2 specifies.
4. Exit codes stay 0 (success) and 1 (failure), per the bootstrap
   contract.
5. Commit prefix: `fix:`. The interim rejection prevents a false
   success and does not implement the real-db feature, which belongs
   to the D2 `feat:` commit.
6. Non-goals: no configuration-profile (`development`/`production`)
   handling, no D2 helper, no database checks.
7. Argument parsing (agreed 2026-11-28): all arguments are examined
   before any check runs. If `-h` or `--help` appears anywhere,
   usage is printed to stdout and the script exits 0, whatever the
   other arguments (e.g. `--real-db --help`). Otherwise a repeated
   `--real-db` is an error: exit 1, usage to stderr, no checks
   run. Any unknown argument, including `realdb` without the
   leading dashes, fails per amendment 2.
8. Versions (agreed 2026-11-28): the D1 commit carries
   `scripts/bootstrap.sh` v1.11 and `tests/test_bootstrap_r4_py.py`
   v1.4; the D2 `feat:` commit then carries `bootstrap.sh` v1.12
   (amends D8 item 2 and §2.2.5).

D2 — Flow. All local checks run first, unchanged; then
`check_real_db`. Bash requires `TNS_ADMIN` set to an existing
directory and `$TNS_ADMIN/tnsnames.ora` readable; client
`sqlnet.ora` is not required (Thin mode does not read it). New
helper `src/common/check_db_connectivity.py`:

* hardcoded `SCHEMAS = ("snomed", "snomed_stage")`, no schema
  argument;
* load configuration; any failure reports CONFIG FAILED, exit 1;
* before any connection, check both schemas' password variables
  (names from `database.yaml` `password_env_var`), reporting all
  missing at once;
* call `test_connection` per schema, continuing after a failure;
* return the TNS alias for the summary.

The `database.yaml` comment is to be corrected (in the D8 `docs:`
commit) to: "`tnsnames.ora` is required for ACE's
python-oracledb Thin-mode alias resolution. Thin mode does not read
`sqlnet.ora`; that file may still be used by Oracle Client/Thick-mode
tools involved in Phase 1 provisioning." Status: `Agreed`
(2026-10-09, as amended by Jan).

D3 — Output channel. Helper writes result records to a
`--result-file` (mktemp, registered in `TEMP_FILES`); helper
stdout/stderr (log lines) captured to another temporary file and shown
only on failure. Alternative considered: prefixed record lines on
stdout. Record format not yet decided (JSON suggested). Status:
`Proposed`, awaiting Jan.

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
cut off and must be completed. While §4.4 is unresolved, the hint
must not assert NNE as the cause. A, B and C are to be settled
together with D4 as one error-handling unit. Status: `Proposed`.

D5 — Real-db summary adds "Oracle connection identifier: ARADB",
"Oracle schema snomed: OK", "Oracle schema snomed_stage: OK". No
credential values. Status: `Proposed`, awaiting Jan.

D6 — Isolated tests at two levels. Helper-level: direct invocation
with `--config-dir` fixtures. Bootstrap-level: fake `oracledb`
package in a mkdtemp directory first on `PYTHONPATH`, behavior per
schema set by a control variable (OK, 01017, 28000, 3001, 6000, 12541,
other); the fake provides `connect`, `DatabaseError`,
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

D8 — Commits, in order: (1) fix: D1 local-mode correction plus revised Round 4; (2) feat: --real-db, bootstrap.sh v1.12 (D1 amendment 8), the helper and its tests; (3) docs: decision C wording, database.yaml comment, new §6.1 items. The docs/git_workflow.md status/prefix check was not documented as completed before D1; Jan defers that review to the post-Phase-0 ARC workflow review in §6.10. Status: item (1) Pushed in 4bc5823 (prefix fix:); the rest Proposed, awaiting Jan.

#### 2.2.5 `bootstrap.sh` changes implied by D1–D5

* `main`: accept `--real-db` alongside `-h`/`--help`;
  a script-scoped mode variable replaces `TNS_ADMIN` as the source
  of truth for mode (the existing code comment says the opposite and
  must be rewritten). Unknown arguments print usage to stderr and
  exit 1 (D1 amendment 2).
* `check_env_vars`: remove the `TNS_ADMIN`-triggered branch.
* New `check_real_db`, run only with `--real-db` after all
  local checks (D2; in the D1 interim, `--real-db` fails
  immediately per D1 amendment 3).
* `print_environment_summary`: mode line (D1) and real-db lines per
  D5.
* `print_usage`: rewrite environment-variable and notes sections.
* Header: v1.11 (D1); v1.12 (D2), per D1 amendment 8.

Undecided details, to settle while drafting: repeated or combined
flags (settled in D1 amendment 7); whether an unreadable
`tnsnames.ora` has its own message; exact output-line wording.

#### 2.2.6 Pending OCI evidence (not blocking)

A read-only evidence script was proposed for OCI Frankfurt: installed
python-oracledb version, files in `$TNS_ADMIN` (names only), the
`ARADB` entry in `tnsnames.ora` (protocol TCP or TCPS), non-comment
lines of client `sqlnet.ora`, and server-side
`ENCRYPTION`/`CRYPTO_CHECKSUM` settings if readable. Not yet run.
Its main purpose is now §4.4.

#### 2.2.7 Session-opening verification (2026-11-28)

Jan is working on the MacBook (pull-only); repository state was taken
from Ubuntu. Repository `/home/jan/project_embeddings`, branch
`main`, HEAD `2c54008` (`docs: close out project control
documents`), clean, aligned with `origin/main` after fetch (0 ahead,
0 behind). Matches `docs/project_summary.md` (updated 2026-11-24).
Commits since §2.2.1: `0a85bef` (this ledger), `584045f` (SNOMED
vocabulary v0.5), `2c54008` (close-out).

Files reviewed this session: `docs/dev_workflow.md` v2.2,
`docs/project_summary.md`, `docs/todo.md` §2.2 (excerpt).

#### 2.2.8 Work unit — D1 implementation

Status: `Pushed` (2026-11-28; Round 4 passed on Ubuntu and OCI).

Scope: `scripts/bootstrap.sh` and the affected cases in
`tests/test_bootstrap_r4_py.py`, per D1 and its amendments.

Prerequisites:

1. Read the current `scripts/bootstrap.sh`,
   `tests/test_bootstrap_r4_py.py`, `docs/conventions.md` and the
   `docs/phase0_foundation.md` Step 0.6 section.
2. Search the repository for `Mode: OCI/production` and `TNS_ADMIN`
   in `*.py`, `*.sh` and `*.md` files. Report any match outside the
   scope above; do not change it within this unit.
3. The planned docs/git_workflow.md status/prefix check was not documented as complete before the D1 commit. Jan has deferred determining whether that document is active and reconciling it with the approved prefixes to the post-Phase-0 ARC review (§6.10).

Required tests:

1. No arguments, isolated environment: exit 0, "Mode: local".
2. `TNS_ADMIN` set to a temporary directory, both
   application-schema password variables unset: exit 0,
   "Mode: local", no password requested.
3. `--real-db`: exit 1, the exact interim message on stderr, no
   check output, no summary.
4. Unknown argument: exit 1, usage on stderr, no checks run.
5. `-h` and `--help`: exit 0, usage on stdout.
6. Required log-variable checks still enforced (existing tests).
7. SYSDBA credentials never required (existing guard).
8. No output contains "Mode: OCI/production".
9. `--real-db --help` and `--help --real-db`: exit 0, usage on
   stdout, no checks; `--real-db --real-db`: exit 1, usage on
   stderr, no checks (D1 amendment 7).

All tests use isolated temporary fixtures and never a real wallet or
`TNS_ADMIN` path (`dev_workflow.md` §8).

Sequence (updated after D1 verification):

1. Transfer the §2.2 D1 scope to Ubuntu — completed.
2. Produce and transfer scripts/bootstrap.sh v1.11 and tests/test_bootstrap_r4_py.py v1.4 — completed. Round 4 passed 15/15 on Ubuntu and 15/15 on OCI.
3. Commit and push only the two D1 files from Ubuntu — completed in 4bc5823.
4. Complete the control-document close-out in a separate docs: commit and push, then verify the final repository state — pending.

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
* Material session outcomes belong in `docs/project_summary.md`
  during session close-out.
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

* Section 10 of `docs/dev_workflow.md` and the Bash requirements
  in `docs/conventions.md` have no substantive conflict.
* For a managed repository Bash file, the mandatory `ARC_FILE:`
  marker remains on line 1.
* The requirement to place `set -euo pipefail` "at the top"
  means before operational commands. It does not prohibit the required
  marker or introductory comments.
* A temporary script presented in conversation is not a managed
  repository file and therefore does not require an `ARC_FILE:`
  line.
* No change to `docs/conventions.md` is required to resolve the
  Bash review.

### 3.4 Documentation scope

Owner: Jan

* Broad documentation review remains deferred to Step 0.7 unless a
  documentation issue directly blocks current work.
* The inconsistent Python file-header example in
  `docs/conventions.md` is deferred to Step 0.7.
* The status of docs/git_workflow.md and its relationship to the
  approved commit-prefix set will be resolved in the ARC project
  after Phase 0. It does not block current Phase 0 work; see §6.10.
* After Phase 0, review and revise the ACE development workflow as
  a whole for planned use of agents and ARC aliases.sh; see §6.10.
* Automation of session opening and close-out remains deferred until
  it is separately designed, reviewed, and approved.

### 3.5 Phase 0 and Phase 1 Oracle boundary

Owner: Jan

* Phase 0 establishes the staging-schema pattern.
* Phase 0 does not provision Oracle application schemas.
* Creation and use of `snomed` and `snomed_stage` belong to
  Phase 1.
* `db_connection.py` recognizes `sys` only for privileged
  Oracle provisioning.
* Neither local nor real-database bootstrap may use `sys` or
  require SYSDBA credentials.
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

`--real-db` remains unimplemented in `scripts/bootstrap.sh`.
Design, implementation, and isolated testing of `--real-db` are
not blocked and may proceed against isolated fixtures simulating
successful connections and Oracle failures.

Real-schema verification: `Blocked` pending Phase 1 provisioning of
the `snomed` and `snomed_stage` schemas as nonprivileged
accounts, and possibly by §4.4.

* `--real-db` verification must confirm each account connects and
  executes a read-only query — nothing more privileged.
* Isolated-fixture testing does not constitute evidence that real
  schemas are reachable; only execution against real Oracle schemas
  does.
* Until real-schema verification is performed, any deployment-
  readiness claim requiring actual Oracle connectivity must be treated
  as unverified.

Required action:

* [x] Review `db_connection.py`'s approved interface for Oracle
  reachability checks — performed 2026-10-09; findings in §2.2.3,
  outcome decisions A–C pending.
* [ ] Design `--real-db`'s check of both `snomed` and
  `snomed_stage` schemas, safe handling of unprovisioned schemas,
  and confirmation that no Oracle objects are modified — without
  requiring SYS/SYSDBA credentials, per §3.5. In progress, §2.2.4.

### 4.2 OCI virtual environment

Lifecycle status: `Agreed`

Owner: Jan

Verification (2026-09-19): the precondition check of the OCI test
wrapper found exactly one virtual-environment candidate:

    ./wenv/bin/activate

The actual OCI virtual environment is therefore `wenv`.

`config/project.yaml` still declares a path ending in `/venv`
for both the production environment (line 34) and the development
environment (line 50). No reference to those values was found in
`scripts/bootstrap.sh` or in `src/`, which identify the
virtual environment through `VIRTUAL_ENV`. Other possible consumers
were not checked.

Required action:

* [ ] Decide how to reconcile the difference (change the production
  configuration to `wenv`, rename the OCI virtual environment, or
  document the difference), then apply and record the outcome.
* [ ] Check for any other consumer of `paths.venv` before changing
  configuration.

### 4.3 UZIS and SNOMED International follow-up

Lifecycle status: `Agreed`

Status modifier: `Blocked` pending contact details

Owner: Jan

Support: Current assistant

The UZIS workshop took place on 2026-11-23. Jan could not pose his
prepared questions during the session. A SNOMED International
representative invited follow-up contact.

The existing draft in `docs/uzis_correspondence.md` was not
reported as sent. MUDr. Molinari’s email address and the appropriate
SNOMED International contact remain to be confirmed.

Points to clarify:

* Ask MUDr. Molinari for the appropriate SNOMED International contact
  for Jan’s implementation questions.
* Ask whether the implementer or user group mentioned at the workshop
  already exists or is still planned.
* Ask which international implementation guidance applies to Czech
  vendor implementations and how it relates to Czech specifications.
* Clarify what the workshop speaker meant by “EHR” and its connection
  to SNOMED CT. The exact term and relevance to ACE remain unconfirmed.
* Identify the appropriate contact or documentation for supported
  RF2 release checking and downloads.

Approved next actions:

1. Review and update the existing correspondence draft to request the
   contact and these clarifications.
2. Jan reviews and sends the email.
3. Record the reply and any confirmed contact or group details in the
   existing ACE documentation.

### 4.4 Oracle Native Network Encryption vs Thin mode

Lifecycle status: `Proposed`

Owner: Jan

Support: Current assistant

python-oracledb Thin mode does not support Oracle Native Network
Encryption (NNE) or native checksumming. Per Jan (2026-10-09), OCI
Base Database enables NNE as `REQUIRED` by default; a Thin
connection may then fail with `DPY-3001`, `DPY-4011`,
`DPY-6000`, or a corresponding Oracle error. Supported remedies
are TLS (TCPS) or Thick mode.

`db_connection.py` is Thin-only. If ACE's OCI database enforces NNE,
no ACE code can connect to it, which affects real-schema verification
and all of Phase 1 ingestion. This is a project-level decision outside
Step 0.6. It does not block isolated implementation of
`--real-db`.

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

      SNOMED_TEST_REAL_DB=true

* [ ] Repeat the applicable real-Oracle verification during Phase 0
  close-out if the evidence is insufficient.

Repeating this verification does not reopen Step 0.5 implementation.
§4.4 may bear on why evidence is missing; the `TNS_ADMIN`
hypothesis was rejected (§2.2.3 finding 7).

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
* [ ] Verify the actual contents and intended use of `sql/ddl/tables/`.
* [ ] Resolve privileged Oracle credential-name inconsistencies:
  `docs/infrastructure.md` §5 uses
  `SNOMED_ADMIN_DB_PASSWORD`; `config/database.yaml` and the
  now-removed bootstrap check use `SNOMED_SYS_DB_PASSWORD` — these
  never matched.
* [ ] Review `scripts/common/run.sh` and corresponding
  documentation claims.
* [ ] Correct the inconsistent Python file-header example in
  `docs/conventions.md`.
* [ ] Add the Python test invocation convention to
  `docs/conventions.md`: run test files directly with
  `python3 tests/<file>.py`, no pytest. The document currently says
  `python`, not `python3`.
* [ ] Correct the stale "master todo.md … TOOLING section" reference
  in `docs/conventions.md` (ACE's `docs/todo.md` has no such
  section; presumably the arc repository's todo is meant).
* [ ] Resolve docs/git_workflow.md status and prefix compatibility
  after Phase 0 in the ARC workflow review (§6.10).
* [ ] Decide during the environment-summary conformance review
  whether the active configuration profile and log directory should
  be added to the summary.
* [ ] Spec lists "required project configuration" among local-mode
  checks; `scripts/bootstrap.sh` has no such check. Decide whether
  to add one or revise the spec.
* [ ] `src/common/db_connection.py` `get_connection` does not
  chain its final exception (`from last_exc`), contrary to
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
* [ ] Decide whether `docs/patch_26ai.md` should move to the
  canonical `docs/runbooks/` location, creating that directory if
  required. Do not recreate the obsolete singular `docs/runbook/`
  path.
* [ ] Remove the root `.pytest_cache/` and verify the applicable
  `.gitignore` rule.
* [ ] Remove unneeded `.DS_Store` files without staging unrelated
  filesystem changes.
* [ ] Review the proposed YAML migration of `check_env_vars`
  (moving the hardcoded bash array to a YAML config, mirroring
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

### 6.6 `dev_workflow.md` revision — explicit prefix statement

Lifecycle status: `Agreed`

Owner: Jan

Support: Current assistant

Add an explicit step to `dev_workflow.md` §7 requiring the
assistant to state which approved commit-message prefix applies and
why, before presenting any commit message. This applies as a general
rule to any LLM acting as "Current assistant," not to a specific
model.

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

### 6.7 ANTHEA transfer of `ace_architecture.md`

Lifecycle status: `Agreed`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

`docs/ace_architecture.md` is committed to ACE temporarily. Jan
has stated that after `v0.1.0-phase0` is tagged, it should be
transferred into the ANTHEA repository and then removed from ACE.
ANTHEA's own repository status is not yet confirmed; this is revisited
when ANTHEA work resumes after Phase 0.

Required action:

* [ ] After `v0.1.0-phase0` is tagged, commit
  `docs/ace_architecture.md` into the ANTHEA repository (once
  confirmed reachable).
* [ ] Remove `docs/ace_architecture.md` from the ACE repository once
  the ANTHEA transfer is confirmed.

### 6.8 Isolated fixture-root redesign for bootstrap Round tests

Lifecycle status: `Agreed`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

`tests/test_bootstrap_r1_sh.sh` (and potentially other Round files)
currently run against the real project tree because a temporary
`config/directory_structure.yaml` override is not possible without
patching. This is accepted for now, with real-tree mutations hardened
(state-verified before mutating, restored immediately, backed by a
suite-level EXIT trap) rather than eliminated.

Deferred work:

* [ ] Design and build an isolated fixture-root harness: a fresh
  temporary directory per test/fixture group, with `scripts/`,
  `src/common/`, and a controllable `config/` copied or
  symlinked in, so `directory_structure.yaml` can be overridden
  per test without touching the real repository at all.
* [ ] Once the harness exists, extend Round 1 coverage to bootstrap's
  own independent directory-safety checks (not just the helper's):
  rejection of an absolute directory path, a `..` component, and
  a directory that resolves through a symlink escaping
  `PROJECT_ROOT` — security-relevant behavior introduced in the Step
  0.6 revision that is not currently exercised at the bootstrap
  level, only at the helper level.
* [ ] Once the harness exists, revisit whether the same isolation
  should extend to the other Round files still running against the
  real tree.

### 6.9 Phase 1 — SNOMED CT release ingestion and storage

Lifecycle status: `Agreed`

Status modifier: `Deferred`

Owner: Jan

Support: Current assistant

Phase 1 will load SNOMED CT release content into ACE's Oracle database
so ACE can use it as queryable terminology data. RF2 is the release
distribution format; the files must be imported into the planned
database representation. The workshop raised storage and automation,
but the specific process discussed was not confirmed.

Before designing or offering ingestion commercially:

* [ ] Identify the applicable SNOMED CT licensing and use conditions
  for ACE's intended users and deployment.
* [ ] Confirm whether affiliates may check for and download releases
  programmatically, including through the MLDS API or another
  supported mechanism.
* [ ] Confirm whether scheduled, unattended release checks and
  downloads are supported.
* [ ] Design how RF2 content will be loaded, stored, versioned, and
  updated in Oracle, including how failures will be handled.
* [ ] Ask SNOMED International which implementation guidance or
  support resources apply.

These items belong to Phase 1 planning. They do not expand Step 0.6
or block its completion.

### 6.10 Post-Phase 0 development workflow review

Lifecycle status: Agreed

Status modifier: Deferred until Phase 0 is complete

Owner: Jan

Support: Current assistant

After Phase 0, Jan will use the ARC project to resolve whether docs/git_workflow.md remains active and how it relates to the approved commit-prefix rules. Jan also plans to review and revise the ACE development workflow as a whole for planned use of agents and ARC aliases.sh.

The current approved ACE workflow remains in force until any revision is designed, reviewed, and approved. Reconcile the existing §6.6 prefix-statement work within that broader review; do not silently discard it.

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
documentation; Jan verified that 2.1.2 supports `TNS_ADMIN` in
Thin mode. It does not explain the §5 evidence gap.
