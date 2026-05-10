# =============================================================================
# Arachnet Clinical Embeddings — Configuration Loader
# src/common/config_loader.py
# =============================================================================
# Purpose:
#   Loads and merges the three YAML configuration files for the Arachnet
#   Clinical Embeddings project. Handles include directives, environment
#   resolution, path shortcuts, interpolation, and mandatory key validation.
#
# Usage:
#   from src.common.config_loader import load_config
#   cfg = load_config()
#
#   CLI export mode:
#   python -m src.common.config_loader --export
#
# Author: Jan Mura
# Version: 0.4.0
# =============================================================================

import os
import sys
import yaml
from omegaconf import OmegaConf, DictConfig


# Mandatory keys that must be present and non-null after full merge.
# Path keys use shortcut form, e.g. "paths.base" resolves via cfg.paths.
# Mandatory keys / updated

MANDATORY_KEYS = [
    "active_environment",
    "project.name",
    "project.data_release",
    "project.snomed_notice",
    "paths.base",
    "paths.log",
    "paths.data_volume",
    "paths.rf2",
    "paths.parquet",
    "database.tns_alias",
    "database.snomed.user",
    "database.snomed.password_env_var",
    "database.snomed.tablespace",
    "database.snomed_stage.user",
    "database.snomed_stage.password_env_var",
    "database.snomed_stage.tablespace",
    "database.sys.user",
    "database.sys.password_env_var",
    "database.tables",
    "ingestion.release.release_type",
    "ingestion.release.encoding",
    "ingestion.release.delimiter",
    "ingestion.release.skip_header",
    "ingestion.load.batch_size",
    "ingestion.load.truncate_before_load",
    "ingestion.load.commit_frequency",
    "ingestion.load.stop_on_error",
    "ingestion.national_extensions.enabled",
    "ingestion.validation.enabled",
    "ingestion.validation.abort_on_blocking_failure",
    "ingestion.swap.strategy",
    "ingestion.swap.previous_schema_action",
    "ingestion.swap.previous_schema_name",
    "ingestion.logging.level",
    "ingestion.logging.manifest_target",
    "ingestion.logging.manifest_filename",
    "governance.license",
]
# Default config directory relative to this file.
_DEFAULT_CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "config"
)

# Name of the root config file.
_PROJECT_YAML = "project.yaml"


# =============================================================================
# Private functions
# =============================================================================

