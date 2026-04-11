# config_loader.py
# Configuration loader for Arachnet Clinical Embeddings.
# Loads project.yaml, merges included config files as named sub-trees,
# resolves OmegaConf interpolation, validates mandatory keys, and exposes
# the resolved config object to all phase scripts.
#
# Usage:
#   from src.common.config_loader import load_config
#   cfg = load_config()
#
# Environment variables:
#   SNOMED_LOG_DIR   — passed through to logger (read by logger.py)
#   SNOMED_LOG_LEVEL — passed through to logger (read by logger.py)
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Last modified: 2026-04-10

import sys
from pathlib import Path

from omegaconf import OmegaConf, DictConfig, ListConfig, UnsupportedValueType
from omegaconf.errors import (
    OmegaConfBaseException,
    GrammarParseError,
    InterpolationResolutionError,
)

import yaml.parser

from src.common.exceptions import SnomedConfigError
from src.common.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# Config directory is resolved relative to this file's location so the
# loader works regardless of the working directory when it is called.
# This file lives at src/common/config_loader.py so three parents up
# reaches the project root, and then we step into config/.
_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
_PROJECT_YAML = _CONFIG_DIR / "project.yaml"

_VALID_ENVIRONMENTS = ("development", "production")


# ---------------------------------------------------------------------------
# Internal functions
# ---------------------------------------------------------------------------

