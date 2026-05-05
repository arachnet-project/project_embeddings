# Arachnet Clinical Embeddings — Project Summary
# docs/project_summary.md
# =========================================
# Version: 1.5
# Last updated: 2026-05-05
# Purpose: Full project context for session handover and crash recovery.
#          Covers project overview, conventions, all Phase 0 steps,
#          infrastructure, tooling, and immediate next actions.
#          Complete history from Step 0.1 through session 2026-05-05.


## 1. Project overview

Arachnet Clinical Embeddings is a SNOMED CT terminology embedding platform
built on Oracle 23ai (being upgraded to 26ai). It ingests SNOMED CT RF2
release files, loads them into Oracle, validates completeness, swaps stage
to production, and produces clinical embeddings for downstream use.

Owner: Jan Mura, Arachnet Project z.s.
Licence: BUSL 1.1 (to be added to repository).


### Platforms

Ubuntu on MacBook Air (hostname: jan-MacBookAir) — primary development
and testing machine. MacBook Air hardware running Ubuntu Linux natively,
no macOS, no virtual machine. Python venv, mocked database tests,
Git origin. All development happens here first.

OCI Frankfurt — Oracle Cloud Infrastructure. Production target.
Oracle database: 23ai SE2, version 23.7.0.25.01.
Real database tests run here with SNOMED_TEST_REAL_DB=true.

26ai upgrade: confirmed available on OCI. Upgrade is a patch (release
update), not a full database upgrade — internal version stays 23.0.0.0.0,
only VERSION_FULL changes to 23.26.0.0.0. No application re-certification
required. All objects, grants, profiles created under 23ai carry over
unchanged. Run setup scripts on 23ai first, then apply 26ai patch.

Mac Studio — Phase 3 ML computations only. Not relevant until Phase 3.


### Infrastructure

Oracle Database on OCI: 23ai SE2, version 23.7.0.25.01.
Managed DB System on separate VM in private VCN.
No public IP on DB VM — access only from Linux VM via private subnet.
TNS alias: ARADB. TNS_ADMIN must be set in environment before any
script or connection attempt.

Two application schemas: snomed (production) and snomed_stage (stage).
Tablespaces: TBS_SNOMED and TBS_SNOMED_STAGE.
Profile: NO_EXPIRY_PROFILE — no password expiry, FAILED_LOGIN_ATTEMPTS=10,
PASSWORD_LOCK_TIME=1/24 (1-hour auto-unlock, defence in depth).

SYS and SYSTEM: already assigned to NO_EXPIRY_PROFILE. Done.

Schemas snomed and snomed_stage: NOT YET CREATED on OCI.
SQL setup scripts written, reviewed, approved at v1.2.
Must be run via scripts/run_sql_setup.sh. See Section 5, Step 0.5.

Linux VM (arachnetwebserver): Oracle Linux 9. Public IP 130.61.83.216.
sudo dnf update was aborted at confirmation prompt. Needs re-run with y.
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
SQLcl 24.4.1 or later — available on OCI Linux VM. Command: sql on PATH.
scripts/run_sql_setup.sh — orchestrates all four DDL setup scripts.
    Sources logger.sh and functions.sh.
    Validates env vars via require_var.
    Injects credentials as DEFINE variables into SQLcl heredoc.
    Supports RUN_00=true flag to optionally include 00_create_profile.sql.
    Do NOT set RUN_00 in .bashrc — use inline: RUN_00=true bash ...
    Current version: 1.3 (bugs fixed 2026-05-05, see Section 5).

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
Import yaml directly (import yaml) not submodules (import yaml.parser).
Catch yaml.YAMLError not yaml.parser.ParserError.


## 3. Repository structure