# --- _load_yaml_file ---
def _load_yaml_file(path):
    """Load a single YAML file and return an OmegaConf DictConfig.

    Parameters
    ----------
    path : str
        Absolute or relative path to the YAML file.

    Returns
    -------
    DictConfig
        Parsed configuration as an OmegaConf DictConfig.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the file is empty, not valid YAML, or does not parse to a mapping.
    IOError
        If the file cannot be read due to a permission or OS error.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Configuration file not found: {}".format(path)
        )

    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except PermissionError as exc:
        raise IOError(
            "Permission denied reading configuration file: {}".format(path)
        ) from exc
    except OSError as exc:
        raise IOError(
            "OS error reading configuration file: {}: {}".format(path, exc)
        ) from exc
    except yaml.YAMLError as exc:
        raise ValueError(
            "YAML parse error in {}: {}".format(path, exc)
        ) from exc

    if raw is None:
        raise ValueError(
            "Configuration file is empty: {}".format(path)
        )

    if not isinstance(raw, dict):
        raise ValueError(
            "Configuration file does not contain a YAML mapping: {}".format(path)
        )

    return OmegaConf.create(raw)
# --- end _load_yaml_file ---


# --- _merge_includes ---
def _merge_includes(cfg, config_dir):
    """Load files listed under the 'includes' key and merge them into cfg.

    Each included file is loaded and merged into cfg. If the included file
    already has the subtree key at its top level, it is merged directly.
    If it does not, it is wrapped under the subtree key derived from the
    filename without extension, e.g. database.yaml becomes cfg.database.

    The 'includes' key itself is removed from the merged result.

    Parameters
    ----------
    cfg : DictConfig
        The base configuration, typically loaded from project.yaml.
    config_dir : str
        Directory from which include paths are resolved.

    Returns
    -------
    DictConfig
        Merged configuration with all included files as named sub-trees.

    Raises
    ------
    FileNotFoundError
        If an included file does not exist.
    ValueError
        If an included file cannot be parsed.
    IOError
        If an included file cannot be read.
    """
    if "includes" not in cfg:
        return cfg

    merged = OmegaConf.to_container(cfg, resolve=False)
    includes = merged.pop("includes")
    base = OmegaConf.create(merged)

    for filename in includes:
        include_path = os.path.join(config_dir, filename)
        included_cfg = _load_yaml_file(include_path)

        # Derive the sub-tree key from the filename without extension.
        subtree_key = os.path.splitext(os.path.basename(filename))[0]

        # If the included file already has the subtree key at its top level,
        # merge it directly to avoid double-wrapping. Otherwise wrap it.
        if subtree_key in included_cfg:
            base = OmegaConf.merge(base, included_cfg)
        else:
            base = OmegaConf.merge(base, OmegaConf.create({subtree_key: included_cfg}))

    return base
# --- end _merge_includes ---


# --- _resolve_paths ---
def _resolve_paths(cfg):
    """Add a cfg.paths shortcut pointing to the active environment's paths.

    The shortcut is a plain dict snapshot taken with resolve=False so that
    OmegaConf interpolation expressions in path values are preserved as
    literal strings rather than being resolved at this stage. This avoids
    premature resolution before all values are in place.

    Parameters
    ----------
    cfg : DictConfig
        Fully merged configuration containing cfg.environments and
        cfg.active_environment.

    Returns
    -------
    DictConfig
        Configuration with cfg.paths added as a shortcut.

    Raises
    ------
    KeyError
        If active_environment is not found in cfg.environments.
    ValueError
        If the active environment does not have a paths section.
    """
    active = OmegaConf.select(cfg, "active_environment")
    if active is None:
        raise KeyError("active_environment is not set in configuration.")

    # Derive valid environments dynamically from cfg.environments keys.
    if "environments" not in cfg:
        raise KeyError("No environments section found in configuration.")

    valid_environments = list(OmegaConf.to_container(cfg.environments, resolve=False).keys())

    if active not in valid_environments:
        raise KeyError(
            "active_environment '{}' is not defined in environments. "
            "Valid values are: {}".format(active, valid_environments)
        )

    env_cfg = OmegaConf.select(cfg, "environments.{}".format(active))

    if env_cfg is None or "paths" not in env_cfg:
        raise ValueError(
            "Environment '{}' does not have a paths section.".format(active)
        )

    # Take a plain dict snapshot with resolve=False to preserve interpolation
    # expressions as literals. This prevents premature resolution.
    paths_snapshot = OmegaConf.to_container(env_cfg.paths, resolve=False)

    return OmegaConf.merge(cfg, OmegaConf.create({"paths": paths_snapshot}))
# --- end _resolve_paths ---


# --- _walk_tree ---
def _walk_tree(node):
    """Recursively walk an OmegaConf node and yield all leaf (key, value) pairs.

    Only DictConfig nodes are descended into. ListConfig nodes and scalar
    leaves are yielded directly without further traversal.

    Parameters
    ----------
    node : any
        An OmegaConf DictConfig, ListConfig, or scalar value.

    Yields
    ------
    tuple
        (key, value) pairs where key is a dot-separated path string and
        value is the leaf value.
    """
    if isinstance(node, DictConfig):
        for key in node:
            child = node[key]
            if isinstance(child, DictConfig):
                for sub_key, sub_value in _walk_tree(child):
                    yield "{}.{}".format(key, sub_key), sub_value
            else:
                yield key, child
    else:
        # Non-DictConfig node passed directly — yield as a single unnamed leaf.
        # This branch is not reached in normal usage but is kept for safety.
        pass
# --- end _walk_tree ---


# --- _resolve_interpolation ---
def _resolve_interpolation(cfg):
    """Force resolution of all OmegaConf interpolation expressions in cfg.

    Walks the entire configuration tree and attempts to access every leaf
    value. Any unresolvable interpolation raises an error immediately rather
    than failing silently at point of use.

    Parameters
    ----------
    cfg : DictConfig
        Fully merged configuration, including cfg.paths shortcut.

    Returns
    -------
    DictConfig
        The same DictConfig, with all interpolation expressions confirmed
        resolvable. The object is not copied; this is a validation pass.

    Raises
    ------
    omegaconf.errors.UnsupportedInterpolationType
        If an interpolation type is not supported.
    omegaconf.errors.InterpolationResolutionError
        If a referenced key does not exist or cannot be resolved.
    """
    for key, value in _walk_tree(cfg):
        # Accessing via OmegaConf.select forces resolution of interpolation.
        _ = OmegaConf.select(cfg, key)

    return cfg
# --- end _resolve_interpolation ---


# --- _validate_mandatory_keys ---
def _validate_mandatory_keys(cfg: DictConfig) -> DictConfig:
    """Check that all mandatory keys are present and non-null in cfg.

    Iterates through MANDATORY_KEYS and uses OmegaConf.select to look up
    each key. A key is considered missing if OmegaConf.select returns None,
    which covers both absent keys and keys explicitly set to null.

    All missing keys are collected before raising so that the error message
    reports everything that is wrong in a single pass.

    Parameters
    ----------
    cfg : DictConfig
        Fully merged configuration, including cfg.paths shortcut.

    Returns
    -------
    DictConfig
        The same cfg if all mandatory keys are present. The object is not
        copied; this is a validation pass.

    Raises
    ------
    ValueError
        If one or more mandatory keys are missing or null. The error message
        lists all missing keys.
    """
    missing = []

    for key in MANDATORY_KEYS:
        value = OmegaConf.select(cfg, key)
        if value is None:
            missing.append(key)

    if missing:
        raise ValueError(
            "Configuration is missing mandatory keys: {}".format(missing)
        )

    return cfg
# --- end _validate_mandatory_keys ---


# --- _export_to_shell ---
def _export_to_shell(cfg: DictConfig) -> None:
    """Print all scalar config values as shell variable assignments.

    Walks the full configuration tree and prints each scalar value as a
    shell variable assignment on stdout. The variable name is derived from
    the dot-separated key path, uppercased, with dots replaced by
    underscores, and prefixed with SNOMED_.

    List values are skipped with a warning to stderr.

    Example output line:
        SNOMED_DATABASE_TNS_ALIAS=mydb

    Parameters
    ----------
    cfg : DictConfig
        Fully merged and validated configuration.

    Returns
    -------
    None
    """
    from omegaconf import ListConfig

    for key, value in _walk_tree(cfg):
        if isinstance(value, ListConfig):
            sys.stderr.write(
                "WARNING: skipping list value for key: {}\n".format(key)
            )
            continue

        var_name = "SNOMED_" + key.upper().replace(".", "_")
        sys.stdout.write("{}={}\n".format(var_name, value))
# --- end _export_to_shell ---


# =============================================================================
# Public functions
# =============================================================================

# --- load_config ---
def load_config(config_dir: str = None) -> DictConfig:
    """Load, merge, and validate the full project configuration.

    Loads project.yaml from config_dir, merges all included files as named
    sub-trees, resolves the active environment paths shortcut, validates all
    interpolation expressions, and checks that all mandatory keys are present
    and non-null.

    If config_dir is None, defaults to the config directory at the project
    root, resolved relative to this file.

    Parameters
    ----------
    config_dir : str, optional
        Path to the directory containing project.yaml and included config
        files. Defaults to None, which uses the project config directory.

    Returns
    -------
    DictConfig
        Fully merged, resolved, and validated configuration.

    Raises
    ------
    FileNotFoundError
        If project.yaml or any included file does not exist.
    ValueError
        If any config file is invalid YAML, empty, not a mapping, or if
        mandatory keys are missing or null.
    IOError
        If any config file cannot be read.
    KeyError
        If active_environment is not set or not found in environments.
    """
    if config_dir is None:
        config_dir = os.path.normpath(_DEFAULT_CONFIG_DIR)

    project_yaml_path = os.path.join(config_dir, _PROJECT_YAML)

    cfg = _load_yaml_file(project_yaml_path)
    cfg = _merge_includes(cfg, config_dir)
    cfg = _resolve_paths(cfg)
    cfg = _resolve_interpolation(cfg)
    cfg = _validate_mandatory_keys(cfg)

    return cfg
# --- end load_config ---


# =============================================================================
# CLI entry point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--export":
        try:
            cfg = load_config()
            _export_to_shell(cfg)
            sys.exit(0)
        except Exception as exc:
            sys.stderr.write("ERROR: {}\n".format(exc))
            sys.exit(1)
    else:
        sys.stderr.write(
            "Usage: python -m src.common.config_loader --export\n"
        )
        sys.exit(1)
# =============================================================================
# End of file
# =============================================================================
