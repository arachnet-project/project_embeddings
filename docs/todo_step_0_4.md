
# Step 0.4 — Config Loader Todo

**Date started:** 2026-04-02
**Status:** In progress

---

## Files to produce

- [ ] `src/common/config_loader.py`
- [ ] `tests/test_config_loader_py.py`
- [ ] `tests/protocols/test_config_loader_py.md`

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
Lists: silently skipped in CLI export — not mappable to env vars.
Env var naming: `SNOMED_<SECTION>_<KEY>` uppercase.

---

## Mandatory keys (agreed list)

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

## Open questions

- [ ] Confirm: warn to stderr when skipping a list during CLI export,
      or skip silently?
- [ ] Confirm: cfg.paths shortcut points to
      cfg.environments[active_environment].paths — is this correct?

---

## Done

Nothing yet.
=== END FILE: docs/todo_step_0_4.md ===
