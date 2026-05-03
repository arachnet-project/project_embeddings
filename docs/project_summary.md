# Arachnet Clinical Embeddings — Project Summary
# docs/project_summary.md
# =========================================
# Version: 1.4
# Last updated: 2026-05-01
# Purpose: Full project context for session handover and crash recovery.
#          Covers project overview, conventions, Phase 0 progress,
#          and immediate next actions.
#          Updated 2026-05-01: 03_grants.sql reviewed and approved,
#          run_sql_setup.sh rewrite agreed, Step 0.5 completion
#          checklist finalised.


## 1. Project overview

Arachnet Clinical Embeddings is a SNOMED CT terminology embedding platform
built on Oracle 23ai (being upgraded to 26ai). It ingests SNOMED CT RF2
release files, loads them into Oracle, validates completeness, swaps stage
to production, and produces clinical embeddings for downstream use.

Owner: Jan Mura, Arachnet Project z.s.
Licence: BUSL 1.1 (to be added to repository).


### Platforms

Two active machines:

Ubuntu on MacBook Air (hostname: jan-MacBookAir) — primary development
and testing machine. MacBook Air hardware running Ubuntu Linux natively,
no macOS, no virtual machine. Python venv, mocked database tests,
Git origin. All development happens here first.

OCI Frankfurt — Oracle Cloud Infrastructure. Production target.
Oracle database currently at 23ai SE2, version 23.7.0.25.01.
Real database tests run here with SNOMED_TEST_REAL_DB=true.
26ai upgrade: confirmed available on OCI. Upgrade is a patch (release
update), not a full database upgrade. No application re-certification
required. All objects, grants, and profiles created under 23ai carry
over unchanged. Run setup scripts on 23ai first, then apply 26ai patch.

Mac Studio — Phase 3 ML computations only. Not a pipeline or development
machine. Not relevant until Phase 3.


### Infrastructure

Oracle Database on OCI: 23ai SE2, version 23.7.0.25.01.
Managed DB System on separate VM in private VCN.
No public IP on DB VM — access only from Linux VM via private connection string.
TNS alias: ARADB. TNS_ADMIN must be set in environment before any script runs.

Two application schemas: snomed (production) and snomed_stage (stage).
Tablespaces: TBS_SNOMED and TBS_SNOMED_STAGE.
Profile: NO_EXPIRY_PROFILE — no password expiry, 10 failed login attempts
allowed before 1-hour auto-lockout (defence in depth).

SYS and SYSTEM accounts: already assigned to NO_EXPIRY_PROFILE. Done.

Linux VM (arachnetwebserver): Oracle Linux 9. Public IP 130.61.83.216.
sudo dnf update run but aborted at confirmation prompt. Needs re-run with y.
Reboot needed after dnf update completes.

OCI CLI version: 3.79.0 on Mac.

Project root paths:
    OCI:    /home/opc/project_embeddings
    Ubuntu: /home/jan/project_embeddings


## 2. Technology stack and conventions

### Python
Python 3.10.12 currently installed on Ubuntu. Upgrade to 3.12.x pending.
Venv must be rebuilt after upgrade.
python-oracledb in thin mode only. No Oracle client installation needed.
OmegaConf for configuration management. Pin exact version in requirements.txt.
PyYAML for YAML parsing. Import as: import yaml. Catch yaml.YAMLError.
Standard library only beyond the above. No frameworks.

### Oracle tooling
SQLcl 24.4.1 or later available on OCI Linux VM.
run_sql_setup.sh — wrapper script (scripts/run_sql_setup.sh) that sources
logger.sh and functions.sh, validates env vars via require_var, injects
credentials as DEFINE variables into SQL*Plus, and runs all four DDL
setup scripts in order.
Status: needs to be rewritten from run_setup.sh. See Section 5.

### Bash
Bash 4.0 or later required. Ubuntu and OCI both ship Bash 5.x.
set -euo pipefail and export LC_ALL=C.UTF-8 in all executable scripts.
Sourced library files do not set shell options or locale.
Set SNOMED_LOG_DIR before sourcing logger.sh in any executable script.

### Coding conventions
Documented in docs/conventions.md, version 1.5. Key points:
- 4-space indentation in Python and SQL.
- .format() for all Python string formatting. No f-strings.
- Block markers around every Python function definition:
    # --- function_name ---
    # --- end function_name ---
