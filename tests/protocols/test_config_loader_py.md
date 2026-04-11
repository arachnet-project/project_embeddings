All 9 tests pass. Round 1 is complete.

Let me update the test protocol to record the rerun results.

=== BEGIN FILE: tests/protocols/test_config_loader_py.md ===
# Test Protocol — test_config_loader_py.py
# Arachnet Clinical Embeddings

**Module under test:** src/common/config_loader.py
**Test script:** tests/test_config_loader_py.py
**Document version:** 1.2
**Date:** 2026-04-10
**Status:** Round 1 complete — all tests passing

---

## How to run

Activate the venv and run from the project root:

    source venv/bin/activate
    python tests/test_config_loader_py.py

All tests print PASS or FAIL with a summary line at the end.
Exit code 0 means all passed. Exit code 1 means at least one failed.

---

## Round 1 — _load_yaml_file and _merge_includes

**Functions covered:**
- _load_yaml_file(path)
- _merge_includes(cfg)

**Preconditions:**
- venv active with omegaconf installed
- config/project.yaml, config/database.yaml, config/ingestion.yaml present
- SNOMED_LOG_DIR set or ./log/ writable

---

### Test cases

**load_yaml_file: project.yaml returns DictConfig**
What it checks: _load_yaml_file loads project.yaml and returns an
OmegaConf DictConfig instance.
Expected: PASS
Result: PASS

**load_yaml_file: active_environment present**
What it checks: The loaded project.yaml config contains the
active_environment key.
Expected: PASS
Result: PASS

**load_yaml_file: includes key present**
What it checks: The loaded project.yaml config contains the includes key.
Expected: PASS
Result: PASS

**load_yaml_file: missing file raises SnomedConfigError**
What it checks: Passing a nonexistent path raises SnomedConfigError,
not a generic Python exception.
Expected: PASS
Result: PASS

**load_yaml_file: bad YAML raises SnomedConfigError**
What it checks: A malformed YAML file raises SnomedConfigError.
A temporary bad YAML file is created and removed automatically.
Expected: PASS
Result: PASS

**merge_includes: subtrees present**
What it checks: After _merge_includes, cfg contains both cfg.database
and cfg.ingestion.
Expected: PASS
Result: PASS

**merge_includes: cfg.database.tns_alias present**
What it checks: cfg.database.tns_alias is present and non-empty after
merge, confirming database.yaml was loaded and merged correctly.
Expected: PASS
Result: PASS

**merge_includes: cfg.ingestion.release present**
What it checks: cfg.ingestion.release is present after merge, confirming
ingestion.yaml was loaded and merged correctly.
Expected: PASS
Result: PASS

**merge_includes: project.yaml keys preserved**
What it checks: active_environment and project.name are still present
after the merge, confirming the merge did not overwrite the original
project.yaml content.
Expected: PASS
Result: PASS

---

### Round 1 summary

First run: 6 passed, 3 failed. Two bugs identified and fixed.
Bug 1: yaml.parser.ParserError leaked through _load_yaml_file.
Fix: added explicit except clause for yaml.parser.ParserError.
Bug 2: _merge_includes double-wrapped included configs, producing
cfg.database.database.tns_alias instead of cfg.database.tns_alias.
Fix: removed wrapper, merged included_cfg directly since each included
YAML already has the correct top-level key.

Rerun: 9 passed, 0 failed.
Date: 2026-04-10
Platform: Ubuntu
Python version: 3.10.12
Overall: PASS

---

## Round 2 — _resolve_paths and _resolve_interpolation

To be added after those functions are implemented.

---

## Round 3 — _validate_mandatory_keys

To be added after that function is implemented.

---

## Round 4 — Full end to end: load_config

To be added after the public function is complete.

