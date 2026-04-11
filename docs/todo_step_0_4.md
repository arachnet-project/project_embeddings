# Step 0.4 — Config Loader Todo

**Date started:** 2026-04-02
**Status:** In progress

---

## Files to produce

- [x] `src/common/config_loader.py` — in progress
- [ ] `tests/test_config_loader_py.py` — in progress
- [ ] `tests/protocols/test_config_loader_py.md` — in progress

---

## Design summary

Six-part process:

1. Load `project.yaml` with OmegaConf.
2. Read `includes` list, load each file, merge as named sub-trees
   (`cfg.database`, `cfg.ingestion`).
3. Resolve `active_environment`, expose active paths as `cfg.paths`.
4. Walk tree once to force interpolation resolution.
5. Validate mandatory keys — raise `SnomedConfigError` (exit 1) if absent.
6. CLI mode: print `export KEY=VALUE` lines for eval in Bash.
   Module mode: return resolved OmegaConf config object.

Mandatory keys: hardcoded list in loader (Option A).
Lists: warn to stderr and skip in CLI export — not mappable to env vars.
Env var naming: `SNOMED_<SECTION>_<KEY>` uppercase.

---

## Resolved design decisions

- CLI export skips list values with a warning to stderr.
  Rationale: silent skip could cause hard-to-diagnose bugs if a caller
  expects a key to appear in the exported environment and it does not.

- cfg.paths points to cfg.environments[active_environment].paths.
  This is a synthetic shortcut added by the loader after OmegaConf loads
  the file. It is not present in the YAML itself.

- _load_yaml_file is the single YAML loading function. Both the top-level
  file and all included files are loaded through it.

- _merge_includes iterates the includes list internally. load_config
  calls it once and receives the fully merged config.

---

## Mandatory keys

- `active_environment`
- `project.name`
- `project.data_release`
- `project.snomed_notice`
- `environments.<active>.paths.base`
- `environments.<active>.paths.log`
- `environments.<active>.paths.data_volume`
- `environments.<active>.paths.rf2`
- `environments.<active>.paths.parquet`
- `database.tns_alias`
- `database.production_schema.user`
- `database.production_schema.password_env_var`
- `database.production_schema.tablespace`
- `database.stage_schema.user`
- `database.stage_schema.password_env_var`
- `database.stage_schema.tablespace`
- `database.tables`
- `ingestion.release.release_type`
- `ingestion.release.encoding`
- `ingestion.release.delimiter`
- `ingestion.release.skip_header`
- `ingestion.load.batch_size`
- `ingestion.load.truncate_before_load`
- `ingestion.load.commit_frequency`
- `ingestion.load.stop_on_error`
- `ingestion.national_extensions.enabled`
- `ingestion.validation.enabled`
- `ingestion.validation.abort_on_blocking_failure`
- `ingestion.swap.strategy`
- `ingestion.swap.previous_schema_action`
- `ingestion.swap.previous_schema_name`
- `ingestion.logging.level`
- `ingestion.logging.manifest_target`
- `ingestion.logging.manifest_filename`
- `governance.license`

---

## Progress

### Round 1 — complete 2026-04-10

Functions written and tested:
- _load_yaml_file(path)
- _merge_includes(cfg)

Test result: 9 passed, 0 failed after bug fixes.

Bugs found and fixed:
- yaml.parser.ParserError leaked through _load_yaml_file — fixed by
  adding explicit except clause.
- _merge_includes double-wrapped included configs — fixed by merging
  included_cfg directly without wrapper.

### Round 2 — pending

Functions to write next:
- _resolve_paths(cfg)
- _resolve_interpolation(cfg)

### Round 3 — pending

Functions to write:
- _validate_mandatory_keys(cfg)

### Round 4 — pending

Functions to write:
- load_config() — public interface, CLI and module modes


