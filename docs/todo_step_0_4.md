
=== BEGIN FILE: docs/todo_step_0_4.md ===
# Step 0.4 — Configuration Loader — Todo
# =========================================
# Tracks detailed progress for Step 0.4 of Phase 0.
# Last updated: 2026-04-14

## Status: In progress

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

### Pending

_validate_mandatory_keys(cfg)
- Written: no
- Round 3: not yet run

load_config(config_dir=None)
- Written: no
- Round 4: not yet run

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
- Status: not yet written

tests/test_config_loader_r4_py.py
- Status: not yet written

tests/test_config_loader_py.py
- Status: not yet written — orchestrator, runs all rounds
- To be written after Round 4 passes

## Notes

- Test approach: plain python with _report and _summarise pattern.
  Consistent with Steps 0.1 through 0.3.
- conftest.py was added to project root during a pytest experiment
  and has been removed. Not part of the project.
- _merge_includes takes config_dir as second parameter.
- load_config takes optional config_dir parameter defaulting to None.
- Valid environments derived dynamically from cfg.environments keys.
- MANDATORY_KEYS list defined at module level in config_loader.py.
=== END FILE: docs/todo_step_0_4.md ===