project_embeddings/
    config/
        project.yaml          — root config, includes database.yaml, ingestion.yaml
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
        run_sql_setup.sh      — DDL setup runner (version 1.3, complete)
        test_infrastructure_sh.sh — OCI resource OCID verification (fixed 2026-05-05)
        run.sh                — main pipeline orchestrator (Step 0.7, pending)

    arc/                      — project CLI automation tool (new 2026-05-05)
        arc_lib.sh            — shared library for all arc commands
        arc_send.sh           — arc-send: rsync outbox to remote machine
        arc_get.sh            — arc-get: receive files or pull from remote
        arc_openlink.sh       — arc-openlink: open URL from inbox link file
        arc_status.sh         — arc-status: show transfer directory state
    arc_setup.sh              — arc CLI installer (run once per machine)

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
        project_summary.md          — this file, version 1.5
        todo.md                     — needs reconstruction after crash
        todo_step_0_5.md            — Step 0.5 SQL setup todo
        todo_step_0_6.md            — Step 0.6 db_connection todo, to be written
        dev_workflow.md             — daily workflow and testing strategy
        claude_chat_howto.md        — claude_chat.py usage guide
        uzis_correspondence.md      — UZIS email analysis and meeting agenda
        uzis_meeting_prep.md        — meeting script for UZIS online meeting
        runbooks/
            run_sql_setup.md        — verify reflects run_sql_setup.sh v1.3

    log/                            — NOT committed to Git (.gitignore)
    venv/                           — NOT committed to Git (.gitignore)
    claude_chat.py                  — Claude API terminal interface (project root)
    requirements.txt
    syn.sh                          — rsync sync script
    .gitignore
    LICENSE                         — BUSL 1.1, to be added


## 4. Environment variables

All credentials managed via environment variables in ~/.bashrc on each
machine. Never commit passwords or keys to version control.

    # Oracle admin credentials — SYSDBA, used by run_sql_setup.sh only
    export ORACLE_SYS_USER="SYS"
    export ORACLE_SYS_PASSWORD=""               # fill in on each machine

    # Application schema credentials — used by run_sql_setup.sh
    export ORACLE_SNOMED_USER="SNOMED"
    export ORACLE_SNOMED_PASSWORD=""            # fill in on each machine

    export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
    export ORACLE_SNOMED_STAGE_PASSWORD=""      # fill in on each machine

    # TNS alias — used by run_sql_setup.sh and db_connection.py
    export ORACLE_TNS_ALIAS="ARADB"

    # db_connection.py reads these names from database.yaml config.
    # Same values as above, different variable names.
    export SNOMED_DB_PASSWORD=""                # same as ORACLE_SNOMED_PASSWORD
    export SNOMED_STAGE_DB_PASSWORD=""          # same as ORACLE_SNOMED_STAGE_PASSWORD
    export SNOMED_ADMIN_DB_PASSWORD=""          # same as ORACLE_SYS_PASSWORD

    # OCI resource OCIDs
    export OCI_NETWORK_COMPARTMENT_OCID=""
    export OCI_DB_COMPARTMENT_OCID=""
    export OCI_LINUX_COMPARTMENT_OCID=""
    export OCI_VCN_OCID=""
    export OCI_PUBLIC_SUBNET_OCID=""
    export OCI_PRIVATE_SUBNET_OCID=""
    export OCI_LINUX_VM_OCID=""
    export OCI_DB_SYSTEM_OCID=""
    export OCI_BASTION_OCID=""

    # Logging — path differs per machine
    export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"   # Ubuntu
    # export SNOMED_LOG_DIR="/home/opc/project_embeddings/log" # OCI

    # Anthropic API key — Ubuntu only, for claude_chat.py
    # CRITICAL: Never commit. Key from log/transcript_2026-05-02_20-24-14.txt
    # has been COMPROMISED and must be revoked. See Section 9.
    export ANTHROPIC_API_KEY=""                 # fill in new key after revocation

    # Claude alias — Ubuntu only
    alias claude="cd /home/jan/project_embeddings && \
        source venv/bin/activate && python claude_chat.py"


## 5. Phase 0 status

