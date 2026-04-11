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
# Last modified: 2026-04-09

import sys
from pathlib import Path

from omegaconf import OmegaConf, DictConfig, UnsupportedValueType
from omegaconf.errors import OmegaConfBaseException, GrammarParseError

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
