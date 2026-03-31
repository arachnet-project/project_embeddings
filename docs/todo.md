# Project Todo & Session Log — Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-03-28

Update this document at the end of every working session.
Commit it alongside any other changes from that session.

---

## How to use this document

**Done** — completed and committed items. Move from Pending to Done
when committed to Git and tested.

**Pending — code** — files that need to be written or finalised.

**Pending — actions** — things you need to do: run tests, push,
pull, verify, configure.

**Pending — decisions** — open questions that need an answer before
work can continue.

Add new items at the top of each section so the most recent work
is always visible first.

---

## Done

### Phase 0 — Foundation

- `docs/git_workflow.md` — Git workflow for Ubuntu and OCI
- `docs/directory_structure.md` — full directory structure with naming conventions
- `tests/protocols/test_exceptions_py.md` — test protocol for exceptions.py
- `tests/protocols/test_logger_py.md` — test protocol for logger.py
- `tests/protocols/test_logger_sh.md` — test protocol for logger.sh
- `tests/test_exceptions_py.py` — test script for exceptions.py
- `tests/test_logger_py.py` — test script for logger.py
- `tests/test_logger_sh.sh` — test script for logger.sh (replaces test_logger.sh)
- `scripts/common/logger.sh` — Bash logging library, LC_ALL removed, Unix only
- `docs/phase0_foundation.md` v1.4 — updated, Unix only, locale handling clarified
- `src/common/exceptions.py` — exception hierarchy, complete
- `docs/error_codes.md` — exit code reference, complete
- `config/project.yaml` — complete with REQUIRED markers
- `config/database.yaml` — complete with REQUIRED markers, 17 tables
- `config/ingestion.yaml` — complete with REQUIRED markers
- Verify actual directory structure on disk matches directory_structure.md, complete
---

## Pending — code

### Step 0.3 — Logging (in progress)

- [ ] `src/common/logger.py` — draft produced, not yet reviewed or tested.
      Review the draft before running test_logger_py.py.

### Step 0.4 — Config loader (not started)

- [ ] `src/common/config_loader.py`
- [ ] `tests/test_config_loader_py.py`
- [ ] `tests/protocols/test_config_loader_py.md`

### Step 0.5 — Database connection helper (not started)

- [ ] `src/common/db_connection.py`
- [ ] `tests/test_db_connection_py.py`
- [ ] `tests/protocols/test_db_connection_py.md`

### Step 0.6 — Bash orchestrator (not started)

- [ ] `scripts/run.sh`
- [ ] `tests/test_run_sh.sh`
- [ ] `tests/protocols/test_run_sh.md`

### Other

- [ ] `LICENSE` — BUSL 1.1 licence file to be added to project root
- [ ] `tests/results/.gitkeep` — create to establish results directory in Git
- [ ] `.gitignore` — update with contents from directory_structure.md
- [ ] `project.yaml` — add `software_license: BUSL-1.1` key

---

## Pending — actions (your side)

### Immediate — before first Git push

- [ ] Review `src/common/logger.py` draft
- [ ] Run `python tests/test_exceptions_py.py` on Ubuntu
- [ ] Run `python tests/test_exceptions_py.py` on OCI
- [ ] Run `bash tests/test_logger_sh.sh` on Ubuntu (Pass 1, 2, 3)
- [ ] Run `bash tests/test_logger_sh.sh` on OCI (Pass 1, 2, 3)
- [ ] Run `python tests/test_logger_py.py` on Ubuntu (after reviewing logger.py)
- [ ] Run `python tests/test_logger_py.py` on OCI

- [ ] Create `tests/results/` directory and `.gitkeep` file
- [ ] Create `tests/protocols/` directory
- [ ] Move downloaded files into correct locations per directory_structure.md
- [ ] Update `.gitignore` with contents from directory_structure.md
- [ ] First Git commit and push

### First push commit message suggestion

```
feat: Phase 0 Steps 0.1-0.3 complete — YAML configs, exceptions, logger
```

### After first push

- [ ] `git pull` on the other machine
- [ ] Set `SNOMED_LOG_LEVEL=INFO` in `.bashrc` on both machines
      (change from DEBUG used during testing)

### Ubuntu setup (in progress)

- [ ] Confirm project root path on Ubuntu
      (update git_workflow.md if different from `/home/jan/project_embeddings`)
- [ ] Set up `.bashrc` on Ubuntu per git_workflow.md
- [ ] Create and populate venv on Ubuntu
- [ ] Run all three test scripts on Ubuntu

### OCI

- [ ] Run all three test scripts on OCI
- [ ] Confirm `TNS_ADMIN` path and add to `.bashrc` on OCI

---

## Pending — decisions

- [ ] UZIS response on Czech national extension — language code,
      module ID, language refset SCTID, RF2 file list.
      Needed to complete `national_extensions` section in ingestion.yaml.

- [ ] Ubuntu project root path — confirm exact path before finalising
      git_workflow.md and .bashrc instructions.

- [ ] Python API script for terminal Claude access — Jan to write.
      Will replace browser-based claude.ai for development work.

---

## Session log

### 2026-03-28

- Resolved macOS locale error in logger.sh — LC_ALL moved out of
  sourced library into calling scripts
- Decided: Unix/Linux only — macOS dropped as dev platform
- Mac Studio reserved for Phase 3 ML work only
- Reorganised tests/ directory — protocols/ and results/ subdirectories
- Established test script naming convention: test_<component>_<language>
- Produced test scripts for logger.sh, logger.py, exceptions.py
- Produced protocols for all three test scripts
- Updated directory_structure.md with new tests/ structure and naming table
- Updated git_workflow.md — two platforms only, LC_ALL in .bashrc

### 2026-03-27

- Produced logger.sh draft
- Produced logger.py draft
- Produced test_logger_sh.sh (now renamed test_logger_sh.sh)
- Produced test protocol (now in tests/protocols/test_logger_sh.md)
- Produced phase0_foundation.md v1.3
- Produced git_workflow.md v1.0
- Produced directory_structure.md v1.0
- Jan ran test on macOS — locale error found and resolved

### 2026-03-26

- Produced exceptions.py — complete
- Produced error_codes.md — complete
- Updated phase0_foundation.md — Step 0.2 marked complete
- Decided: no config_schema.md — inline REQUIRED markers are authoritative
- Decided: BUSL 1.1 software licence for project code
- Decided: project targets Unix/Linux only

### 2026-03-21 to 2026-03-25

- Completed Step 0.1 — all three YAML files with REQUIRED markers
- Established architectural decisions (see project summary document)
- Set up GitHub repo from macOS