Step 0.1 — YAML configuration files — Complete.
    config/project.yaml, config/database.yaml, config/ingestion.yaml.
    active_environment: development. Environment key: development (not dev).
    Dev base path: /home/jan/project_embeddings.
    database.yaml version 1.3 — DB connection, schema credential env var
    names (not values), table registry.

Step 0.2 — Error handling — Complete.
    src/common/exceptions.py written and tested (45 tests passing).
    Exception hierarchy:
        SnomedBaseError          base class
        SnomedConfigError        exit code 1
        SnomedDBConnectionError  exit code 2
        SnomedDDLError           exit code 3
        SnomedLoadError          exit code 4
        SnomedValidationError    exit code 5

Step 0.3 — Logging utility — Complete.
    src/common/logger.py written and tested (13 tests passing).
    scripts/common/logger.sh written and tested (version 1.1).
    Log format: YYYY-MM-DDTHH:MM:SS | LEVEL    | name | message

Step 0.4 — Configuration loader — Complete. 32 tests passing.
    src/common/config_loader.py — four rounds of testing.
    Functions:
        _load_yaml_file, _merge_includes, _resolve_paths, _walk_tree,
        _resolve_interpolation, _validate_mandatory_keys,
        _export_to_env, load_config(config_dir=None)
    Key decisions:
        MANDATORY_KEYS hardcoded as Python list (Option A).
        Lists warn to stderr in CLI export mode.
        cfg.paths uses OmegaConf.to_container(resolve=False) hard copy.
        load_config accepts optional config_dir for testability.

