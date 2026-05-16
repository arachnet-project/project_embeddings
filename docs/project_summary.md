# Arachnet Clinical Terminology Embeddings — Project Summary
# docs/project_summary.md
# =========================================
# Version: 1.7
# Last updated: 2026-05-13
# Purpose: Full project context for session handover and crash recovery.
#          Covers project overview, conventions, all Phase 0 steps,
#          infrastructure, tooling, and immediate next actions.
#          Complete history from Step 0.1 through session 2026-05-13.


## 1. Project overview

Arachnet Clinical Terminology Embeddings is a SNOMED CT terminology
embedding platform built on Oracle 23ai (26ai patch pending).
It ingests SNOMED CT RF2 release files, loads them into Oracle,
validates completeness, swaps stage to production, and produces
clinical embeddings for downstream use.

Full name: Arachnet Clinical Terminology Embeddings
Short name: Arachnet
Owner: Jan Mura, Arachnet Project z.s.
Licence: BUSL 1.1 (to be added to repository).


### Platforms

Ubuntu on MacBook Air — primary development machine.
CAUTION: power cable unstable, replacement ordered from Apple dealer.
Do not use for long sessions until cable replaced.

OCI Frankfurt — Oracle Cloud Infrastructure. Production target.
Oracle database: 23ai SE2, version 23.7.0.25.01.
Real database tests run here with SNOMED_TEST_REAL_DB=true.

26ai patch: attempted 2026-05-09. Precheck passed, APPLY failed.
DB remains on 23.7.0.25.01 and is fully available. Root cause unknown.
Oracle support (Slavomír Seno) informed by email 2026-05-10.
See docs/runbooks/patch_26ai.md.
All application code works on 23ai — patch is not a blocker.

MacBook Pro M1 — macOS. Backup/secondary machine.
Currently used as primary when MacBook Air cable is unstable.
Not relevant for ML until Phase 3.


### Infrastructure

Oracle Database on OCI: 23ai SE2, version 23.7.0.25.01.
DB name: ArachDB. DB unique name: ArachDB_b7d_fra.
Managed DB System on separate VM in private VCN.
No public IP on DB VM — access only from Linux VM via private subnet.
TNS alias: ARADB. TNS_ADMIN must be set in environment.
Service name: ArachDB_b7d_fra.db.arachworknet.oraclevcn.com
DB host (private IP): 10.0.1.182
is-cdb: true (Container Database)

Automatic backups: enabled. SLOT_TWO (02:00-04:00 UTC), 7-day retention,
Object Storage. Full backup every Sunday.
Last manual backup: 2026-05-09 "pre-26ai-patch-manual-backup", ACTIVE.

Application schemas — CREATED and VERIFIED 2026-05-09:
    snomed       — production, TBS_SNOMED, NO_EXPIRY_PROFILE
    snomed_stage — stage, TBS_SNOMED_STAGE, NO_EXPIRY_PROFILE

Linux VM (arachnetwebserver): Oracle Linux 9. Public IP 130.61.83.216.
SSH alias: ara (in ~/.ssh/config on both Mac and Ubuntu).
SQLcl 24.4.1 on PATH as sql.

OCI CLI version: 3.79.0 on Mac.

Project root paths:
    OCI:    /home/opc/project_embeddings
    Ubuntu: /home/jan/project_embeddings


## 2. Technology stack and conventions

### Python
Python 3.10.12 on Ubuntu. Upgrade to 3.12 deferred — not blocking.
python-oracledb thin mode only. No Oracle client installation needed.
OmegaConf for configuration. PyYAML for YAML parsing.
Standard library only beyond the above. No frameworks.

### Coding conventions
Documented in docs/conventions.md, version 1.5. Key points:
- 4-space indentation in Python and SQL.
- .format() for all string formatting. No f-strings.
- Block markers around every Python function definition.
- Type annotations from _validate_mandatory_keys onward.
- NumPy-style docstrings in all Python functions.
- Plain Python testing with _report and _summarise pattern. No pytest.
- SQL keywords in uppercase. Schema, table, column names in lowercase.
- Bash logging via scripts/common/logger.sh. No bare echo for log messages.
- Import sections labelled: Standard library / Third-party / Project.
- Commit convention: feat: fix: docs: test: chore: refactor:
- Git: Ubuntu pushes. OCI and Mac pull only. Never edit code on OCI.

