# Test Protocol — config_loader.py
# tests/protocols/test_config_loader_py.md
# =========================================
# Records all test rounds for src/common/config_loader.py.
# Last updated: 2026-04-15

## Test approach

Plain python scripts with _report and _summarise pattern.
Run each round with: python tests/test_config_loader_rN_py.py
Run full suite with: python tests/test_config_loader_py.py
No pytest. No conftest.py. Consistent with Steps 0.1 through 0.3.

## Round 1 — _load_yaml_file and _merge_includes

File: tests/test_config_loader_r1_py.py
Date: 2026-04-14
Result: 9 passed, 0 failed

Tests:
- load_yaml_file: valid file returns DictConfig
- load_yaml_file: missing file raises FileNotFoundError
- load_yaml_file: empty file raises ValueError
- load_yaml_file: invalid YAML raises ValueError
- load_yaml_file: non-mapping raises ValueError
- merge_includes: no includes key leaves cfg unchanged
- merge_includes: loads included file as sub-tree
- merge_includes: removes includes key
- merge_includes: missing file raises FileNotFoundError

Bugs found: none

Notes:
- _load_yaml_file raises FileNotFoundError and ValueError directly.
  Does not raise SnomedConfigError. This is correct for Step 0.4.
- _merge_includes takes config_dir as second parameter.

## Round 2 — _resolve_paths, _walk_tree, _resolve_interpolation

File: tests/test_config_loader_r2_py.py
Date: 2026-04-14
Result: 9 passed, 0 failed

Tests:
- resolve_paths: adds cfg.paths shortcut
- resolve_paths: unknown environment raises KeyError
- resolve_paths: no environments section raises KeyError
- resolve_paths: missing paths section raises ValueError
- walk_tree: flat dict yields all pairs
- walk_tree: nested dict yields dot-separated keys
- walk_tree: empty dict yields nothing
- resolve_interpolation: plain values pass through
- resolve_interpolation: valid reference passes

Bugs found: none

Notes:
- _resolve_paths derives valid environments dynamically from
  cfg.environments keys. No hardcoded list.
- cfg.paths shortcut uses OmegaConf.to_container with resolve=False
  to preserve interpolation expressions as literals.

## Round 3 — _validate_mandatory_keys

File: tests/test_config_loader_r3_py.py
Date: 2026-04-14
Result: 5 passed, 0 failed

Tests:
- validate_mandatory_keys: all keys present returns cfg
- validate_mandatory_keys: single missing key raises ValueError
- validate_mandatory_keys: multiple missing keys all reported
- validate_mandatory_keys: null value treated as missing
- validate_mandatory_keys: error message has expected prefix

Bugs found: none

Notes:
- All missing keys collected before raising so the error message
  reports everything wrong in a single pass.
- Null values treated as missing. OmegaConf.select returns None
  for both absent keys and keys explicitly set to null.

## Round 4 — load_config and _export_to_shell

File: tests/test_config_loader_r4_py.py
Date: 2026-04-15
Result: 9 passed, 0 failed

Tests:
- load_config: returns DictConfig
- load_config: cfg.paths shortcut present
- load_config: cfg.database present
- load_config: cfg.ingestion present
- load_config: missing config_dir raises FileNotFoundError
- load_config: missing mandatory key raises ValueError
- export_to_shell: produces output
- export_to_shell: output lines have KEY=value format
- export_to_shell: skips list values

Bugs found and fixed:
- _merge_includes double-wrapping bug. Included files that already
  have the subtree key at top level were being wrapped again, producing
  cfg.database.database.tns_alias instead of cfg.database.tns_alias.
  Fixed by checking whether subtree_key is already present in
  included_cfg before wrapping.

Notes:
- load_config default config_dir resolved relative to this file using
  _DEFAULT_CONFIG_DIR constant.
- CLI export mode: python -m src.common.config_loader --export
- List values skipped with WARNING to stderr in _export_to_shell.
- Env var naming in CLI export: SNOMED_SECTION_KEY uppercase.

## Orchestrator — Full Step 0.4 Suite

File: tests/test_config_loader_py.py
Date: 2026-04-15
Result: 32 passed, 0 failed

Ubuntu run: 2026-04-15, 32 passed, 0 failed
OCI run: 2026-04-15, 32 passed, 0 failed

Rounds included:
- Round 1: 9 tests
- Round 2: 9 tests
- Round 3: 5 tests
- Round 4: 9 tests

Notes:
- Orchestrator calls each test function directly rather than calling
  each round's main() function. This is necessary because main() calls
  sys.exit() which would terminate the process before subsequent rounds
  run. Results accumulate in each module's own _results list and are
  read back by the orchestrator for the combined summary.
- omegaconf and pyyaml must be installed via requirements.txt before
  running on any environment.
