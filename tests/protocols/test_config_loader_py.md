# Test Protocol — config_loader.py
# tests/protocols/test_config_loader_py.md
# =========================================
# Records all test rounds for src/common/config_loader.py.
# Last updated: 2026-04-14

## Test approach

Plain python scripts with _report and _summarise pattern.
Run each round with: python tests/test_config_loader_rN_py.py
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
Status: not yet run

## Round 4 — load_config

File: tests/test_config_loader_r4_py.py
Status: not yet run

## Orchestrator

File: tests/test_config_loader_py.py
Status: not yet written — to be written after Round 4 passes
