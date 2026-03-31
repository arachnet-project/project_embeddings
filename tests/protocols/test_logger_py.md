# Test Protocol — test_logger_py.py
## Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-03-28
**Tests:** `src/common/logger.py`
**Script:** `tests/test_logger_py.py`
**Platforms:** Ubuntu, OCI Oracle Linux 9

---

## Prerequisites

### Environment variables in `.bashrc`

```bash
export SNOMED_LOG_DIR="/path/to/project_embeddings/log"
export SNOMED_LOG_LEVEL="DEBUG"
```

Apply: `source ~/.bashrc`

### Virtual environment active

```bash
source venv/bin/activate
```

### Files in place

```bash
ls src/common/logger.py
ls tests/test_logger_py.py
```

---

## Test passes

### Pass 1 — Full test with DEBUG level

```bash
python tests/test_logger_py.py
```

### Pass 2 — INFO level filtering

```bash
SNOMED_LOG_LEVEL=INFO python tests/test_logger_py.py
```

### Pass 3 — Unwritable directory (included in script as Test 7)

Test 7 inside the script handles this automatically. No separate
command needed.

---

## Expected output — Pass 1

```
--- test_logger_py.py ---
Platform    : Linux x.x.x x86_64
Python      : 3.12.x
Project root: /path/to/project_embeddings
SNOMED_LOG_DIR  : /path/to/log
SNOMED_LOG_LEVEL: DEBUG

Test 1: get_logger() returns a Logger instance
  PASS  get_logger() returns logging.Logger
  PASS  Logger name is correct

Test 2: get_phase_logger() returns correctly named logger
  PASS  get_phase_logger() returns logging.Logger
  PASS  Phase logger name is correct

Test 3: Root logger has handlers configured
  PASS  Root logger has at least one handler
  INFO  Handlers: ['StreamHandler', 'TimedRotatingFileHandler']
  PASS  StreamHandler present (stdout)

Test 4: Log level matches SNOMED_LOG_LEVEL environment variable
  PASS  Root logger level matches env (DEBUG)

Test 5: File handler present when SNOMED_LOG_DIR is set
  PASS  TimedRotatingFileHandler present
  PASS  Log file exists after writing
  PASS  Log file is non-empty
  INFO  Log file path: /path/to/log/snomed.log
  INFO  Log file size: <n> bytes

Test 6: Logging at each level produces no exceptions
  PASS  All log levels execute without exception

Test 7: Fallback to stdout when SNOMED_LOG_DIR is unwritable
  PASS  Warning emitted to stderr when log dir unwritable
  PASS  Only StreamHandler present in fallback mode

--- Results: 14 passed, 0 failed ---
PASS — all checks passed.
```

---

## Pass criteria

| # | Check |
|---|-------|
| 1 | `get_logger()` returns `logging.Logger` instance |
| 2 | Logger name matches argument passed |
| 3 | `get_phase_logger()` returns correctly named logger |
| 4 | Root logger has at least one handler |
| 5 | `StreamHandler` always present |
| 6 | `TimedRotatingFileHandler` present when SNOMED_LOG_DIR set |
| 7 | Log file created and non-empty after write |
| 8 | Log level matches SNOMED_LOG_LEVEL |
| 9 | All log levels execute without exception |
| 10 | Warning on stderr when log dir unwritable |
| 11 | Only StreamHandler in fallback mode |
| 12 | Exit code 0 |

---

## Results

| Field | Ubuntu | OCI |
|-------|--------|-----|
| Date tested | | |
| Python version | | |
| All criteria met | | |
| Notes | | |

---

## After passing

Change `SNOMED_LOG_LEVEL` back to `INFO` in `.bashrc`.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