Step 0.5 — SQL database setup — Scripts complete, NOT yet run on OCI.

    SQL scripts (all version 1.2, reviewed and approved):
    Target: Oracle 23ai / 26ai. No 19c fallback anywhere.

    00_create_profile.sql:
        Creates NO_EXPIRY_PROFILE.
        FAILED_LOGIN_ATTEMPTS=10, PASSWORD_LOCK_TIME=1/24.
        Skip on OCI — profile already exists.
        Use RUN_00=true only on a fresh database.

    01_create_tablespaces.sql:
        Creates TBS_SNOMED and TBS_SNOMED_STAGE.
        Explicit EXTENT MANAGEMENT LOCAL AUTOALLOCATE,
        SEGMENT SPACE MANAGEMENT AUTO.

    02_create_schemas.sql:
        Creates users SNOMED and SNOMED_STAGE.
        Credentials via &&ORACLE_SNOMED_USER / &&ORACLE_SNOMED_PASSWORD
        SQL*Plus substitution variables — no hardcoded credentials.

    03_grants.sql:
        GRANT CREATE SESSION, TABLE, VIEW, SEQUENCE, PROCEDURE to snomed.
        GRANT CREATE SESSION, TABLE, SEQUENCE to snomed_stage only
            (ingestion target — no VIEW or PROCEDURE).
        QUOTA UNLIMITED on assigned tablespace per schema.
        QUOTA 0 ON SYSTEM — blocks accidental system tablespace writes.
        Cross-schema SELECT (Oracle 23ai/26ai schema-level privilege):
            GRANT SELECT ANY TABLE ON SCHEMA snomed_stage TO snomed;
        Covers all current and future tables automatically.

    run_sql_setup.sh (version 1.3 — four bugs fixed 2026-05-05):
        Sources logger.sh and functions.sh.
        require_var checks all nine credential and path variables.
        Verifies tnsnames.ora present at TNS_ADMIN.
        run_ddl_script() connects via SQLcl, injects DEFINE variables.

        Bugs fixed in v1.3:
        1. || true on SQLcl call swallowed exit code — removed.
        2. WHENEVER SQLERROR EXIT SQL.SQLCODE moved before CONNECT.
        3. EXIT SUCCESS changed to EXIT 0.
        4. DEFINE names corrected to match &&ORACLE_SNOMED_USER syntax.
        5. Verification hint: schema grant is in dba_schema_privs,
           not dba_sys_privs.

        Usage:
            bash scripts/run_sql_setup.sh
            RUN_00=true bash scripts/run_sql_setup.sh   # fresh DB only

    Bash infrastructure (all complete):
        scripts/common/logger.sh version 1.1
        scripts/common/functions.sh version 1.1
            Key fix: return 1 not exit 1 in require_var and require_command.
            Counter defaults initialised at source time.
        scripts/run_tests.sh version 1.1
        tests/test_functions_sh.sh version 1.2 — 10 tests passing.
        Full test suite: 6 scripts, all passing on Ubuntu.

    OCI infrastructure test script (scripts/test_infrastructure_sh.sh):
        Test 9 (DB OCID retrieval) fixed 2026-05-05.
        Root cause: --all not supported in OCI CLI 3.79.0 for
        oci db database list.
        Fix: --all replaced with --limit 10, Python loop filters
        by lifecycle-state == AVAILABLE.

    Remaining to close Step 0.5:

    A. Fill passwords into ~/.bashrc on OCI and Ubuntu.
       ORACLE_SYS_PASSWORD, ORACLE_SNOMED_PASSWORD,
       ORACLE_SNOMED_STAGE_PASSWORD and SNOMED_* equivalents.

    B. Run sudo dnf update on OCI Linux VM, then reboot.
       SSH to 130.61.83.216.
       sudo dnf update   (type y)
       sudo reboot
       Reconnect after 3-5 minutes.

    C. Deploy test_infrastructure_sh.sh fix to OCI and re-run.
       bash scripts/test_infrastructure_sh.sh
       All 10 checks should pass.

    D. Run SQL setup scripts on OCI.
       bash scripts/run_sql_setup.sh
       Verify:
           SELECT username, default_tablespace, profile
           FROM dba_users
           WHERE username IN ('SNOMED', 'SNOMED_STAGE');

           SELECT * FROM dba_sys_privs
           WHERE grantee IN ('SNOMED', 'SNOMED_STAGE')
           ORDER BY grantee, privilege;

           SELECT * FROM dba_schema_privs
           WHERE grantee = 'SNOMED';

    E. Upgrade Python to 3.12.x on Ubuntu.
           sudo apt update
           sudo apt install -y software-properties-common
           sudo add-apt-repository -y ppa:deadsnakes/ppa
           sudo apt update
           sudo apt install -y python3.12 python3.12-venv python3.12-dev
           cd ~/project_embeddings
           rm -rf venv
           python3.12 -m venv venv
           source venv/bin/activate
           pip install --upgrade pip
           pip install -r requirements.txt
           pip install anthropic
       Rerun: bash scripts/run_tests.sh
       Confirm all 6 scripts pass on Python 3.12.
       Update docs/conventions.md Python version to 3.12.

    F. Apply 26ai patch via OCI console.
       Precheck first. Manual backup. Disable auto-backups.
       After patch: verify TNS_ADMIN and tnsnames.ora unchanged.
       Run test query via SQLcl to confirm connectivity.

    G. Commit and close Step 0.5.
       Message: fix: SQL scripts v1.2, run_sql_setup.sh v1.3,
       Bash infrastructure, Python 3.12, 26ai patch confirmed.

Step 0.6 — Database connection helper — Pending. Blocked on Step 0.5.
Step 0.7 — Bash pipeline orchestrator — Pending. Blocked on Step 0.6.


## 6. db_connection.py design (Step 0.6)

File location: src/common/db_connection.py
All Oracle communication goes through this module exclusively.
Uses oracledb thin mode only. No Oracle client installation needed.
No code outside this module imports oracledb directly.

Module-level constants:
    _VALID_SCHEMAS = ("production", "stage", "admin")
    _RETRY_WAIT_SECONDS = 2
    _DDL_LOG_MAX_LENGTH = 200

