# logger.py
# Logging utility for Arachnet Clinical Embeddings.
# Thin wrapper around Python's standard logging module.
# All modules import get_logger() from here — never configure logging directly.
#
# Configuration is read from environment variables only.
# No dependency on config_loader.py or any YAML file.
# This is intentional — the logger must be available before the config
# loader runs. See docs/phase0_foundation.md Step 0.3 bootstrapping note.
#
# Environment variables:
#   SNOMED_LOG_DIR   — directory to write log files to.
#                      Default: ./log/ relative to current working directory.
#   SNOMED_LOG_LEVEL — log verbosity: DEBUG, INFO, WARNING, ERROR.
#                      Default: INFO.
#
# Usage:
#   from src.common.logger import get_logger
#   logger = get_logger(__name__)
#   logger.info("Loading RF2 file: %s", filepath)
#   logger.error("Batch insert failed: %s", detail)
#
# Last modified: 2026-03-27

import logging
import logging.handlers
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"   # ISO 8601, no microseconds
_LOG_BACKUP_COUNT = 30                    # retain 30 days of rotated log files
_DEFAULT_LOG_LEVEL = "INFO"

# Track whether handlers have been initialised to avoid duplicate setup
# when get_logger() is called multiple times across modules.
_initialised = False


# ---------------------------------------------------------------------------
# Internal setup function
# ---------------------------------------------------------------------------

def _initialise_logging() -> None:
    """
    Configure the root logger with a file handler and a stdout handler.
    Called once on first get_logger() invocation.
    Subsequent calls are no-ops due to the _initialised guard.
    """
    global _initialised
    if _initialised:
        return

    # --- Resolve log level ---------------------------------------------------
    level_name = os.environ.get("SNOMED_LOG_LEVEL", _DEFAULT_LOG_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)
    if level_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        # Invalid level specified — fall back and warn
        sys.stderr.write(
            f"WARNING: SNOMED_LOG_LEVEL='{level_name}' is not valid. "
            f"Using INFO.\n"
        )
        level = logging.INFO

    # --- Resolve log directory -----------------------------------------------
    log_dir_str = os.environ.get("SNOMED_LOG_DIR", "")
    if log_dir_str:
        log_dir = Path(log_dir_str)
    else:
        # Fall back to ./log/ relative to current working directory
        log_dir = Path.cwd() / "log"
        sys.stderr.write(
            f"WARNING: SNOMED_LOG_DIR not set. "
            f"Falling back to {log_dir}\n"
        )

    # --- Configure formatter -------------------------------------------------
    formatter = logging.Formatter(
        fmt=_LOG_FORMAT,
        datefmt=_LOG_DATE_FORMAT
    )

    # --- Configure root logger -----------------------------------------------
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # --- Stdout handler — always present -------------------------------------
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(level)
    root_logger.addHandler(stdout_handler)

    # --- File handler — added only if log directory is usable ---------------
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "snomed.log"

        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",          # rotate at midnight
            interval=1,               # every 1 day
            backupCount=_LOG_BACKUP_COUNT,
            encoding="utf-8",
            utc=False                 # use local time for rotation boundary
        )
        # Rotated files are named snomed.log.YYYY-MM-DD
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    except OSError as e:
        # Log directory not writable — fall back to stdout only.
        # This is not fatal. The program continues; we just lose the file log.
        # Do NOT raise here — a logging infrastructure failure must never
        # suppress the original operation.
        sys.stderr.write(
            f"WARNING: Cannot write to log directory '{log_dir}': {e}. "
            f"Logging to stdout only.\n"
        )

    _initialised = True


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given name.

    Call this once at module level in every Python module that needs logging:

        logger = get_logger(__name__)

    The name appears in every log line and should identify the module clearly.
    Using __name__ gives the full dotted module path, e.g. 'src.common.config_loader'.
    For phase scripts, prefer explicit names like 'phase1.loader.sct_concept'.

    Args:
        name: Logger name. Conventionally __name__ of the calling module.

    Returns:
        A standard logging.Logger instance, fully configured.
    """
    _initialise_logging()
    return logging.getLogger(name)


def get_phase_logger(phase: str, step: str, script: str) -> logging.Logger:
    """
    Return a logger named by phase, step, and script for pipeline scripts.
    Produces log lines clearly identifying where in the pipeline a message
    originated.

    Args:
        phase:  Phase identifier, e.g. 'phase0', 'phase1'
        step:   Step identifier, e.g. 'step0.3', 'step1.2'
        script: Script name, e.g. 'load_concepts', 'validate_stage'

    Returns:
        A standard logging.Logger instance.

    Example:
        logger = get_phase_logger('phase1', 'step1.2', 'load_concepts')
        # Produces lines like:
        # 2026-03-27T14:23:01 | INFO     | phase1.step1.2.load_concepts | ...
    """
    _initialise_logging()
    logger_name = f"{phase}.{step}.{script}"
    return logging.getLogger(logger_name)
```
