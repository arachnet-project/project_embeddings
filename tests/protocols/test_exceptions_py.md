# Test Protocol — test_exceptions_py.py
## Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-03-28
**Tests:** `src/common/exceptions.py`
**Script:** `tests/test_exceptions_py.py`
**Platforms:** Ubuntu, OCI Oracle Linux 9

---

## Prerequisites

No environment variables required. `exceptions.py` has no dependencies.

### Virtual environment active

```bash
source venv/bin/activate
```

### Files in place

```bash
ls src/common/exceptions.py
ls tests/test_exceptions_py.py
```

---

## Test pass

Single pass — no environment variation needed:

```bash
python tests/test_exceptions_py.py
```

---

## Expected output

```
--- test_exceptions_py.py ---
Platform    : Linux x.x.x x86_64
Python      : 3.12.x
Project root: /path/to/project_embeddings

Test 1: All exception classes importable
  PASS  SnomedBaseError importable
  PASS  SnomedConfigError importable
  PASS  SnomedDBConnectionError importable
  PASS  SnomedDDLError importable
  PASS  SnomedLoadError importable
  PASS  SnomedValidationError importable

Test 2: Inheritance hierarchy
  PASS  SnomedBaseError inherits from Exception
  PASS  SnomedConfigError inherits from SnomedBaseError
  PASS  SnomedDBConnectionError inherits from SnomedBaseError
  PASS  SnomedDDLError inherits from SnomedBaseError
  PASS  SnomedLoadError inherits from SnomedBaseError
  PASS  SnomedValidationError inherits from SnomedBaseError

Test 3: Exit codes
  PASS  SnomedConfigError.exit_code == 1
  PASS  SnomedDBConnectionError.exit_code == 2
  PASS  SnomedDDLError.exit_code == 3
  PASS  SnomedLoadError.exit_code == 4
  PASS  SnomedValidationError.exit_code == 5

Test 4: Raise and catch each exception
  PASS  SnomedConfigError caught as SnomedBaseError
  PASS  SnomedConfigError exit_code on instance == 1
  PASS  SnomedConfigError message stored correctly
  PASS  SnomedConfigError detail stored correctly
  ... (same for all five subclasses)

Test 5: __str__ output format
  PASS  str() contains exit code
  PASS  str() contains message
  PASS  str() contains detail
  INFO  str() output: [exit 1] Missing mandatory key | project.data_release

Test 6: Exception without detail argument
  PASS  Exception without detail raises cleanly
  PASS  detail is empty string
  PASS  str() works without detail

Test 7: Subclass caught by parent except clause
  PASS  SnomedValidationError caught by except SnomedBaseError
  PASS  exit_code accessible on caught instance

Test 8: Credential safety — manual verification
  INFO  Verify by inspection: no exception class stores or logs
        credential values. The detail parameter is free-form text.
        Convention: never pass password values as detail argument.
  INFO  This is a convention check — no automated assertion possible.

--- Results: 29 passed, 0 failed ---
PASS — all checks passed.
```

---

## Pass criteria

| # | Check |
|---|-------|
| 1 | All six classes importable |
| 2 | All subclasses inherit from SnomedBaseError |
| 3 | SnomedBaseError inherits from Exception |
| 4 | Exit codes: Config=1, DBConn=2, DDL=3, Load=4, Validation=5 |
| 5 | Each exception raiseable and catchable as SnomedBaseError |
| 6 | exit_code accessible on instance |
| 7 | message and detail stored correctly on instance |
| 8 | str() includes exit code, message, and detail |
| 9 | Exception without detail argument works correctly |
| 10 | Subclass caught by parent except clause |
| 11 | Exit code 0 |

---

## Results

| Field | Ubuntu | OCI |
|-------|--------|-----|
| Date tested | | |
| Python version | | |
| All criteria met | | |
| Notes | | |

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