Imports:
    import time
    import oracledb
    from contextlib import contextmanager
    from src.common.exceptions import (
        SnomedConfigError, SnomedDBConnectionError,
        SnomedDDLError, SnomedLoadError)
    from src.common.logger import get_logger

Functions:

_get_credentials(cfg, schema) -> tuple(user, password, tns_alias)
    Internal. Resolves password from env var named in config.
    Valid schemas: production, stage, admin.
    Raises SnomedConfigError for unknown schema.
    Raises SnomedDBConnectionError if env var not set or empty.
    Never logs the password value.

get_connection(cfg, schema) -> oracledb.Connection
    Public. Returns direct oracledb connection in thin mode.
    autocommit=False on all connections.
    Retries once after _RETRY_WAIT_SECONDS on failure.
    Raises SnomedDBConnectionError after two failures.

open_connection(cfg, schema) -> context manager -> oracledb.Connection
    Public. Context manager wrapping get_connection.
    Connection closed automatically on exit, even on exception.
    No commit on exception — caller handles commit/rollback.
    Implemented with @contextmanager decorator.

execute_ddl(conn, sql) -> None
    Public. Executes single DDL statement.
    Logs SQL at DEBUG (truncated to _DDL_LOG_MAX_LENGTH chars).
    Raises SnomedDDLError on failure with Oracle error code.
    DDL implicitly commits — no explicit commit needed.

execute_batch(conn, sql, data, batch_size)
        -> tuple(rows_loaded, batches_processed)
    Public. Bulk INSERT via executemany in batches of batch_size.
    Does NOT commit — caller commits after all batches.
    Rolls back and raises SnomedLoadError on any batch failure.

test_connection(cfg, schema="production") -> True
    Public. Executes SELECT 1 FROM DUAL.
    Returns True on success.
    Raises SnomedDBConnectionError on failure — never returns False.

get_pool(cfg, schema) -> raises NotImplementedError
    Public stub. Connection pooling deferred to Phase 3/4.

Testing:
    Ubuntu: mock oracledb.connect with unittest.mock.
    OCI: real connection via SNOMED_TEST_REAL_DB=true.


## 7. Arc project CLI

Cross-machine automation CLI built 2026-05-05. Provides named commands
as symlinks in ~/bin for repeated cross-machine workflows. Uses rsync
over SSH. OCI Linux VM acts as bridge between Ubuntu and MacOS.

Files:
    arc_setup.sh              installer — run once on each machine
    arc/arc_lib.sh            shared library (config, SSH opts, Orca check)
    arc/arc_send.sh           rsync ~/transfer/outbox to remote inbox
    arc/arc_get.sh            list inbox or pull from remote
    arc/arc_openlink.sh       open URL from inbox/link/link.txt in Firefox
    arc/arc_status.sh         show transfer directory state

Transfer directory (created by arc_setup.sh on each machine):
    ~/transfer/
        outbox/               stage files here before arc-send
        outbox/link/link.txt  put magic links here
        inbox/                files arrive here from remote
        inbox/link/link.txt   link file, opened by arc-openlink

Config: ~/.arc_config (created by arc_setup.sh):
    ARC_UBUNTU_HOST="jan@130.61.83.216"
    ARC_MACOS_HOST="jan@<macos-ip>"

Setup (run once on each machine):
    bash arc_setup.sh
    export PATH="$HOME/bin:$PATH"   # add to ~/.bashrc if not present

Claude magic link workflow:
    On MacOS:
        echo "https://claude.ai/magic-link/..." \
            > ~/transfer/outbox/link/link.txt
        arc-send ubuntu
    On Ubuntu:
        arc-get
        arc-openlink    # starts Orca if needed, opens Firefox with URL

arc-openlink always starts Orca before Firefox if not already running.
Prints reminder to press Enter before typing in any form field.

Status: written, not yet committed or tested end-to-end.
Commit after setup is tested on both machines.


## 8. Firefox and Orca accessibility

