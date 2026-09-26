# ARC_FILE: docs/project_summary.md

# ACE — Project Summary

**Updated:** 2026-09-26
**Session closed:** 2026-09-26, when the commit containing this summary is pushed
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

This summary covers the session that decided the full remaining scope
of Step 0.6 (`docs/todo.md` §2.1, items 1 through 4), following the
previous close-out at commit `b012d5a` (2026-09-20).

## State inherited at session start

Repository: `/home/jan/project_embeddings` on Ubuntu, branch `main`,
at `b012d5a`, clean, aligned with `origin/main`. Step 0.6's remaining
scope (`todo.md` §2.1) was `Proposed` and undecided.

## Work completed

### §2.1 item 1 and §4.1 — `--real-db` unblocked

Commit `be07afa`, `docs:`:

* `--real-db` design, implementation, and isolated testing are no
  longer blocked by Phase 1 schema provisioning. Only real-schema
  verification (execution against actual Oracle schemas, for exit
  criterion 7) remains blocked.
* Schema/user creation stays out of Phase 0 and bootstrap in every
  case, per §3.5.
* Verified: `docs/road_map.md` v1.3 agrees with
  `docs/phase0_foundation.md` on the Phase 0/Phase 1 Oracle boundary.

### §2.1 items 2, 3, 4 and §6.1 — remaining Step 0.6 scope decided

Commit `97bf3ed`, `docs:`:

* Item 2 (bootstrap verification protocol): stays in Step 0.6,
  sequenced after `--real-db` implementation.
* Item 3 (environment summary): split. Test coverage ("Round 5",
  covering the summary block as a whole, check-result lines, and
  credential-safety in both local and real-database mode) stays in
  Step 0.6. Spec-conformance additions (active configuration profile,
  log directory — both example items, not mandatory) deferred to
  §6.1's Step 0.7 audit, with a corresponding backlog line added there.
* Item 4: `docs/phase0_foundation.md` Step 0.6 output lists reconciled
  with committed files (including the previously unlisted
  `src/common/read_required_dirs.py` and its test), bumped to v1.10.

## Decisions approved

* The four `todo.md` §2.1 items are resolved; no open scope question
  remains for Step 0.6.
* Approved next actions, in order: review `db_connection.py`'s
  interface; design and implement `--real-db` with isolated tests;
  add environment-summary test coverage; write the bootstrap
  verification protocol.
* Versioning convention adopted this session: `todo.md` bumps on
  material change; `phase0_foundation.md` bumps like a `feat`-sized
  change.

## Verification performed

Documentation-only session; no code or tests were touched, so no test
suite applies. Both commits were reviewed against the live file
content and Git status before being made.

## Repository state at session close

Local `HEAD` and `origin/main` will be aligned at the commit
containing this summary, once pushed. Before this close-out commit,
`HEAD` was `97bf3ed`, two commits ahead of the `origin/main` state
inherited at session start (`b012d5a`).

The close-out commit contains exactly:

    docs/project_summary.md
    docs/todo.md

## Preserved working-tree changes

None. The working tree was clean throughout this session; both
substantive commits (`be07afa`, `97bf3ed`) were made from a clean
state.

## Unresolved issues

Unchanged from the previous summary — `--real-db` mode design
(now unblocked for implementation), OCI virtual-environment naming,
UZIS correspondence, Step 0.5 real-Oracle evidence, and the §6
backlog — plus one new backlog line: whether to add the active
configuration profile and log directory to the environment summary
(§6.1), to be decided during the Step 0.7 conformance review.

## Immediate next step

Start a new session. Review `db_connection.py`'s approved interface,
then design and implement `--real-db` in `scripts/bootstrap.sh` with
its isolated tests (`docs/todo.md` §2.1, approved next action 1).
