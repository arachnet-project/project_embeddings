#!/usr/bin/env python3
# test_exceptions_py.py
# Verification test for src/common/exceptions.py
# Run on each target platform: Ubuntu, OCI Oracle Linux 9.
#
# Located in: tests/
# Tests:      src/common/exceptions.py
#
# No environment variables required — exceptions.py has no dependencies.
#
# Usage (run from project root, venv must be active):
#   python tests/test_exceptions_py.py
#
# See tests/protocols/test_exceptions_py.md for the full test protocol.
#
# Last modified: 2026-03-28

import platform
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate project root and add to path
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.common.exceptions import (
    SnomedBaseError,
    SnomedConfigError,
    SnomedDBConnectionError,
    SnomedDDLError,
    SnomedLoadError,
    SnomedValidationError,
)

# ---------------------------------------------------------------------------
# Simple assertion helper
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
print("--- test_exceptions_py.py ---")
print(f"Platform    : {platform.system()} {platform.release()} {platform.machine()}")
print(f"Python      : {sys.version.split()[0]}")
print(f"Project root: {PROJECT_ROOT}")
print()

# ---------------------------------------------------------------------------
# Test 1 — All exception classes exist and are importable
# ---------------------------------------------------------------------------

print("Test 1: All exception classes importable")
check("SnomedBaseError importable", True)           # import would have failed above
check("SnomedConfigError importable", True)
check("SnomedDBConnectionError importable", True)
check("SnomedDDLError importable", True)
check("SnomedLoadError importable", True)
check("SnomedValidationError importable", True)

# ---------------------------------------------------------------------------
# Test 2 — Inheritance hierarchy is correct
# ---------------------------------------------------------------------------

print("\nTest 2: Inheritance hierarchy")
check("SnomedBaseError inherits from Exception",
      issubclass(SnomedBaseError, Exception))
check("SnomedConfigError inherits from SnomedBaseError",
      issubclass(SnomedConfigError, SnomedBaseError))
check("SnomedDBConnectionError inherits from SnomedBaseError",
      issubclass(SnomedDBConnectionError, SnomedBaseError))
check("SnomedDDLError inherits from SnomedBaseError",
      issubclass(SnomedDDLError, SnomedBaseError))
check("SnomedLoadError inherits from SnomedBaseError",
      issubclass(SnomedLoadError, SnomedBaseError))
check("SnomedValidationError inherits from SnomedBaseError",
      issubclass(SnomedValidationError, SnomedBaseError))

# ---------------------------------------------------------------------------
# Test 3 — Exit codes are correct
# ---------------------------------------------------------------------------

print("\nTest 3: Exit codes")
check("SnomedConfigError.exit_code == 1",
      SnomedConfigError.exit_code == 1)
check("SnomedDBConnectionError.exit_code == 2",
      SnomedDBConnectionError.exit_code == 2)
check("SnomedDDLError.exit_code == 3",
      SnomedDDLError.exit_code == 3)
check("SnomedLoadError.exit_code == 4",
      SnomedLoadError.exit_code == 4)
check("SnomedValidationError.exit_code == 5",
      SnomedValidationError.exit_code == 5)

# ---------------------------------------------------------------------------
# Test 4 — Exceptions can be raised and caught correctly
# ---------------------------------------------------------------------------

print("\nTest 4: Raise and catch each exception")

for cls, code in [
    (SnomedConfigError, 1),
    (SnomedDBConnectionError, 2),
    (SnomedDDLError, 3),
    (SnomedLoadError, 4),
    (SnomedValidationError, 5),
]:
    try:
        raise cls("test message", f"detail for exit code {code}")
    except SnomedBaseError as e:
        check(
            f"{cls.__name__} caught as SnomedBaseError",
            isinstance(e, SnomedBaseError)
        )
        check(
            f"{cls.__name__} exit_code on instance == {code}",
            e.exit_code == code
        )
        check(
            f"{cls.__name__} message stored correctly",
            e.message == "test message"
        )
        check(
            f"{cls.__name__} detail stored correctly",
            f"detail for exit code {code}" in e.detail
        )
    except Exception as e:
        check(f"{cls.__name__} raised unexpectedly as {type(e).__name__}", False)

# ---------------------------------------------------------------------------
# Test 5 — str() output includes exit code and message
# ---------------------------------------------------------------------------

print("\nTest 5: __str__ output format")
err = SnomedConfigError("Missing mandatory key",
                        "file=project.yaml key=project.data_release")
str_output = str(err)
check("str() contains exit code", "[exit 1]" in str_output)
check("str() contains message", "Missing mandatory key" in str_output)
check("str() contains detail", "project.data_release" in str_output)
print(f"  INFO  str() output: {str_output}")

# ---------------------------------------------------------------------------
# Test 6 — Exception without detail works correctly
# ---------------------------------------------------------------------------

print("\nTest 6: Exception without detail argument")
try:
    raise SnomedLoadError("Batch insert failed")
except SnomedLoadError as e:
    check("Exception without detail raises cleanly", True)
    check("detail is empty string", e.detail == "")
    check("str() works without detail", "Batch insert failed" in str(e))

# ---------------------------------------------------------------------------
# Test 7 — Subclass caught by parent in except clause
# ---------------------------------------------------------------------------

print("\nTest 7: Subclass caught by parent except clause")
try:
    raise SnomedValidationError("Row count mismatch",
                                "table=sct_concept expected=370000 got=0")
except SnomedBaseError as e:
    check("SnomedValidationError caught by except SnomedBaseError", True)
    check("exit_code accessible on caught instance", e.exit_code == 5)
except Exception:
    check("SnomedValidationError caught by except SnomedBaseError", False)

# ---------------------------------------------------------------------------
# Test 8 — Confirm credential safety convention (manual verification note)
# ---------------------------------------------------------------------------

print("\nTest 8: Credential safety — manual verification")
print("  INFO  Verify by inspection: no exception class stores or logs")
print("        credential values. The detail parameter is free-form text.")
print("        Convention: never pass password values as detail argument.")
print("  INFO  This is a convention check — no automated assertion possible.")

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
