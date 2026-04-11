
# Test Protocol — config_loader.py
# Arachnet Clinical Embeddings

**Module under test:** src/common/config_loader.py
**Test scripts:**
  tests/test_config_loader_r1_py.py
  tests/test_config_loader_r2_py.py
**Document version:** 1.3
**Date:** 2026-04-11
**Status:** Rounds 1 and 2 complete — all tests passing

---

## How to run

Activate the venv and run from the project root:

    source venv/bin/activate
    python tests/test_config_loader_r1_py.py
    python tests/test_config_loader_r2_py.py

Each script prints PASS or FAIL per test and a summary line at the end.
Exit code 0 means all passed. Exit code 1 means at least one failed.

---

## Round 1 — _load_yaml_file and _merge_includes

**Test script:** tests/test_config_loader_r1_py.py
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

**Test script:** tests/test_config_loader_r2_py.py
**Functions covered:**
- _resolve_paths(cfg)
- _resolve_interpolation(cfg)

**Preconditions:**
- Round 1 passing
- venv active with omegaconf installed
- config/project.yaml, config/database.yaml, config/ingestion.yaml present
- SNOMED_LOG_DIR set or ./log/ writable

---

### Test cases

**resolve_paths: cfg.paths present at top level**
What it checks: After _resolve_paths, a paths key exists at the top
level of cfg.
Expected: PASS
Result: PASS

**resolve_paths: cfg.paths.base present**
What it checks: cfg.paths.base is present and non-empty after
_resolve_paths.
Expected: PASS
Result: PASS

**resolve_paths: required path keys present**
What it checks: cfg.paths contains all required keys: base, log,
data_volume, rf2, parquet.
Expected: PASS
Result: PASS

**resolve_paths: invalid environment raises SnomedConfigError**
What it checks: _resolve_paths raises SnomedConfigError if
active_environment is set to an unrecognised value.
Expected: PASS
Result: PASS

**resolve_paths: missing active_environment raises SnomedConfigError**
What it checks: _resolve_paths raises SnomedConfigError if the
active_environment key is absent entirely from the config.
Expected: PASS
Result: PASS

**resolve_interpolation: cfg.paths.base is resolved**
What it checks: After _resolve_interpolation, cfg.paths.base is a plain
string with no interpolation syntax remaining.
Expected: PASS
Result: PASS

**resolve_interpolation: cfg.paths.rf2 is resolved**
What it checks: After _resolve_interpolation, cfg.paths.rf2 is a plain
string that starts with the resolved base path, confirming derived path
interpolation resolved correctly.
Expected: PASS
Result: PASS

**resolve_interpolation: bad reference raises SnomedConfigError**
What it checks: _resolve_interpolation raises SnomedConfigError if an
interpolation expression references a key that does not exist.
Expected: PASS
Result: PASS

---

### Round 2 summary

First run: 8 passed, 0 failed. No bugs found.
Date: 2026-04-11
Platform: Ubuntu
Python version: 3.10.12
Overall: PASS

---

## Round 3 — _validate_mandatory_keys

To be added after that function is implemented.

---

## Round 4 — Full end to end: load_config

To be added after the public function is complete.