### Schema naming — IMPORTANT
Schema names in code and config match Oracle usernames exactly:
    snomed       — production schema
    snomed_stage — stage schema
    sys          — SYSDBA, setup only
No mapping or translation layer. database.yaml v1.4 uses these as keys.

### Environment variables — db_connection.py
    SNOMED_DB_PASSWORD          — snomed schema password
    SNOMED_STAGE_DB_PASSWORD    — snomed_stage schema password
    SNOMED_SYS_DB_PASSWORD      — sys password (renamed from SNOMED_ADMIN_DB_PASSWORD)

### Environment variables — run_sql_setup.sh
    ORACLE_SYS_USER / ORACLE_SYS_PASSWORD
    ORACLE_SNOMED_USER / ORACLE_SNOMED_PASSWORD
    ORACLE_SNOMED_STAGE_USER / ORACLE_SNOMED_STAGE_PASSWORD
    ORACLE_TNS_ALIAS / TNS_ADMIN


## 3. Repository structure

project_embeddings/
    config/
        project.yaml
        database.yaml         — version 1.4 (schema keys = Oracle usernames)
        ingestion.yaml

    src/
        common/
            exceptions.py     — complete, 45 tests passing
            logger.py         — complete, 13 tests passing
            config_loader.py  — complete, 32 tests passing
            db_connection.py  — Step 0.6, IN PROGRESS (see Section 6)

    scripts/
        common/
            logger.sh         — version 1.1
            functions.sh      — version 1.1
        run_tests.sh          — version 1.1
        run_sql_setup.sh      — version 1.3, run on OCI 2026-05-09

    tests/
        test_exceptions_py.py       — 45 tests, passing
        test_logger_py.py           — 13 tests, passing
        test_logger_sh.sh           — passing
        test_functions_sh.sh        — 10 tests, passing
        test_config_loader_py.py    — 32 tests, passing
        test_db_connection_r1_py.py — Round 1 written, NOT YET RUN
        test_db_connection_py.py    — orchestrator, pending

    sql/ddl/setup/              — all four scripts v1.2, run on OCI 2026-05-09

    docs/
        contacts.md              — version 1.0
        conventions.md           — version 1.5
        directory_structure.md   — version 1.4
        error_codes.md
        git_workflow.md
        phase0_foundation.md     — version 1.5
        project_summary.md       — this file, version 1.7
        todo.md                  — reconstructed, see Section 13
        todo_step_0_6.md         — version 1.0
        uzis_correspondence.md   — version 1.1
        runbooks/
            run_sql_setup.md
            patch_26ai.md        — version 1.0

    arc/                      — arc CLI v2.1, to be extracted after Phase 0
        arc_lib.sh, arc_send.sh, arc_get.sh,
        arc_openlink.sh, arc_status.sh
    arc_setup.sh              — version 2.0

    log/                      — NOT committed (.gitignore)
    venv/                     — NOT committed (.gitignore)
    transfer/                 — NOT committed (.gitignore)
    requirements.txt
    .gitignore
    LICENSE                   — BUSL 1.1, to be added


## 4. Environment variables per machine

### Ubuntu (~/.bashrc)
    export ORACLE_SYS_USER="SYS"
    export ORACLE_SYS_PASSWORD=""
    export ORACLE_SNOMED_USER="SNOMED"
    export ORACLE_SNOMED_PASSWORD=""
    export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
    export ORACLE_SNOMED_STAGE_PASSWORD=""
    export ORACLE_TNS_ALIAS="ARADB"
    export SNOMED_DB_PASSWORD=""
    export SNOMED_STAGE_DB_PASSWORD=""
    export SNOMED_SYS_DB_PASSWORD=""        # renamed from SNOMED_ADMIN_DB_PASSWORD
    export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
    export ANTHROPIC_API_KEY=""

