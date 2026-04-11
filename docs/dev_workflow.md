# Development Workflow — Arachnet Clinical Embeddings

**Document version:** 1.1
**Date:** 2026-04-10

---

## Overview

Primary development machine: Ubuntu.
Production machine: OCI Frankfurt (Oracle Linux 9, Oracle Database 23ai).
All code flows through GitHub — never directly between machines.

The workflow follows a simple cycle:
write on Ubuntu → test on Ubuntu → push to GitHub → pull on OCI → verify on OCI.

---

## Where to test what

### Test on Ubuntu only

Any code that does not require Oracle or OCI infrastructure:

- `src/common/exceptions.py` — pure Python, no dependencies
- `src/common/logger.py` — reads environment variables, writes files
- `src/common/config_loader.py` — reads YAML, no database
- Unit tests of individual functions in ingestion scripts
- Any data transformation logic (Parquet, pandas, RF2 parsing)

These tests run fast, require no network, and can be iterated rapidly.
If a test does not need Oracle, it must not need Oracle.

### Test on both Ubuntu and OCI

Code that has Oracle-independent logic worth unit testing, but also
needs real database verification:

- `src/common/db_connection.py` — mock-based unit tests on Ubuntu,
  real connection tests on OCI
- RF2 file loading logic — file parsing on Ubuntu, actual INSERT on OCI

### Test on OCI only

Anything that requires a live Oracle 23ai connection:

- Schema creation and DDL execution
- Actual data loading (executemany, APPEND hint, commit)
- Stage-to-production swap (schema rename)
- Validation checks (COUNT queries, referential integrity SQL)
- Full pipeline integration tests (end-to-end ingestion run)

---

## Daily workflow

### Beginning of work session

    # On Ubuntu — always start by pulling
    cd ~/project_embeddings
    git pull
    source venv/bin/activate

    # Confirm you are on the latest commit
    git log --oneline -3

    # Start Claude API session if needed
    python claude_chat.py --session arachnet

If continuing from a previous session, check `docs/todo.md` for the
current task before writing any code.

At the start of each Claude session, paste the current session summary
from `docs/project_summary.md` to restore context. Use `/extract` at
the end of the session to extract produced files directly into the
project tree.

### Writing and testing a unit (Ubuntu)

1. Write or modify the function in Vim.
2. Run the relevant test script immediately:

       python tests/test_<component>_py.py 2>&1 | tee log/test_run.txt

3. Read the output. Fix failures. Repeat until all checks pass.
4. If the function is complete and all tests pass, move to the next
   function. Do not push partial work.

### End of Ubuntu work session

    # Run the full test suite for everything changed today
    python tests/test_exceptions_py.py
    python tests/test_logger_py.py
    bash tests/test_logger_sh.sh
    python tests/test_config_loader_py.py   # when exists

    # If all pass, commit
    git add .
    git commit -m "feat: descriptive message about what changed"
    git push

    # Update todo.md before closing
    vim docs/todo.md
    git add docs/todo.md
    git commit -m "docs: update todo after session"
    git push

### OCI verification (after Ubuntu push)

Run OCI verification when:
- Any file that touches Oracle was changed
- A full phase step is complete
- Before marking a step Complete in phase0_foundation.md

    # On OCI
    cd /home/opc/project_embeddings
    git pull

    # Run Ubuntu-style tests that are platform-independent
    python tests/test_exceptions_py.py
    python tests/test_logger_py.py
    bash tests/test_logger_sh.sh

    # Run OCI-specific tests (connection, DDL, load) when they exist
    python tests/test_db_connection_py.py   # Phase 0 Step 0.5

---

## Test naming and location

What / Where / When to run:

Unit test, pure Python — tests/test_<x>_py.py — Ubuntu, every change
Unit test, Bash script — tests/test_<x>_sh.sh — Ubuntu, every change
Integration test, Oracle — tests/test_<x>_py.py — OCI, after push
Protocol (what to expect) — tests/protocols/test_<x>.md — Reference
Results record — tests/results/test_<x>_<machine>_<date>.txt — After each run

Test results go in `tests/results/` — not committed to Git (in .gitignore).
Protocols go in `tests/protocols/` — committed to Git, updated when
test scope changes.

---

## Commit discipline

Commit one logical unit at a time. A logical unit is:
- One function completed and tested
- One bug fixed and verified
- One document updated
- One configuration change

Do not accumulate a day's work into one large commit. Small commits
make failures easier to isolate and revert.

Never commit:
- Code with failing tests
- Sensitive data (passwords, API keys)
- Log files or test output
- Virtual environment files
- Session JSON or transcript files

Commit message format follows Conventional Commits.
See `docs/git_workflow.md` for the full convention and examples.

---

## Handling a failed OCI test

If a test passes on Ubuntu but fails on OCI:

1. Read the error carefully — is it Oracle-specific or environment-specific?
2. Check environment variables on OCI: echo $SNOMED_LOG_DIR, echo $TNS_ADMIN
3. Check the OCI log file: tail -50 log/snomed.log
4. If it is a code bug, fix on Ubuntu, push, pull on OCI, retest.
5. If it is an environment issue (missing variable, wrong path), fix
   .bashrc on OCI and source ~/.bashrc.
6. Never fix code directly on OCI — always fix on Ubuntu and push.
   OCI is a receiver, never an editor.

Rule: OCI never edits code. Ubuntu never runs Oracle tests.

---

## Marking a step Complete

A step in `docs/phase0_foundation.md` is marked Complete only when:

1. All test scripts for that step pass on Ubuntu.
2. All test scripts for that step pass on OCI.
3. All outputs listed in the step's Outputs section exist and are
   committed to Git.
4. `docs/todo.md` reflects the completed state.
5. A final commit with message `feat: Step X.Y complete` is pushed.

---

## Weekly rhythm (suggested)

Monday: Pull on both machines. Review docs/todo.md. Plan the week's
target — which step or function to complete.

During the week: Write, test, commit, push on Ubuntu daily.
Pull and verify on OCI at least twice — midweek and end of week.

Friday: Ensure all work is pushed and OCI is current. Update
docs/todo.md with the week's progress. Note any blockers or decisions
needed.

---

## Quick reference — commands

    # Ubuntu daily start
    cd ~/project_embeddings && git pull && source venv/bin/activate

    # Run a test
    python tests/test_config_loader_py.py 2>&1 | tee log/test_run.txt

    # Commit and push
    git add . && git commit -m "message" && git push

    # OCI update
    cd /home/opc/project_embeddings && git pull

    # Start Claude session
    python claude_chat.py --session arachnet

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
