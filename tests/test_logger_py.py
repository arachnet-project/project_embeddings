#!/usr/bin/env python3
# test_logger_py.py
# Verification test for src/common/logger.py
# Run on each target platform: Ubuntu, OCI Oracle Linux 9.
#
# Located in: tests/
# Tests:      src/common/logger.py
#
# Does NOT set SNOMED_LOG_DIR or SNOMED_LOG_LEVEL.
# Relies entirely on environment — tests the real setup.
#
# Usage (run from project root, venv must be active):
#   python tests/test_logger_py.py
#
# See tests/protocols/test_logger_py.md for the full test protocol.
#
# Last modified: 2026-03-28

import logging
import os
import platform
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate project root and add src/ to path so logger.py can be imported
# regardless of which directory the script is called from.
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.common.logger import get_logger, get_phase_logger

# ---------------------------------------------------------------------------
# Simple assertion helper — no test framework dependency
# ---------------------------------------------------------------------------

_pass_count = 0
_fail_count = 0


def check(description: str, condition: bool) -> None:
    global _pass_count, _fail_count
    if condition:
        print(f"  PASS  {description}")
        _pass_count += 1
    else:
        print(f"  FAIL  {description}", file=sys.stderr)
        _fail_count += 1


# ---------------------------------------------------------------------------
# Report environment
# ---------------------------------------------------------------------------

print()
print("--- test_logger_py.py ---")
print(f"Platform    : {platform.system()} {platform.release()} {platform.machine()}")
print(f"Python      : {sys.version.split()[0]}")
print(f"Project root: {PROJECT_ROOT}")
print(f"SNOMED_LOG_DIR  : {os.environ.get('SNOMED_LOG_DIR', '<not set — using default>')}")
print(f"SNOMED_LOG_LEVEL: {os.environ.get('SNOMED_LOG_LEVEL', '<not set — using default INFO>')}")
print()

# ---------------------------------------------------------------------------
# Test 1 — get_logger() returns a Logger instance
# ---------------------------------------------------------------------------

print("Test 1: get_logger() returns a Logger instance")
logger = get_logger("test.step0.3")
check("get_logger() returns logging.Logger", isinstance(logger, logging.Logger))
check("Logger name is correct", logger.name == "test.step0.3")

# ---------------------------------------------------------------------------
# Test 2 — get_phase_logger() returns correctly named logger
# ---------------------------------------------------------------------------

print("\nTest 2: get_phase_logger() returns correctly named logger")
phase_logger = get_phase_logger("phase0", "step0.3", "test_logger_py")
check(
    "get_phase_logger() returns logging.Logger",
    isinstance(phase_logger, logging.Logger)
)
check(
    "Phase logger name is correct",
    phase_logger.name == "phase0.step0.3.test_logger_py"
)

# ---------------------------------------------------------------------------
# Test 3 — Logger has at least one handler configured
# ---------------------------------------------------------------------------

print("\nTest 3: Root logger has handlers configured")
root_logger = logging.getLogger()
check("Root logger has at least one handler", len(root_logger.handlers) > 0)

handler_types = [type(h).__name__ for h in root_logger.handlers]
print(f"  INFO  Handlers: {handler_types}")

has_stream = any("Stream" in t for t in handler_types)
check("StreamHandler present (stdout)", has_stream)

# ---------------------------------------------------------------------------
# Test 4 — Log level is set correctly from environment
# ---------------------------------------------------------------------------

print("\nTest 4: Log level matches SNOMED_LOG_LEVEL environment variable")
env_level = os.environ.get("SNOMED_LOG_LEVEL", "INFO").upper()
expected_level = getattr(logging, env_level, logging.INFO)
actual_level = root_logger.level
check(
    f"Root logger level matches env ({env_level})",
    actual_level == expected_level
)

# ---------------------------------------------------------------------------
# Test 5 — Log file handler present when SNOMED_LOG_DIR is set and writable
# ---------------------------------------------------------------------------

print("\nTest 5: File handler present when SNOMED_LOG_DIR is set")
log_dir = os.environ.get("SNOMED_LOG_DIR", "")
if log_dir:
    has_file_handler = any("Timed" in t or "File" in t for t in handler_types)
    check("TimedRotatingFileHandler present", has_file_handler)

    log_file = Path(log_dir) / "snomed.log"
    # Write a test log entry and verify the file exists
    logger.info("test_logger_py.py — INFO test entry")
    check("Log file exists after writing", log_file.exists())
    check("Log file is non-empty", log_file.stat().st_size > 0)

    print(f"  INFO  Log file path: {log_file}")
    print(f"  INFO  Log file size: {log_file.stat().st_size} bytes")
else:
    print("  SKIP  SNOMED_LOG_DIR not set — file handler test skipped")
    print("        Set SNOMED_LOG_DIR in .bashrc and re-run for full test")

# ---------------------------------------------------------------------------
# Test 6 — Logging at each level produces output without error
# ---------------------------------------------------------------------------

print("\nTest 6: Logging at each level produces no exceptions")
try:
    logger.debug("test_logger_py.py — DEBUG entry")
    logger.info("test_logger_py.py — INFO entry")
    logger.warning("test_logger_py.py — WARNING entry")
    logger.error("test_logger_py.py — ERROR entry")
    check("All log levels execute without exception", True)
except Exception as e:
    check(f"All log levels execute without exception — EXCEPTION: {e}", False)

# ---------------------------------------------------------------------------
# Test 7 — Fallback to stdout when log directory is unwritable
# ---------------------------------------------------------------------------

print("\nTest 7: Fallback to stdout when SNOMED_LOG_DIR is unwritable")
print("  INFO  This test resets logger state — run as final test")

# Reset the module's _initialised flag to test fresh initialisation
import src.common.logger as logger_module
logger_module._initialised = False
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)

# Point to an unwritable directory
os.environ["SNOMED_LOG_DIR"] = "/root/no_permission"

# Capture stderr to check for warning
import io
old_stderr = sys.stderr
sys.stderr = io.StringIO()

try:
    fallback_logger = get_logger("test.fallback")
    stderr_output = sys.stderr.getvalue()
finally:
    sys.stderr = old_stderr

warning_emitted = "WARNING" in stderr_output or "Cannot" in stderr_output
check("Warning emitted to stderr when log dir unwritable", warning_emitted)

fallback_root = logging.getLogger()
fallback_handlers = [type(h).__name__ for h in fallback_root.handlers]
has_only_stream = all("Stream" in t for t in fallback_handlers)
check("Only StreamHandler present in fallback mode", has_only_stream)

# Restore original log dir
if log_dir:
    os.environ["SNOMED_LOG_DIR"] = log_dir
else:
    del os.environ["SNOMED_LOG_DIR"]

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print()
print(f"--- Results: {_pass_count} passed, {_fail_count} failed ---")

if _fail_count > 0:
    print("FAIL — one or more checks failed. See output above.", file=sys.stderr)
    sys.exit(1)
else:
    print("PASS — all checks passed.")
    sys.exit(0)
