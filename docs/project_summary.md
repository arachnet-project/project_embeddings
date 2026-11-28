# ARC_FILE: docs/project_summary.md
# ACE — Project Summary

**Updated:** 2026-11-28
**Session:** D1 implementation and control-document close-out, 2026-11-28
**Prepared by:** Current assistant; Jan review pending
**Current phase:** Phase 0 — Foundation and Infrastructure
**Phase status:** In progress

---

## Project context

Arachnet Clinical Embeddings (ACE) is a SNOMED CT terminology and semantic-search project using Oracle, Python, and Bash. It is owned by Arachnet Project z.s. ANTHEA is the parallel theoretical project.

The repository plan is governed by docs/dev_workflow.md and docs/todo.md. Step 0.6 remains in progress. D1 is complete; D2 and the remaining Step 0.6 work remain open.

## Scope of this summary

This summary records the 2026-11-28 D1 bootstrap implementation session and its verification on Ubuntu and OCI Frankfurt.

## State inherited at the start of the work

The last reported Ubuntu repository check before D1 implementation was /home/jan/project_embeddings on main at 2c54008, clean and aligned with origin/main. The post-workshop control-document close-out was committed and pushed in that commit.

## Work completed

### D1 — Bootstrap mode selection

scripts/bootstrap.sh v1.11 and tests/test_bootstrap_r4_py.py v1.4 implement the agreed D1 behavior. Local mode is selected by default and does not change when TNS_ADMIN is set. The summary reports the selected command-line mode. Until D2 is implemented, --real-db fails immediately with the agreed diagnostic and exit status, before any local checks run. Argument handling follows the agreed help precedence, duplicate-flag, and unknown-argument rules.

The two D1 files were committed and pushed from Ubuntu:

    4bc5823 fix: align bootstrap modes and argument handling

The todo was updated to version 2.9 dated 2026-11-28 with the D1 decision amendments and work unit. The close-out update advances it to version 2.10 and records the D1 verification, the D2 next steps, and the deferred workflow review. It is part of the separate docs close-out commit.

## Decisions approved

- D1 is an independent work unit, completed before the remaining --real-db design decisions.
- The D1 commit prefix is fix:.
- The unresolved status and prefix relationship of docs/git_workflow.md will be reviewed in the ARC project after Phase 0.
- After Phase 0, Jan plans to revise the ACE development workflow as a whole for planned use of agents and ARC aliases.sh. The current approved workflow remains in force until a revision is reviewed and approved.

## Verification performed

Round 4 passed on Ubuntu: reported result 15/15. The pasted Ubuntu output did not include the command line.

On OCI Frankfurt, after pulling 4bc5823, Jan ran:

    python3 tests/test_bootstrap_r4_py.py

The test reported 15/15 passed in the wenv environment. The pull was a fast-forward from 584045f to 4bc5823 and reported no conflicts.

These runs verify the Round 4 bootstrap suite on the two machines. They do not verify real Oracle connectivity. The --real-db behavior remains an interim rejection until D2 is implemented.

## Repository state at close-out preparation

After the D1 push, Ubuntu reported main aligned with origin/main at 4bc5823, with docs/todo.md modified and uncommitted. This predates the final control-document updates. Obtain fresh Ubuntu status, recent history, and HEAD/origin/main relationship before finalizing close-out. Record any preserved working-tree changes explicitly.

## Unresolved issues and pending work

- D2 and its prerequisite decisions remain open: A, B, C, D3, D4, D5, D6, D7, and D8 as recorded in docs/todo.md §2.2.4.
- Step 0.6 environment-summary coverage and the bootstrap verification protocol remain pending after D2.
- Real-schema verification remains blocked pending Phase 1 schema provisioning and the applicable network-encryption decision.
- Step 0.7 and Phase 0 close-out evidence remain pending.
- The docs/git_workflow.md status and the broader ACE workflow revision are deferred until after Phase 0, as recorded in docs/todo.md §6.10.

## Immediate next step

Complete the control-document close-out from Ubuntu: update and review docs/todo.md and this summary against live repository state, commit and push the control documents, and verify the final repository state. Then open the next work session for D2 and its unresolved prerequisites. Do not mark Step 0.6 complete.