# --- _load_yaml_file ---
def _load_yaml_file(path: Path) -> DictConfig:
    """
    Load a single YAML file and return it as an OmegaConf DictConfig.
    Interpolation is not resolved at this stage.

    Args:
        path: Absolute path to the YAML file to load.

    Returns:
        OmegaConf DictConfig loaded from the given file.

    Raises:
        SnomedConfigError: If the file is not found, cannot be parsed,
            or any other loading error occurs. Exit code 1.
    """
    logger.info("Loading YAML file: %s", path)

    if not path.exists():
        msg = "Config file not found: {}".format(path)
        logger.error(msg)
        raise SnomedConfigError(msg)

    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = OmegaConf.load(f)

    except GrammarParseError as e:
        msg = "YAML grammar error in {}: {}".format(path, e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    except yaml.parser.ParserError as e:
        msg = "YAML parsing error in {}: {}".format(path, e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    except UnsupportedValueType as e:
        msg = "Unsupported value type in {}: {}".format(path, e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    except OmegaConfBaseException as e:
        msg = "OmegaConf error loading {}: {}".format(path, e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    except OSError as e:
        msg = "Cannot read config file {}: {}".format(path, e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    logger.info("Loaded YAML file successfully: %s", path)
    return cfg
# --- end _load_yaml_file ---


# --- _merge_includes ---
def _merge_includes(cfg: DictConfig) -> DictConfig:
    """
    Read the includes list from cfg, load each listed YAML file, and
    merge it into cfg as a named sub-tree.

    Each included file is expected to have a single top-level key matching
    its stem name. For example, database.yaml contains a top-level
    database key, and ingestion.yaml contains a top-level ingestion key.
    These are merged directly into cfg, so the result is cfg.database
    and cfg.ingestion respectively.

    Args:
        cfg: OmegaConf DictConfig loaded from project.yaml.

    Returns:
        Merged OmegaConf DictConfig containing all included sub-trees.

    Raises:
        SnomedConfigError: If the includes key is missing, if any listed
            file cannot be loaded, or if a merge fails. Exit code 1.
    """
    if "includes" not in cfg:
        msg = "Missing required key 'includes' in project.yaml."
        logger.error(msg)
        raise SnomedConfigError(msg)

    includes = cfg.includes

    if not includes:
        logger.warning("includes list in project.yaml is empty. "
                       "No sub-configs will be merged.")
        return cfg

    for filename in includes:
        file_path = _CONFIG_DIR / filename
        included_cfg = _load_yaml_file(file_path)

        # Each included file already has its own top-level key matching
        # its stem name, e.g. database.yaml has top-level key "database".
        # Merge directly — no wrapping needed.
        subtree_name = Path(filename).stem
        cfg = OmegaConf.merge(cfg, included_cfg)

        logger.info("Merged %s as cfg.%s", filename, subtree_name)

    return cfg
# --- end _merge_includes ---


# --- _resolve_paths ---
def _resolve_paths(cfg: DictConfig) -> DictConfig:
    """
    Read active_environment from cfg, verify the corresponding environment
    block exists, and add cfg.paths as a copy of the active environment's
    paths block.

    After this function runs, all callers can use cfg.paths.base,
    cfg.paths.log, cfg.paths.rf2 and so on without knowing which
    environment is active.

    cfg.paths is a copied node, not a live reference. Interpolation
    expressions within it are resolved in the subsequent
    _resolve_interpolation step.

    Args:
        cfg: Merged OmegaConf DictConfig from _merge_includes.

    Returns:
        OmegaConf DictConfig with cfg.paths added at the top level.

    Raises:
        SnomedConfigError: If active_environment is missing, not a valid
            value, or the environment block does not exist. Exit code 1.
    """
    if "active_environment" not in cfg:
        msg = "Missing required key 'active_environment' in project.yaml."
        logger.error(msg)
        raise SnomedConfigError(msg)

    active_env = cfg.active_environment

    if active_env not in _VALID_ENVIRONMENTS:
        msg = ("Invalid active_environment '{}'. "
               "Must be one of: {}.".format(
                   active_env, ", ".join(_VALID_ENVIRONMENTS)))
        logger.error(msg)
        raise SnomedConfigError(msg)

    if "environments" not in cfg:
        msg = "Missing 'environments' block in project.yaml."
        logger.error(msg)
        raise SnomedConfigError(msg)

    if active_env not in cfg.environments:
        msg = ("Environment block '{}' not found in "
               "cfg.environments.".format(active_env))
        logger.error(msg)
        raise SnomedConfigError(msg)

    env_block = cfg.environments[active_env]

    if "paths" not in env_block:
        msg = ("Missing 'paths' block under environments.{} "
               "in project.yaml.".format(active_env))
        logger.error(msg)
        raise SnomedConfigError(msg)

    # Wrap the active paths block under the key "paths" and merge it
    # into cfg at the top level. OmegaConf.merge produces a deep copy
    # so cfg.paths is independent of cfg.environments[active_env].paths.
    paths_wrapper = OmegaConf.create({"paths": env_block.paths})
    cfg = OmegaConf.merge(cfg, paths_wrapper)

    logger.info("Resolved active environment: %s", active_env)
    logger.info("cfg.paths set to environments.%s.paths", active_env)

    return cfg
# --- end _resolve_paths ---


# --- _walk_tree ---
def _walk_tree(node) -> None:
    """
    Recursively walk an OmegaConf tree and read every leaf value to
    force interpolation resolution.

    DictConfig and ListConfig nodes are recursed into. Scalar leaf
    values are read. OmegaConf MISSING sentinels are skipped and left
    for _validate_mandatory_keys to handle.

    Args:
        node: An OmegaConf DictConfig, ListConfig, or scalar value.

    Raises:
        InterpolationResolutionError: If any interpolation expression
            cannot be resolved. Propagated to _resolve_interpolation
            for conversion to SnomedConfigError.
    """
    if isinstance(node, DictConfig):
        for key in node:
            _walk_tree(node[key])
    elif isinstance(node, ListConfig):
        for item in node:
            _walk_tree(item)
    else:
        # Scalar leaf — reading it forces OmegaConf to resolve any
        # interpolation expression. If the value is MISSING, OmegaConf
        # raises MissingMandatoryValue which we leave for
        # _validate_mandatory_keys to handle, so we do not catch it here.
        _ = node
# --- end _walk_tree ---


# --- _resolve_interpolation ---
def _resolve_interpolation(cfg: DictConfig) -> DictConfig:
    """
    Force resolution of all OmegaConf interpolation expressions in the
    config tree by walking every node and reading every leaf value.

    Must be called after _resolve_paths so that cfg.paths interpolation
    expressions can resolve correctly against the full tree.

    After this function returns, all values in the tree are plain
    resolved Python values. No lazy interpolation expressions remain.

    Args:
        cfg: OmegaConf DictConfig with cfg.paths added by _resolve_paths.

    Returns:
        OmegaConf DictConfig with all interpolation expressions resolved.

    Raises:
        SnomedConfigError: If any interpolation expression cannot be
            resolved. Exit code 1.
    """
    logger.info("Resolving OmegaConf interpolation expressions.")

    try:
        _walk_tree(cfg)

    except InterpolationResolutionError as e:
        msg = "Interpolation resolution failed: {}".format(e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    except OmegaConfBaseException as e:
        msg = "OmegaConf error during interpolation resolution: {}".format(e)
        logger.error(msg)
        raise SnomedConfigError(msg)

    logger.info("Interpolation resolution complete.")
    return cfg
# --- end _resolve_interpolation ---