### OCI (~/.bash_profile — single source of truth)
    export TNS_ADMIN="/opt/oracle/network/admin"
    export ORACLE_TNS_ALIAS="ARADB"
    export ORACLE_SYS_USER="SYS"
    export ORACLE_SYS_PASSWORD=""
    export ORACLE_SNOMED_USER="SNOMED"
    export ORACLE_SNOMED_PASSWORD=""
    export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
    export ORACLE_SNOMED_STAGE_PASSWORD=""
    export SNOMED_DB_PASSWORD=""
    export SNOMED_STAGE_DB_PASSWORD=""
    export SNOMED_SYS_DB_PASSWORD=""        # renamed from SNOMED_ADMIN_DB_PASSWORD
    export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
    # OCI resource OCIDs — all set, see .bash_profile on OCI

### MacOS (~/.bash_profile)
    # All OCI resource OCIDs set including OCI_DATABASE_OCID
    # No Oracle DB credentials needed on Mac


## 5. Phase 0 status

Step 0.1 — YAML configuration — Complete.
Step 0.2 — Error handling — Complete. 45 tests passing.
Step 0.3 — Logging utility — Complete.
Step 0.4 — Configuration loader — Complete. 32 tests passing.

Step 0.5 — SQL database setup — MOSTLY COMPLETE.
    Done:
    - Tablespaces, schemas, grants created and verified on OCI 2026-05-09
    - Automatic backups enabled on OCI
    - Git repo cleaned and synced across all three machines
    Pending:
    - 26ai patch — failed, waiting for Oracle support response
    - Python 3.12 upgrade on Ubuntu — deferred
    - Commit to formally close Step 0.5

Step 0.6 — Database connection helper — IN PROGRESS.
    Done:
    - database.yaml updated to v1.4
    - config_loader.py MANDATORY_KEYS updated
    - conventions.md updated to v1.5
    - db_connection.py: _get_credentials and get_connection written
    - test_db_connection_r1_py.py written (10 tests), NOT YET RUN
    Pending:
    - Run Round 1 tests on Ubuntu
    - Write Round 2 tests (get_connection mocked error paths)
    - Implement open_connection, execute_ddl, execute_batch,
      execute_query, test_connection, get_pool stub
    - Real DB tests on OCI (SNOMED_TEST_REAL_DB=true)

Step 0.7 — Bash pipeline orchestrator — Pending. Blocked on Step 0.6.


## 6. db_connection.py design (Step 0.6)

File: src/common/db_connection.py
Version: 1.0 (in progress)

Constants:
    _VALID_SCHEMAS = ("snomed", "snomed_stage", "sys")
    _RETRY_WAIT_SECONDS = 2
    _DDL_LOG_MAX_LENGTH = 200

Functions implemented:
    _get_credentials(cfg, schema) -> tuple
        Returns (username, password, tns_alias).
        Reads password from env var named in cfg — never stores it.
        Raises SnomedConfigError or SnomedDBConnectionError.

    get_connection(cfg, schema) -> oracledb.Connection
        Thin mode, autocommit=False.
        Adds AUTH_MODE_SYSDBA when schema == "sys".
        Retries once after _RETRY_WAIT_SECONDS.
        Raises SnomedDBConnectionError after two failures.

Functions pending:
    open_connection(cfg, schema) -> context manager
    execute_ddl(conn, sql) -> None
    execute_batch(conn, sql, data, batch_size) -> tuple
    execute_query(conn, sql, params=None) -> list[dict]
        Returns list of dicts — column names lowercased as keys.
    test_connection(cfg, schema="snomed") -> True
    get_pool(cfg, schema) -> raises NotImplementedError


## 7. Arc project CLI

Version 2.1. Extracted to own Claude project after this session.
See arc_project_summary.md for full context.

Currently in project_embeddings/arc/ — to be extracted to own repo
after Phase 0 closes.

Arc tested end-to-end 2026-05-10. Magic link workflow confirmed working.
Known issues: outbox cleanup (manual for now), shell detection on Mac.


## 8. Firefox and Orca accessibility

Status: WORKING. Authenticated on claude.ai via Firefox on Ubuntu.
Magic link workflow via arc confirmed working.

Voxin voices: recommended replacement for eSpeak. Good naturalness,
works well with Orca. Installation improved — now straightforward
package installer. Worth installing when Ubuntu is next accessible.

Key rules:
- Always start Orca before Firefox
- Press Enter on input fields to switch to Focus mode before typing
- Use Firefox ESR from APT, not snap
- USB tethering to iPhone preferred over café WiFi

