# Logger Test Protocol — Step 0.3
## Arachnet Clinical Embeddings

**Document version:** 1.0  
**Date:** 2026-03-27  
**Applies to:** `src/common/logger.py`, `scripts/common/logger.sh`  
**Test script:** `scripts/common/test_logger.sh`

---

## Purpose

Verify that the logging utility works correctly on all three platforms before
any other Phase 0 code is written. The logger is a dependency of every
subsequent module — a defect here propagates everywhere.

Platforms to test:

- macOS (MacBook Pro M1, primary dev machine)
- OCI Oracle Linux 9 (production)
- Ubuntu (MacBook Air Intel, secondary dev machine)

---

## Prerequisites

### 1. Environment variables set in `.bashrc`

Add the following to `~/.bashrc` on each machine before running the test.
Adjust the path to match the machine's project root.

**macOS:**
```bash
export SNOMED_LOG_DIR="/Users/jan/arachnet/snomed/project_embeddings/log"
export SNOMED_LOG_LEVEL="DEBUG"
```

**OCI:**
```bash
export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
export SNOMED_LOG_LEVEL="DEBUG"
```

**Ubuntu:**
```bash
export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
export SNOMED_LOG_LEVEL="DEBUG"
```

Set `SNOMED_LOG_LEVEL=DEBUG` for the test so all four log levels are
exercised. After the test passes, change to `INFO` for normal use.

After editing `.bashrc`, apply the changes to the current session:
```bash
source ~/.bashrc
```

Verify the variables are set:
```bash
echo $SNOMED_LOG_DIR
echo $SNOMED_LOG_LEVEL
```

### 2. Files in place

Confirm both files exist at the correct paths:
```bash
ls scripts/common/logger.sh
ls scripts/common/test_logger.sh
```

### 3. Execute permission set

```bash
chmod +x scripts/common/test_logger.sh
```

---

## Test procedure

Run from the project root directory on each machine:

```bash
cd /path/to/project_embeddings
bash scripts/common/test_logger.sh
```

---

## Expected output

### stdout

The output should look like this (timestamps will differ):

```
--- Logger test ---
Platform    : Darwin 24.x.x arm64          ← or Linux on OCI/Ubuntu
Bash version: 5.x.x(1)-release
SNOMED_LOG_DIR  : /path/to/log
SNOMED_LOG_LEVEL: DEBUG
Log file    : /path/to/log/snomed.log
LC_ALL      : C.UTF-8

2026-03-27T14:23:01 | DEBUG    | test.step0.3                            | DEBUG message — should NOT appear at INFO level
2026-03-27T14:23:01 | INFO     | test.step0.3                            | INFO message — pipeline starting
2026-03-27T14:23:01 | WARNING  | test.step0.3                            | WARNING message — skip_tables is non-empty
2026-03-27T14:23:01 | ERROR    | test.step0.3                            | ERROR message — simulated load failure

--- Verification ---
Log file created : YES
Log file path    : /path/to/log/snomed.log
Log file size    : <non-zero> bytes
Lines in log file: <non-zero>

Last 5 lines of log file:
<same four log lines as stdout>

--- Test complete ---
Exit code will be 0 if no errors were encountered above.
```

### stderr

The ERROR line produces an additional stderr output:
```
ERROR: ERROR message — simulated load failure
```

This is correct behaviour — errors go to both the log and stderr.

---

## Pass criteria

All of the following must be true on each platform:

| # | Check | How to verify |
|---|-------|---------------|
| 1 | All four log level lines appear on stdout | Visual inspection |
| 2 | DEBUG line appears (because SNOMED_LOG_LEVEL=DEBUG) | Visual inspection |
| 3 | Log format matches: `timestamp \| level \| name \| message` | Visual inspection |
| 4 | Log file created in `SNOMED_LOG_DIR` | Verification section of output |
| 5 | Log file contains the same four lines as stdout | `tail -5` output in verification |
| 6 | ERROR line also appears on stderr | Redirect stdout and check: `bash test_logger.sh > /dev/null` — ERROR line should still appear |
| 7 | `LC_ALL` is `C.UTF-8` | Reported in environment section |
| 8 | Bash version is 4.0 or later | Reported in environment section |
| 9 | Script exits with code 0 | `echo $?` immediately after running |

### Additional check — INFO level filtering

Re-run with log level overridden to INFO:

```bash
SNOMED_LOG_LEVEL=INFO bash scripts/common/test_logger.sh
```

The DEBUG line must NOT appear in stdout or the log file. All other
lines must appear. This confirms level filtering works correctly.

### Additional check — missing log directory

Temporarily set `SNOMED_LOG_DIR` to an unwritable path:

```bash
SNOMED_LOG_DIR="/root/no_permission" bash scripts/common/test_logger.sh
```

Expected: a WARNING on stderr about the log directory, followed by all
four log lines on stdout only. The script must not abort — it must
complete with exit code 0. This confirms the fallback behaviour works.

---

## Recording results

For each platform record the following after a successful test run:

| Field | Value |
|-------|-------|
| Platform | macOS / OCI / Ubuntu |
| Date tested | YYYY-MM-DD |
| Bash version | from script output |
| `SNOMED_LOG_DIR` | path used |
| All pass criteria met | YES / NO |
| Notes | any observations |

---

## Failure handling

If any pass criterion fails:

1. Note which criterion failed and on which platform.
2. Check the stderr output for warning or error messages.
3. Do not proceed to Step 0.4 until the logger passes on all platforms.
4. Fix the defect in `logger.sh`, re-run the full test procedure.

---

## After passing on all platforms

1. Change `SNOMED_LOG_LEVEL` from `DEBUG` back to `INFO` in `.bashrc`
   on all machines.
2. Run `source ~/.bashrc` on each machine.
3. Mark Step 0.3 as Complete in `docs/phase0_foundation.md`.
4. Commit all files:
   ```bash
   git add scripts/common/logger.sh
   git add scripts/common/test_logger.sh
   git add docs/test_logger_protocol.md
   git commit -m "feat: Step 0.3 logger.sh complete and tested"
   git push
   ```
5. Pull on all other machines:
   ```bash
   git pull
   ```

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
