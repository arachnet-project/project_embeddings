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
# Author: Jan Mura
# Version: 0.4.0
# =============================================================================

import os
import yaml
from omegaconf import OmegaConf, DictConfig


# Mandatory keys that must be present and non-null after full merge.
# Path keys use shortcut form, e.g. "paths.base" resolves via cfg.paths.
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
    "database.production_schema.user",
    "database.production_schema.password_env_var",
    "database.production_schema.tablespace",
    "database.stage_schema.user",
    "database.stage_schema.password_env_var",
    "database.stage_schema.tablespace",
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

    Each included file is loaded as a named sub-tree. The key used in the
    merged config is the bare filename without extension, e.g. database.yaml
    becomes cfg.database.

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

        # Merge the included config as a named sub-tree.
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


# =============================================================================