Platform: Ubuntu on MacBook Air. Screen reader: Orca. Browser: Firefox ESR.

Root cause of login form focus loss:
    Orca Browse mode intercepts single keypresses as navigation commands.
    Pressing 'a' while in Browse mode jumps to next anchor, not text input.

Fix — switch to Focus mode before typing:
    Press Enter when landed on an input field.
    Orca announces "focus mode" or plays a chime.
    Type normally. Press Escape to return to Browse mode.

Startup order (always Orca first):
    orca &
    sleep 2
    firefox https://claude.ai &
    arc-openlink handles this automatically.

Find Orca modifier key:
    grep -r "orcaModifierKeys" ~/.local/share/orca/
    or: orca --setup
    Desktop layout: Insert or KP_Insert.
    Laptop layout: Caps Lock.

Enable accessibility bridge (required):
    gsettings get org.gnome.desktop.interface toolkit-accessibility
    gsettings set org.gnome.desktop.interface toolkit-accessibility true

Firefox: use ESR from APT, not the snap version.
Check: which firefox   # /snap/ in path means snap version

Switch from snap to APT ESR:
    sudo snap remove firefox
    sudo add-apt-repository ppa:mozillateam/ppa
    sudo apt update
    echo 'Package: firefox*
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001' | sudo tee /etc/apt/preferences.d/mozilla-firefox
    sudo apt install firefox-esr


## 9. Git security incident

Incident: Anthropic API key committed in
log/transcript_2026-05-02_20-24-14.txt at line 402,
commit 35bf63135544abd60941d1fb3858ff7dadcdb1a5.
GitHub push protection blocked the push — remote is still clean.

Status: UNRESOLVED. Key not yet revoked. History not yet cleaned.

Resolution steps (in order):

1. Fix Firefox/Orca (Section 8) — needed to reach console.anthropic.com.

2. Log in to console.anthropic.com.
   Create a new API key.
   Update ANTHROPIC_API_KEY in ~/.bashrc. Source ~/.bashrc.

3. Revoke old key via CLI using new key:
       curl https://api.anthropic.com/v1/api_keys \
         -H "x-api-key: $ANTHROPIC_API_KEY" \
         -H "anthropic-version: 2023-06-01" \
         -H "anthropic-beta: api-keys-2024-10-11" \
         | python3 -m json.tool
       # find the id of the old key, then:
       curl -X DELETE \
         https://api.anthropic.com/v1/api_keys/PASTE_OLD_KEY_ID \
         -H "x-api-key: $ANTHROPIC_API_KEY" \
         -H "anthropic-version: 2023-06-01" \
         -H "anthropic-beta: api-keys-2024-10-11"

4. Remove log/ from all git history:
       pip install git-filter-repo --break-system-packages
       cd ~/project_embeddings
       git filter-repo --path log/ --invert-paths

5. Verify clean:
       git grep "sk-ant" $(git log --format="%H")
       # must return nothing

6. Confirm log/ is in .gitignore:
       grep "log/" .gitignore
       # if missing: echo "log/" >> .gitignore && git add .gitignore
       #             git commit -m "chore: ensure log/ excluded"

7. Re-add remote (filter-repo removes it):
       git remote add origin \
           git@github.com:arachnet-project/project_embeddings.git

8. Force push:
       git push --force origin main


## 10. Oracle Agentic AI — project relevance

Oracle 26ai introduces Select AI Agent and MCP server integration.
Autonomous Database MCP Server is NOT available on Base DB System (your setup).

What IS available:

SQLcl MCP Server — works with Base DB System from Phase 1 onward.
    Point Claude Desktop at SQLcl running in MCP mode for natural
    language database queries during development and QA.
    Config:
        { "mcpServers": { "oracle-sqlcl": {
            "command": "/path/to/sqlcl/bin/sql", "args": ["-mcp"] } } }