- Type annotations from _validate_mandatory_keys onward. No retrofitting.
- NumPy-style docstrings in all Python functions.
- Plain Python testing with _report and _summarise pattern. No pytest.
- SQL keywords in uppercase. Schema, table, column names in lowercase.
- Bash logging via scripts/common/logger.sh. No bare echo for log messages.
- Pipeline scripts may use config_loader --export for configuration.
- Infrastructure scripts must be self-contained, no venv dependency.
- Commit convention: feat: fix: docs: test: chore: refactor:
- Git: Ubuntu pushes. OCI pulls only. Never edit code on OCI.

### OmegaConf behaviour — important notes
OmegaConf builds a tree of DictConfig and ListConfig nodes, not plain dicts.
Interpolation (${path.to.key}) is resolved lazily at access time.
Live node references must not be assigned to new positions in the same tree.
Use OmegaConf.to_container(resolve=False) to get a plain dict before
wrapping in a new OmegaConf.create() call.
Pin OmegaConf to exact version in requirements.txt.
Import yaml directly (import yaml) not submodules.
Catch yaml.YAMLError not yaml.parser.ParserError.


## 3. Repository structure

project_embeddings/
    config/
        project.yaml          — root config, includes database.yaml and ingestion.yaml
        database.yaml         — DB connection, schemas, table registry (version 1.3)
        ingestion.yaml        — Phase 1 RF2 ingestion pipeline config

    src/
        common/
            exceptions.py     — project exception hierarchy (complete)
            logger.py         — Python logging utility (complete)
            config_loader.py  — YAML config loader (Step 0.4, complete)
            db_connection.py  — Oracle connection helper (Step 0.6, pending)

    scripts/
        common/
            logger.sh         — Bash logging library (version 1.1, complete)
            functions.sh      — shared Bash functions (version 1.1, complete)
        run_tests.sh          — run all tests (version 1.1, complete)
        run_sql_setup.sh      — DDL setup runner (to be written, replaces run_setup.sh)
        run_setup.sh          — OLD name, to be deleted after run_sql_setup.sh written
        run.sh                — main pipeline orchestrator (Step 0.7, pending)

    tests/
        test_exceptions_py.py          — 45 tests, passing
        test_logger_py.py              — 13 tests, passing
        test_logger_sh.sh              — passing
        test_functions_sh.sh           — 10 tests, passing (version 1.2)
        test_config_loader_py.py       — orchestrator, 32 tests, passing
        test_config_loader_r1_py.py    — Round 1
        test_config_loader_r2_py.py    — Round 2
        test_config_loader_r3_py.py    — Round 3
        test_config_loader_r4_py.py    — Round 4
        test_db_connection_py.py       — empty placeholder, Step 0.6 pending
        protocols/
            test_logger_sh.md
            test_logger_py.md
            test_exceptions_py.md
            test_config_loader_py.md
            test_db_connection_py.md   — to be written in Step 0.6
        results/                       — not committed to Git

    sql/
        ddl/
            setup/
                00_create_profile.sql       — version 1.2, reviewed, approved
                01_create_tablespaces.sql   — version 1.2, reviewed, approved
                02_create_schemas.sql       — version 1.2, reviewed, approved
                03_grants.sql               — version 1.2, reviewed, approved
            tables/                         — one file per SNOMED CT table, Phase 1

    docs/
        conventions.md              — version 1.5
        directory_structure.md      — version 1.4
        error_codes.md
        git_workflow.md
        phase0_foundation.md        — version 1.5
        project_summary.md          — this file, version 1.4
        todo.md                     — needs reconstruction after crash
        todo_step_0_5.md            — Step 0.5 SQL setup todo
        todo_step_0_6.md            — Step 0.6 db_connection todo, to be written
        dev_workflow.md             — daily workflow and testing strategy
        claude_chat_howto.md        — claude_chat.py usage guide
        uzis_correspondence.md      — UZIS email analysis and meeting agenda
        uzis_meeting_prep.md        — meeting script for UZIS online meeting
        runbooks/
            run_sql_setup.md        — verify reflects run_sql_setup.sh

    log/                            — not committed to Git
    venv/                           — not committed to Git
    claude_chat.py                  — Claude API terminal interface (project root)
    requirements.txt
    syn.sh                          — rsync sync script
    .gitignore
    LICENSE                         — BUSL 1.1, to be added


