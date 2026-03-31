# Test Protocol — test_logger_sh.sh
## Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-03-28
**Tests:** `scripts/common/logger.sh`
**Script:** `tests/test_logger_sh.sh`
**Platforms:** Ubuntu, OCI Oracle Linux 9

---

## Prerequisites

### Environment variables in `.bashrc`

**Ubuntu:**
```bash
export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
export SNOMED_LOG_LEVEL="DEBUG"
```

**OCI:**
```bash
export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
export SNOMED_LOG_LEVEL="DEBUG"
```

Apply: `source ~/.bashrc`

### Files and permissions

```bash
ls scripts/common/logger.sh
ls tests/test_logger_sh.sh
chmod +x tests/test_logger_sh.sh
```

---

## Test passes

### Pass 1 — Full DEBUG output

```bash
bash tests/test_logger_sh.sh
```

### Pass 2 — INFO level filtering

```bash
SNOMED_LOG_LEVEL=INFO bash tests/test_logger_sh.sh
```

DEBUG line must NOT appear. All other lines must appear.

### Pass 3 — Unwritable directory fallback

```bash
SNOMED_LOG_DIR="/root/no_permission" bash tests/test_logger_sh.sh
```

Expected: WARNING on stderr, all four log lines on stdout, exit code 0.

---

## Expected output — Pass 1

```
--- test_logger_sh.sh ---
Platform    : Linux x.x.x x86_64
Bash version: 5.x.x(1)-release
Project root: /path/to/project_embeddings
SNOMED_LOG_DIR  : /path/to/log
SNOMED_LOG_LEVEL: DEBUG
Log file    : /path/to/log/snomed.log
LC_ALL      : C.UTF-8

<timestamp> | DEBUG    | test.step0.3                            | DEBUG message — should NOT appear at INFO level
<timestamp> | INFO     | test.step0.3                            | INFO message — pipeline starting
<timestamp> | WARNING  | test.step0.3                            | WARNING message — skip_tables is non-empty
<timestamp> | ERROR    | test.step0.3                            | ERROR message — simulated load failure

--- Verification ---
Log file created : YES
...
--- test_logger_sh.sh complete — exit 0 ---
```

stderr additionally shows:
```
ERROR: ERROR message — simulated load failure
```

---

## Pass criteria

| # | Check |
|---|-------|
| 1 | All four log lines appear on stdout |
| 2 | DEBUG appears (SNOMED_LOG_LEVEL=DEBUG) |
| 3 | Format: `timestamp \| level \| name \| message` |
| 4 | Log file created in SNOMED_LOG_DIR |
| 5 | Log file contains same four lines as stdout |
| 6 | ERROR also on stderr |
| 7 | LC_ALL is C.UTF-8 |
| 8 | Bash version 4.0 or later |
| 9 | Exit code 0 |
| 10 | Pass 2: DEBUG absent at INFO level |
| 11 | Pass 3: WARNING on stderr, stdout only, exit 0 |

---

## Results

| Field | Ubuntu | OCI |
|-------|--------|-----|
| Date tested | | |
| Bash version | | |
| All criteria met | | |
| Notes | | |

---

## After passing

Change `SNOMED_LOG_LEVEL` back to `INFO` in `.bashrc` on both machines.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
