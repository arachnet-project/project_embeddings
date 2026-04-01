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
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Last modified: 2026-04-01

import logging
import logging.handlers
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_LOG_BACKUP_COUNT = 30
_DEFAULT_LOG_LEVEL = "INFO"

_VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
# Guard against duplicate handler registration when get_logger() is called
# multiple times across modules in the same process. Without this guard,
# each call would add another handler and every log line would print
# multiple times.
_initialised = False


# ---------------------------------------------------------------------------
# Internal setup function
# ---------------------------------------------------------------------------

def _initialise_logging() -> None:
    """
    Configure the root logger with a file handler and a stdout handler.
    Called once on first get_logger() or get_phase_logger() invocation.
    Subsequent calls are no-ops due to the _initialised guard.
    """
    global _initialised
    if _initialised:
        return

    # --- Resolve log level ---------------------------------------------------
    level_name = os.environ.get("SNOMED_LOG_LEVEL", _DEFAULT_LOG_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)
    if level_name not in  _VALID_LOG_LEVELS:
        sys.stderr.write(
            "WARNING: SNOMED_LOG_LEVEL='{}' is not valid. "
            "Using INFO.\n".format(level_name)
        )
        level = logging.INFO

    # --- Resolve log directory -----------------------------------------------
    log_dir_str = os.environ.get("SNOMED_LOG_DIR", "")
    if log_dir_str:
        log_dir = Path(log_dir_str)
    else:
        log_dir = Path.cwd() / "log"
        sys.stderr.write(
            "WARNING: SNOMED_LOG_DIR not set. "
            "Falling back to {}\n".format(log_dir)
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
            when="midnight",
            interval=1,
            backupCount=_LOG_BACKUP_COUNT,
            encoding="utf-8",
            utc=False
        )
        # Rotated files named snomed.log.YYYY-MM-DD
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    except OSError as e:
        # Log directory not writable — fall back to stdout only.
        # Do NOT raise — a logging infrastructure failure must never
        # suppress the original operation.
        sys.stderr.write(
            "WARNING: Cannot write to log directory '{}': {}. "
            "Logging to stdout only.\n".format(log_dir, e)
        )

    _initialised = True


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given name.

    Call once at module level in every Python module that needs logging:

        logger = get_logger(__name__)

    Using __name__ gives the full dotted module path, for example
    src.common.config_loader. This appears in every log line and identifies
    where the message originated.

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

    Produces log lines that clearly identify where in the pipeline a
    message originated. Use this in pipeline scripts, not in utility
    modules.

    Args:
        phase:  Phase identifier, e.g. phase0, phase1
        step:   Step identifier, e.g. step0.3, step1.2
        script: Script name, e.g. load_concepts, validate_stage

    Returns:
        A standard logging.Logger instance.

    Example:
        logger = get_phase_logger("phase1", "step1.2", "load_concepts")
        logger.info("Starting load")
        # Produces:
        # 2026-03-30T14:23:01 | INFO     | phase1.step1.2.load_concepts | Starting load
    """
    _initialise_logging()
    logger_name = "{}.{}.{}".format(phase, step, script)
    return logging.getLogger(logger_name)