Clipboard on Ubuntu:
    xclip -sel clip < file.txt    # file to clipboard
    xclip -sel clip -o            # clipboard to stdout


## 9. Git status (as of 2026-05-13)

Repository: git@github.com:arachnet-project/project_embeddings.git
Latest commit: e5c6c66 — all three machines in sync.
Git incident: RESOLVED.

Pending commits (to do on Ubuntu when cable is stable):
    src/common/db_connection.py   — updated with all convention fixes
    docs/conventions.md           — v1.5
    docs/project_summary.md       — v1.7 (this file)
    docs/todo.md                  — updated
    tests/test_db_connection_r1_py.py — new


## 10. Oracle 26ai patch — status

See docs/runbooks/patch_26ai.md for full details.
Precheck: SUCCEEDED. Apply: FAILED (2026-05-09).
DB on 23.7.0.25.01, fully operational. Not a blocker.
Oracle support informed. Awaiting response from Slavomír Seno.


## 11. Backup configuration

Auto-backup: ENABLED. SLOT_TWO, 7-day retention, Object Storage.
Full backup: every Sunday. Last manual backup: 2026-05-09, ACTIVE.


## 12. UZIS correspondence

Czech SNOMED CT RF2 package does not exist yet. Release date unknown.
Email sent to MUDr. Molinari (request for development sample) 2026-05-10.
CC: MUDr. Zvolský. Written in Czech.
See docs/uzis_correspondence.md and docs/contacts.md.


## 13. Immediate next actions (in order)

1.  Run Round 1 tests on Ubuntu when cable is stable:
        cd ~/project_embeddings && source venv/bin/activate
        python tests/test_db_connection_r1_py.py

2.  Commit pending files to repo from Ubuntu:
        src/common/db_connection.py
        docs/conventions.md
        docs/project_summary.md
        docs/todo.md
        tests/test_db_connection_r1_py.py
    Then git pull on OCI and Mac.

3.  Update ~/.bashrc on Ubuntu:
        Rename SNOMED_ADMIN_DB_PASSWORD to SNOMED_SYS_DB_PASSWORD.

4.  Deploy clean .bashrc and .bash_profile to OCI
    (produced 2026-05-10, in downloads).

5.  Install Voxin voices on Ubuntu for better Orca experience.

6.  Write Round 2 tests (get_connection mocked error paths).

7.  Implement open_connection, execute_ddl, execute_batch,
    execute_query, test_connection, get_pool.

8.  Run real DB tests on OCI (SNOMED_TEST_REAL_DB=true).

9.  Resolve 26ai patch with Oracle support.

10. Extract arc to own repository.

11. Add LICENSE (BUSL 1.1) to repository.

12. Formally close Step 0.5 with a commit.


## 14. Open questions and pending decisions

- 26ai patch failure root cause — waiting for Oracle support
- Python 3.12 upgrade deferred — revisit after Phase 0
- arc CLI not yet in own repo — after Phase 0
- SNOMED_TEST_REAL_DB=true tests not yet run since schemas created
- run_sql_setup.sh: SET VERIFY OFF missing — passwords shown in output
- OCI security hardening pending: fail2ban, cron audit, log rotation
- UZIS namespace process for Arachnet extension authoring not initiated
- MUDr. Molinari email address not confirmed — find before sending again
- LICENSE file not yet added to repo


## 15. Notes for LLMs reading this summary

- Jan is blind — Orca on Ubuntu, VoiceOver on Mac
- MacBook Air power cable unstable — prefer Mac M1 until fixed
- arc scripts use readlink -f for symlink-safe SCRIPT_DIR
- Git incident resolved — do not raise it again
- OCI DB on private subnet — access only via bastion (ara)
- Ubuntu pushes to git, OCI and Mac pull only
- Schema names = Oracle usernames: snomed, snomed_stage, sys
- SNOMED_ADMIN_DB_PASSWORD renamed to SNOMED_SYS_DB_PASSWORD
- database.yaml v1.4 — schema keys are Oracle usernames directly
- execute_query returns list[dict] — column names lowercased as keys
- 26ai patch failed — DB healthy on 23ai, not blocked for development
- Round 1 tests written but not yet run — do this before open_connection
- Arc has its own Claude project now — separate from this one
