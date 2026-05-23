# Development Workflow — Arachnet Clinical Embeddings

**Document version:** 1.2
**Date:** 2026-05-21

---

## Overview

Primary development machine: Ubuntu.
Production machine: OCI Frankfurt (Oracle Linux 9, Oracle Database 23ai).
All code flows through GitHub — never directly between machines.

The workflow follows a simple cycle:
write on Ubuntu → test on Ubuntu → push to GitHub → pull on OCI → verify on OCI.

---

## Shell aliases and functions

The following aliases and functions are defined in `~/.bashrc` on Ubuntu
and OCI. They are the standard way to interact with the project shell.
The canonical `.bashrc` source is managed manually — update all machines
when aliases change.

### Project entry

    ace     cd ~/project_embeddings && source venv/bin/activate

### Clipboard helpers (Ubuntu — xclip based)

    xi      Read from clipboard (xclip -selection clipboard -o)
    xo      Write to clipboard (xclip -selection clipboard -i)
    xed     Open clipboard content in vim, write result back to clipboard
    xcat    Print clipboard content to terminal
    xclear  Clear clipboard

### File helpers

    xcf     Copy file path to clipboard
    xcaf    Copy file content to clipboard

### Test and run helpers

    xbash   Run clipboard content as bash, output to terminal and CB
    xpy     Run clipboard content as python, output to terminal and CB
    xrun    Run clipboard content as bash with venv active
    xcom    Run wrk/commit.sh (git stage/commit/push)
    xpull   Run wrk/pull.sh (git pull + status)

### OCI transfer

    xsup    rsync upload: Ubuntu → OCI transfer directory
    xsd     rsync download: OCI transfer directory → Ubuntu

### Workflow pattern

The typical inner loop on Ubuntu:

1. Claude produces code or a test in chat.
2. `xed` — paste into vim, review, edit if needed, save.
3. `xbash` or `xpy` — run it directly from clipboard.
4. Read output. Fix in chat or in vim. Repeat.
5. When passing, `xcom` — commit and push.

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

    ace                         # cd to project + activate venv
    xpull                       # pull latest from GitHub
    git log --oneline -3        # confirm current commit

Check `docs/todo.md` for current task before writing any code.
At the start of each Claude session, open a new chat within the ACE
project — memory carries over automatically.

### Writing and testing a unit (Ubuntu)

1. Write or modify the function in Vim.
2. Run the relevant test script immediately:

       python tests/test_<component>_py.py 2>&1 | tee log/test_run.txt

   Or using the clipboard loop: write test in Claude → `xpy` → read output.

3. Read the output. Fix failures. Repeat until all checks pass.
4. If the function is complete and all tests pass, move to the next
   function. Do not push partial work.

### End of Ubuntu work session

    # Run all tests changed today
    python tests/test_exceptions_py.py
    python tests/test_logger_py.py
    bash tests/test_logger_sh.sh
    python tests/test_config_loader_py.py

    # Update wrk/commit.sh — set msg= and files=() then:
    xcom

    # Update todo.md before closing
    vim docs/todo.md
    # set msg and files in commit.sh, then:
    xcom

### OCI verification (after Ubuntu push)

Run OCI verification when:
- Any file that touches Oracle was changed
- A full phase step is complete
- Before marking a step Complete in phase0_foundation.md

    # On OCI
    ace
    xpull

    # Run platform-independent tests
    python tests/test_exceptions_py.py
    python tests/test_logger_py.py

    # Run OCI-specific tests when they exist
    SNOMED_TEST_REAL_DB=true python tests/test_db_connection_py.py

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

    ace                                     # enter project on any machine
    xpull                                   # pull latest
    xpy                                     # run clipboard as python
    xbash                                   # run clipboard as bash
    xcom                                    # commit and push via commit.sh
    python tests/test_X_py.py 2>&1 | tee log/test_run.txt   # run a test

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