Phase 3 Python hybrid workflow (no Oracle agentic features needed):
    1. Oracle vector search over SNOMED concept embeddings.
    2. Top-N results sent to Claude API.
    3. Claude explains best match and clinical distinctions.
    Fits naturally with db_connection.py from Step 0.6.

If Select AI Agent is wanted in future: migration to Autonomous Database
required. Significant decision — not an immediate concern.


## 11. claude_chat.py

Location: ~/project_embeddings/claude_chat.py
Purpose: Terminal interface to Claude API. Designed for Orca screen reader.
Recommendation: switch to claude.ai web interface to eliminate per-token
API cost. $25 spent in ~18 days — long sessions expensive due to full
history sent per turn.

Transcripts: ~/project_embeddings/log/transcript_*.txt
CRITICAL: transcripts may contain API keys if key is printed in session.
log/ must never be committed. See Section 9.

Features:
    --session NAME, --model sonnet|opus
    /json /save /quit /clear /history /sessions /file /extract
    MAX_TOKENS: 8192
    Models: claude-sonnet-4-6 ($3/$15/M), claude-opus-4-6 ($5/$25/M)

Alias:
    alias claude="cd /home/jan/project_embeddings && \
        source venv/bin/activate && python claude_chat.py"


## 12. UZIS correspondence

Contact: MUDr. Irena Molinari (UZIS), Mr. Zvolský (Standardisation).
Online meeting arranged. Prep: docs/uzis_meeting_prep.md.

Confirmed:
    RF2 package follows SNOMED International standards.
    Language refset SCTID included in distribution.
    Czech descriptions: sct_description with languageCode=cs.
    Arachnet added to release notification list.

Open questions:
    ModuleId stability (likely confused with effectiveTime — confirm SCTID).
    Complete refset inventory.
    Release schedule vs SNOMED International.
    Package access for development.
    Namespace process for Arachnet extension authoring.

Meeting date: not confirmed. Check email.


## 13. Immediate next actions (in order)

1.  Fix Firefox/Orca (Section 8):
    toolkit-accessibility, ESR vs snap, startup order.

2.  Resolve git security incident (Section 9):
    revoke old key, clean history, force push.
    Prerequisite: Firefox working to reach console.anthropic.com.

3.  Add billing payment at console.anthropic.com if API access still needed.

4.  Fill passwords into ~/.bashrc on Ubuntu and OCI.

5.  Run sudo dnf update on OCI Linux VM (130.61.83.216), then reboot.

6.  Deploy test_infrastructure_sh.sh fix to OCI, re-run all 10 checks.

7.  Run SQL setup scripts on OCI:
    bash scripts/run_sql_setup.sh
    Run verification queries (Section 5, item D).

8.  Upgrade Python to 3.12 on Ubuntu (Section 5, item E).
    Rerun full test suite.

9.  Apply 26ai patch via OCI console.
    Precheck, backup, patch, verify connectivity.

10. Commit and close Step 0.5.

11. Write docs/todo_step_0_6.md, then begin Step 0.6 — db_connection.py.

12. Set up arc CLI on both machines:
    bash arc_setup.sh, fill ~/.arc_config, test magic link workflow.

13. Reconstruct docs/todo.md (empty after crash).


## 14. Open questions and pending decisions

- Confirm oracledb thin mode unchanged after 26ai patch.
- docs/todo.md empty — reconstruct after Step 0.5 closes.
- docs/todo_step_0_6.md not yet written.
- LICENSE file (BUSL 1.1) not yet added.
- docs/runbooks/run_sql_setup.md — verify reflects run_sql_setup.sh v1.3.
- docs/conventions.md — update Python version to 3.12 after upgrade.
- UZIS meeting date not confirmed.
- Consider migrating fully from claude_chat.py to claude.ai web interface.
- run_ddl_script() should become general run_sql() in functions.sh — Step 0.6.
- arc CLI not yet committed — commit after tested on both machines.
- Check claude_chat.py does not print ANTHROPIC_API_KEY in session output.
