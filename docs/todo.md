# Project Todo — Arachnet Clinical Embeddings

**Version:** 1.7
**Date:** 2026-04-10

Update and commit at the end of every working session.

---

## Status keys

Done — completed, tested, committed.
Pending-code — files to write.
Pending-action — things to do personally.
Pending-decision — open questions blocking work.

---

## Done

### Phase 0 — Foundation

- `config/project.yaml` — complete, REQUIRED markers, dev path corrected 2026-04-02
- `config/database.yaml` — complete, REQUIRED markers, 17 tables
- `config/ingestion.yaml` — complete, REQUIRED markers
- `src/common/exceptions.py` — tested Ubuntu and OCI
- `src/common/logger.py` — tested Ubuntu and OCI
- `scripts/common/logger.sh` — tested Ubuntu and OCI
- `tests/test_exceptions_py.py` — passing
- `tests/test_logger_py.py` — passing
- `tests/test_logger_sh.sh` — passing
- `tests/protocols/test_exceptions_py.md` — complete
- `tests/protocols/test_logger_py.md` — complete
- `tests/protocols/test_logger_sh.md` — complete
- `docs/error_codes.md` — complete
- `docs/phase0_foundation.md` — complete
- `docs/directory_structure.md` — complete
- `docs/git_workflow.md` — v1.2, updated 2026-04-10
- `docs/dev_workflow.md` — v1.1, updated 2026-04-10
- `docs/conventions.md` — v1.2, agreed 2026-04-06
- `config/templates/python_header.py` — produced 2026-04-06

### Step 0.4 — Config loader (in progress)

- `src/common/config_loader.py` — _load_yaml_file and _merge_includes
  complete, Round 1 tests passing 2026-04-10
- `tests/test_config_loader_py.py` — Round 1 complete, 9 passed
- `tests/protocols/test_config_loader_py.md` — Round 1 documented

### Ongoing

- `~/claude_chat.py` — working, used for all sessions

---

## Pending — code

### Step 0.4 — Config loader (remaining functions)
See `docs/todo_step_0_4.md` for detail.

- [ ] `src/common/config_loader.py` — _resolve_paths, _resolve_interpolation,
      _validate_mandatory_keys, load_config still to write
- [ ] `tests/test_config_loader_py.py` — Rounds 2, 3, 4 still to add
- [ ] `tests/protocols/test_config_loader_py.md` — Rounds 2, 3, 4 still to add

### Step 0.5 — Database connection helper

- [ ] `src/common/db_connection.py`
- [ ] `tests/test_db_connection_py.py`
- [ ] `tests/protocols/test_db_connection_py.md`

### Step 0.6 — Bash orchestrator

- [ ] `scripts/run.sh`
- [ ] `tests/test_run_sh.sh`
- [ ] `tests/protocols/test_run_sh.md`

### Other

- [ ] `LICENSE` — BUSL 1.1, project root
- [ ] `tests/results/.gitkeep`
- [ ] Add `software_license: BUSL-1.1` to `project.yaml`

---

## Pending — actions

### Before first Git push

- [ ] Create `tests/results/` and `.gitkeep`
- [ ] Update `.gitignore` per `docs/directory_structure.md`
- [ ] Commit: `feat: Phase 0 Steps 0.1-0.3 complete`
- [ ] Push to GitHub, pull on OCI

### Ubuntu setup

- [ ] Set `.bashrc` — SNOMED_LOG_DIR, SNOMED_LOG_LEVEL, LC_ALL, venv
- [ ] Create and populate venv with `requirements.txt`
- [ ] Upgrade Python to 3.12 before Phase 1 (currently 3.10.12)
- [ ] Always launch `claude_chat.py` from project root for correct /extract paths
- [ ] Add Vim autocommand to ~/.vimrc for Python header template:
      autocmd BufNewFile *.py 0r /home/jan/project_embeddings/config/templates/python_header.py

### OCI setup

- [ ] Set `.bashrc` — all variables including DB passwords and TNS_ADMIN
- [ ] Confirm TNS_ADMIN path, verify tnsnames.ora
- [ ] Confirm Oracle accounts: snomed, snomed_stage, system

---

## Pending — decisions

- [ ] UZIS response — Czech extension: language code, module ID,
      language refset SCTID, RF2 file list. Needed for `ingestion.yaml`.

---

## Session log

### 2026-04-10

- Round 1 of config_loader testing complete — 9 passed after bug fixes
- Bug 1 fixed: yaml.parser.ParserError now caught in _load_yaml_file
- Bug 2 fixed: _merge_includes double-wrapping removed
- dev_workflow.md v1.1 produced — MacBook removed, Claude workflow added
- git_workflow.md v1.2 produced — daily workflow moved to dev_workflow.md,
  conventions pointer updated to docs/conventions.md
- scripts/run_tests.sh produced — simple test runner for Ubuntu

### 2026-04-06

- Sent logger.py to Claude
- Agreed conventions.md as the home for file structure conventions
- Resolved open questions from Step 0.4 todo:
  CLI export skips lists with warn to stderr
  cfg.paths points to cfg.environments[active_environment].paths
- conventions.md v1.2 produced and agreed
- config/templates/python_header.py produced
- Conventions apply from Step 0.4 onward — no retrofitting of earlier files

### 2026-04-02

- Restored session context after interruption
- Sent all three YAML files to Claude for Step 0.4 work
- Corrected dev base path in project.yaml: now /home/jan/project_embeddings
- Renamed dev environment key from "dev" to "development"
- Discussed todo structure — split into master + per-step files
- Step 0.4 in progress

### 2026-04-01

- Fixed typo in logger.py: _VALID_LOG_LEVEL:S to _VALID_LOG_LEVELS:
- Ran all three test scripts on Ubuntu — all passing
- Clarified: DB env vars needed on OCI only

### 2026-03-30

- First Ubuntu test run (test_logger_sh.sh) — PASS
- Fixed LC_ALL locale error — moved to calling scripts
- Dropped macOS as dev platform, Unix/Linux only

### 2026-03-28

- Reorganised tests/ with protocols/ and results/ subdirectories
- Produced all test scripts and protocols

### 2026-03-26

- Produced exceptions.py and error_codes.md
- Decided BUSL 1.1 licence

### 2026-03-21 to 2026-03-25

- Completed Step 0.1 — all three YAML files
- Set up GitHub repo

