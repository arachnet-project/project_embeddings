
# Step 0.4 — Configuration Loader — Todo
# =========================================
# Tracks detailed progress for Step 0.4 of Phase 0.
# Last updated: 2026-04-20

## Status: Complete

## Functions

### Complete

_load_yaml_file(path)
- Written: yes
- Round 1: 2026-04-14, 5 tests, 5 passed, 0 failed

_merge_includes(cfg, config_dir)
- Written: yes
- Round 1: 2026-04-14, 4 tests, 4 passed, 0 failed

_resolve_paths(cfg)
- Written: yes
- Round 2: 2026-04-14, 4 tests, 4 passed, 0 failed

_walk_tree(node)
- Written: yes
- Round 2: 2026-04-14, 3 tests, 3 passed, 0 failed

_resolve_interpolation(cfg)
- Written: yes
- Round 2: 2026-04-14, 2 tests, 2 passed, 0 failed

_validate_mandatory_keys(cfg)
- Written: yes
- Round 3: 2026-04-14, 5 tests, 5 passed, 0 failed

load_config(config_dir=None)
- Written: yes
- Round 4: 2026-04-15, 6 tests, 6 passed, 0 failed

_export_to_shell(cfg)
- Written: yes
- Round 4: 2026-04-15, 3 tests, 3 passed, 0 failed

## Test files

tests/test_config_loader_r1_py.py
- Status: complete
- Run with: python tests/test_config_loader_r1_py.py
- Last result: 2026-04-14, 9 passed, 0 failed

tests/test_config_loader_r2_py.py
- Status: complete
- Run with: python tests/test_config_loader_r2_py.py
- Last result: 2026-04-14, 9 passed, 0 failed

tests/test_config_loader_r3_py.py
- Status: complete
- Run with: python tests/test_config_loader_r3_py.py
- Last result: 2026-04-14, 5 passed, 0 failed

tests/test_config_loader_r4_py.py
- Status: complete
- Run with: python tests/test_config_loader_r4_py.py
- Last result: 2026-04-15, 9 passed, 0 failed

tests/test_config_loader_py.py
- Status: complete — orchestrator, runs all four rounds
- Run with: python tests/test_config_loader_py.py
- Last result: 2026-04-15, 32 passed, 0 failed

## Notes

- Test approach: plain python with _report and _summarise pattern.
  Consistent with Steps 0.1 through 0.3.
- No pytest. No conftest.py.
- Type annotations in signatures from _validate_mandatory_keys onward.
  No retrofitting of earlier functions.
- _merge_includes takes config_dir as second parameter.
- load_config takes optional config_dir parameter defaulting to None.
- Valid environments derived dynamically from cfg.environments keys.
- MANDATORY_KEYS list defined at module level in config_loader.py.
- CLI export mode: python -m src.common.config_loader --export
- Orchestrator calls test functions directly, not main(), because
  main() calls sys.exit() which would terminate the process before
  subsequent rounds run.
- Bug fixed during Round 4: _merge_includes double-wrapping.
  Included files that already have the subtree key at top level
  are now merged directly instead of being wrapped again.
=== END FILE: docs/todo_step_0_4.md ===