## 4. Environment variables

All Oracle credentials managed via environment variables in ~/.bashrc.
Never commit passwords to version control.

Required variables on OCI and Ubuntu:

    # Oracle admin credentials — SYSDBA access for setup scripts only
    export ORACLE_SYS_USER="SYS"
    export ORACLE_SYS_PASSWORD=""               # fill in on each machine

    # Application schema credentials
    export ORACLE_SNOMED_USER="SNOMED"
    export ORACLE_SNOMED_PASSWORD=""            # fill in on each machine

    export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
    export ORACLE_SNOMED_STAGE_PASSWORD=""      # fill in on each machine

    # TNS alias — used by run_sql_setup.sh and db_connection.py
    export ORACLE_TNS_ALIAS="ARADB"

    # Python db_connection.py reads these variable names from config:
    export SNOMED_DB_PASSWORD=""                # same value as ORACLE_SNOMED_PASSWORD
    export SNOMED_STAGE_DB_PASSWORD=""          # same value as ORACLE_SNOMED_STAGE_PASSWORD
    export SNOMED_ADMIN_DB_PASSWORD=""          # same value as ORACLE_SYS_PASSWORD

    # OCI compartment and resource OCIDs
    export OCI_NETWORK_COMPARTMENT_OCID=""
    export OCI_DB_COMPARTMENT_OCID=""
    export OCI_LINUX_COMPARTMENT_OCID=""
    export OCI_VCN_OCID=""
    export OCI_PUBLIC_SUBNET_OCID=""
    export OCI_PRIVATE_SUBNET_OCID=""
    export OCI_LINUX_VM_OCID=""
    export OCI_DB_SYSTEM_OCID=""
    export OCI_BASTION_OCID=""

    # Logging
    export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"   # Ubuntu
    export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"   # OCI

Claude API alias (Ubuntu only):
    alias claude="cd /home/jan/project_embeddings && \
        source venv/bin/activate && python claude_chat.py"


## 5. Phase 0 status

Step 0.1 — YAML configuration files — Complete.
Step 0.2 — Error handling — Complete.
Step 0.3 — Logging utility — Complete.
Step 0.4 — Configuration loader — Complete. 32 tests passing on Ubuntu.

Step 0.5 — SQL database setup — In progress.

    Completed:
    - All four SQL scripts reviewed, corrected, approved at version 1.2.
    - scripts/common/logger.sh version 1.1 complete.
    - scripts/common/functions.sh version 1.1 complete.
    - scripts/run_tests.sh version 1.1 complete.
    - tests/test_functions_sh.sh version 1.2, 10 tests passing.
    - Full test suite 6 scripts all passing on Ubuntu.

    Remaining to close Step 0.5:

    1. Write scripts/run_sql_setup.sh.
       Replaces scripts/run_setup.sh.
       Must source logger.sh and functions.sh.
       Must use require_var for all prerequisite checks.
       Must use log_info and log_error, no bare echo.
       Must use ORACLE_TNS_ALIAS not OCI_DB_CONNECTION_STRING.
       Must support RUN_00=true flag to optionally include 00_create_profile.sql.
       Must delete scripts/run_setup.sh after replacement is confirmed.

    2. Fix comment in 00_create_profile.sql header.
       Remove incorrect statement about SYS/SYSTEM assignment being done
       at initial setup. Replace with: SYS and SYSTEM already assigned to
       NO_EXPIRY_PROFILE — no action needed.

    3. Run SQL setup scripts on OCI.
       SSH to arachnetwebserver (130.61.83.216).
       Confirm TNS_ADMIN set and tnsnames.ora present.
       Confirm passwords set in .bashrc.
       Run: bash scripts/run_sql_setup.sh
       Verify after run:
           SELECT username, default_tablespace, profile
           FROM dba_users
           WHERE username IN ('SNOMED', 'SNOMED_STAGE');
           SELECT * FROM dba_sys_privs
           WHERE grantee IN ('SNOMED', 'SNOMED_STAGE')
           ORDER BY grantee, privilege;

    4. Assign SYS and SYSTEM to NO_EXPIRY_PROFILE — ALREADY DONE.
       No action needed.

    5. Run sudo dnf update on OCI Linux VM.
       SSH to 130.61.83.216.
       Run: sudo dnf update
       Type y when prompted.
       Run: sudo reboot
       Wait 3-5 minutes, reconnect.

    6. Upgrade Python to 3.12.x on Ubuntu.
       Deactivate venv first: deactivate
       Run:
           sudo apt update
           sudo apt install -y software-properties-common
           sudo add-apt-repository -y ppa:deadsnakes/ppa
           sudo apt update
           sudo apt install -y python3.12 python3.12-venv python3.12-dev
           python3.12 --version
           cd ~/project_embeddings
           rm -rf venv
           python3.12 -m venv venv
           source venv/bin/activate
           python --version
           pip install --upgrade pip
           pip install -r requirements.txt
           pip install anthropic
       Rerun: bash scripts/run_tests.sh
       Confirm all 6 test scripts pass on Python 3.12.
       Update docs/conventions.md to reference Python 3.12.

    7. Apply 26ai patch via OCI console.
       Run precheck first in OCI console.
       Take manual backup before patching.
       Disable automatic backups during patch window.
       After patch: verify TNS_ADMIN and tnsnames.ora unchanged.
       Confirm connectivity: run test query via SQLcl.
       No application re-certification needed.
       Confirm oracledb thin mode connection parameters unchanged.

    8. Run full test suite on OCI after Oracle upgrade.
       Pull latest from Git on OCI.
       Run: bash scripts/run_tests.sh
       Confirm all passing with SNOMED_TEST_REAL_DB=false.

    9. Commit and close Step 0.5.
       Commit message covers: SQL scripts v1.2, run_sql_setup.sh,
       Bash infrastructure corrections, test_functions_sh.sh,
       Python 3.12 upgrade, Oracle 26ai upgrade confirmed.

Step 0.6 — Database connection helper — Pending.
    src/common/db_connection.py not yet written.
    tests/test_db_connection_py.py is an empty placeholder.
    Design fully agreed — see Section 6.
    Blocked on: Step 0.5 completion.

Step 0.7 — Bash pipeline orchestrator — Pending.
    scripts/run.sh not yet written.
    Depends on all previous steps.


## 6. db_connection.py design (Step 0.6)

File location: src/common/db_connection.py
All Oracle communication in the project goes through this module exclusively.
Uses oracledb thin mode only. No Oracle client installation needed.
No code outside this module imports oracledb directly.

Module-level constants:
    _VALID_SCHEMAS = ("production", "stage", "admin")
    _RETRY_WAIT_SECONDS = 2
    _DDL_LOG_MAX_LENGTH = 200

Imports needed:
    import time
    import oracledb
    from contextlib import contextmanager
    from src.common.exceptions import (
        SnomedConfigError, SnomedDBConnectionError,
        SnomedDDLError, SnomedLoadError)
    from src.common.logger import get_logger

Functions:

_get_credentials(cfg, schema) -> tuple(user, password, tns_alias)
    Internal. Extracts user, resolves password from env var named in config.
    Valid schemas: production, stage, admin.
    Raises SnomedConfigError for unknown schema name.
    Raises SnomedDBConnectionError if password env var not set or empty.
    Never logs the password value.

get_connection(cfg, schema) -> oracledb.Connection
    Public. Returns direct oracledb connection in thin mode.
    autocommit=False on all connections.
    Retries once after _RETRY_WAIT_SECONDS on failure.
    Raises SnomedDBConnectionError after two failures.

open_connection(cfg, schema) -> context manager yielding oracledb.Connection
    Public. Context manager wrapping get_connection.
    Use with: with open_connection(cfg, "production") as conn:
    Connection closed automatically on exit, even on exception.
    No commit on exception exit — caller handles commit/rollback.
    Implemented with @contextmanager decorator.

execute_ddl(conn, sql) -> None
    Public. Executes single DDL statement.
    Logs full SQL at DEBUG level (truncated to _DDL_LOG_MAX_LENGTH).
    Raises SnomedDDLError on failure with Oracle error code.
    DDL in Oracle implicitly commits — no explicit commit needed.

execute_batch(conn, sql, data, batch_size) -> tuple(rows_loaded, batches_processed)
    Public. Bulk INSERT via executemany in batches of batch_size rows.
    Does NOT commit — caller commits after all batches complete.
    Rolls back and raises SnomedLoadError on any batch failure.
    Returns (rows_loaded, batches_processed) for manifest logging.

test_connection(cfg, schema="production") -> True or raises SnomedDBConnectionError
    Public. Executes SELECT 1 FROM DUAL to verify connectivity.
    Returns True on success.
    Raises SnomedDBConnectionError on failure — never returns False.
    Used by run.sh health checks.

get_pool(cfg, schema) -> raises NotImplementedError
    Public stub. Connection pooling is Phase 3/4 work.
    Raises NotImplementedError with clear message explaining deferral.

Testing strategy:
    Ubuntu: mock oracledb.connect with unittest.mock. Tests logic only.
    OCI: real Oracle connection via SNOMED_TEST_REAL_DB=true.


## 7. UZIS correspondence

Czech SNOMED CT national extension contact: MUDr. Irena Molinari, UZIS.
Department of Standardisation contact: Mr. Zvolský.
Online meeting arranged — preparation at docs/uzis_meeting_prep.md.
Full analysis at docs/uzis_correspondence.md.

Key confirmed points from UZIS:
    RF2 package follows SNOMED International standards.
    Language refset SCTID included in distribution package.
    Czech descriptions load into sct_description with languageCode=cs.
    Arachnet to be added to release notification list.

Open questions for meeting:
    ModuleId stability — UZIS said it may differ per release.
    Likely confusion with effectiveTime. Confirm stable fixed SCTID.
    Complete refset inventory beyond language acceptability refset.
    Release schedule relative to SNOMED International.
    Package access for development.
    Namespace process for future Arachnet extension authoring.


## 8. claude_chat.py

Location: ~/project_embeddings/claude_chat.py (project root)
Purpose: Terminal interface to Claude API. Designed for Orca screen reader.
Session JSON files: ~/.claude_sessions/NAME.json
Transcripts: ~/project_embeddings/log/transcript_*.txt

Current version features:
    Named sessions: --session NAME
    Model selection: --model sonnet (default) or --model opus
    Commands: /quit /clear /json /save [--last N] /history /sessions
              /file <path> /extract <path>
    /json  — saves session JSON only (checkpoint, use frequently)
    /save  — saves transcript only
    /quit  — saves both JSON and transcript, then exits
    /extract writes relative to PROJECT_ROOT always
    Rate limit: auto-retry 3 times with 60-second countdown
    Warning if --file used with existing session history
    MAX_TOKENS: 8192

Key workflow rules:
    Always run from project root: cd ~/project_embeddings
    Use --session NAME for all development work.
    Do NOT use --file when resuming existing session.
    Use --file only for fresh sessions on new topics.
    Type /json after every significant response — crash protection.
    Start new sessions for new topics to keep token costs low.

Alias in ~/.bashrc:
    alias claude="cd /home/jan/project_embeddings && \
        source venv/bin/activate && python claude_chat.py"
    Usage: claude --session arachnet_step05


## 9. What to do at the start of the next session

The next session should begin by producing scripts/run_sql_setup.sh.
Send this project_summary.md to Claude at the start of the session
and say: "Please read the project summary and produce
scripts/run_sql_setup.sh per the design in Section 5 Step 0.5 item 1."

Then work through the Step 0.5 remaining items in order as listed
in Section 5.


## 10. Open questions and pending decisions

- Confirm oracledb thin mode connection parameters unchanged after
  26ai patch is applied. Expected: no change, but verify.

- docs/todo.md is empty after crash. Reconstruct after Step 0.5 closes.

- docs/todo_step_0_6.md needs to be written before Step 0.6 begins.

- LICENSE file (BUSL 1.1) not yet added to repository.

- docs/runbooks/run_sql_setup.md — verify it reflects run_sql_setup.sh
  as the primary invocation method.

- docs/conventions.md — update Python version reference to 3.12
  after upgrade is confirmed.

- UZIS meeting date not yet confirmed. Check email and schedule.
