# Arachnet Clinical Terminology Embeddings — Project Summary
# docs/project_summary.md
# =========================================
# Version: 1.6
# Last updated: 2026-05-09
# Purpose: Full project context for session handover and crash recovery.
#          Covers project overview, conventions, all Phase 0 steps,
#          infrastructure, tooling, and immediate next actions.
#          Complete history from Step 0.1 through session 2026-05-09.


## 1. Project overview

Arachnet Clinical Terminology Embeddings is a SNOMED CT terminology
embedding platform built on Oracle 23ai (being patched to 26ai).
It ingests SNOMED CT RF2 release files, loads them into Oracle,
validates completeness, swaps stage to production, and produces
clinical embeddings for downstream use.

Full name: Arachnet Clinical Terminology Embeddings
Short name: Arachnet
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

26ai patch: attempted 2026-05-09. Precheck passed, APPLY failed.
DB remains on 23.7.0.25.01 and is fully available. Root cause unknown.
Oracle support informed. See docs/runbooks/patch_26ai.md.
All application code works on 23ai — patch is not a blocker.

MacBook Pro M1 (soon Mac Studio M4) — macOS. Backup/secondary machine.
Used for OCI CLI operations, arc relay, general access.
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
Object Storage. Full backup every Sunday. Disabled temporarily during
patch attempt, must be re-enabled after patch completes.

Manual backup taken: 2026-05-09, "pre-26ai-patch-manual-backup", ACTIVE.

Two application schemas: snomed (production) and snomed_stage (stage).
Tablespaces: TBS_SNOMED and TBS_SNOMED_STAGE.
Profile: NO_EXPIRY_PROFILE.
Schemas CREATED and VERIFIED on OCI 2026-05-09. See Step 0.5.

Linux VM (arachnetwebserver): Oracle Linux 9. Public IP 130.61.83.216.
SSH alias: ara (in ~/.ssh/config on both Mac and Ubuntu).
sudo dnf update done. Rebooted.

OCI CLI version: 3.79.0 on Mac.

Project root paths:
    OCI:    /home/opc/project_embeddings
    Ubuntu: /home/jan/project_embeddings


## 2. Technology stack and conventions

### Python
Python 3.10.12 on Ubuntu. Upgrade to 3.12.x deferred — system gave
serious warning about third-party PPA. Not blocking anything.
python-oracledb in thin mode only. No Oracle client installation needed.
OmegaConf for configuration management. Pin exact version in requirements.txt.
PyYAML for YAML parsing. Import as: import yaml. Catch yaml.YAMLError.
Standard library only beyond the above. No frameworks.

### Oracle tooling
SQLcl 24.4.1 — available on OCI Linux VM. Command: sql on PATH.
scripts/run_sql_setup.sh v1.3 — orchestrates all four DDL setup scripts.

### Bash
Bash 4.0 or later required. Ubuntu and OCI both ship Bash 5.x.
set -euo pipefail and export LC_ALL=C.UTF-8 in all executable scripts.
Sourced library files do not set shell options or locale.
Set SNOMED_LOG_DIR before sourcing logger.sh in any executable script.

### Coding conventions
Documented in docs/conventions.md, version 1.5. Key points:
- 4-space indentation in Python and SQL.
- .format() for all Python string formatting. No f-strings.
- Block markers around every Python function definition.
- Type annotations from _validate_mandatory_keys onward.
- NumPy-style docstrings in all Python functions.
- Plain Python testing with _report and _summarise pattern. No pytest.
- SQL keywords in uppercase. Schema, table, column names in lowercase.
- Bash logging via scripts/common/logger.sh. No bare echo for log messages.
- Commit convention: feat: fix: docs: test: chore: refactor:
- Git: Ubuntu pushes. OCI pulls only. Never edit code on OCI.


## 3. Repository structure

project_embeddings/
    config/
        project.yaml
        database.yaml         — version 1.3
        ingestion.yaml

    src/
        common/
            exceptions.py     — complete
            logger.py         — complete
            config_loader.py  — complete
            db_connection.py  — Step 0.6, pending

    scripts/
        common/
            logger.sh         — version 1.1
            functions.sh      — version 1.1
        run_tests.sh          — version 1.1
        run_sql_setup.sh      — version 1.3, complete, run on OCI 2026-05-09

    tests/
        test_exceptions_py.py          — 45 tests, passing
        test_logger_py.py              — 13 tests, passing
        test_logger_sh.sh              — passing
        test_functions_sh.sh           — 10 tests, passing
        test_config_loader_py.py       — 32 tests, passing
        test_db_connection_py.py       — placeholder, Step 0.6 pending

    sql/
        ddl/
            setup/
                00_create_profile.sql  — v1.2, skip on OCI (profile exists)
                01_create_tablespaces.sql — v1.2, run 2026-05-09, OK
                02_create_schemas.sql  — v1.2, run 2026-05-09, OK
                03_grants.sql          — v1.2, run 2026-05-09, OK

    docs/
        contacts.md              — version 1.0, new 2026-05-09
        conventions.md           — version 1.5
        directory_structure.md   — version 1.4
        error_codes.md
        git_workflow.md
        phase0_foundation.md     — version 1.5
        project_summary.md       — this file, version 1.6
        todo.md                  — needs reconstruction
        uzis_correspondence.md   — version 1.1, updated 2026-05-09
        runbooks/
            run_sql_setup.md
            patch_26ai.md        — new 2026-05-09

    arc/                      — arc CLI, to be extracted to own repo after Phase 0
        arc_lib.sh            — version 2.1
        arc_send.sh           — version 2.1
        arc_get.sh            — version 2.1
        arc_openlink.sh       — version 2.1
        arc_status.sh         — version 2.1
    arc_setup.sh              — version 2.0

    log/                      — NOT committed (.gitignore)
    venv/                     — NOT committed (.gitignore)
    transfer/                 — NOT committed (.gitignore)
    requirements.txt
    .gitignore
    LICENSE                   — BUSL 1.1, to be added


## 4. Environment variables

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
    export SNOMED_ADMIN_DB_PASSWORD=""
    export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
    export ANTHROPIC_API_KEY=""

### OCI (~/.bashrc and ~/.bash_profile)
    # In ~/.bash_profile:
    export TNS_ADMIN="/opt/oracle/network/admin"
    export ORACLE_TNS_ALIAS="ARADB"

    # In ~/.bashrc:
    export ORACLE_SYS_USER="SYS"
    export ORACLE_SYS_PASSWORD=""
    export ORACLE_SNOMED_USER="SNOMED"
    export ORACLE_SNOMED_PASSWORD=""
    export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
    export ORACLE_SNOMED_STAGE_PASSWORD=""
    export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
    export SNOMED_LOG_LEVEL="DEBUG"
    # OCI resource OCIDs — all set, see .bashrc on OCI

### MacOS (~/.bash_profile)
    # All OCI resource OCIDs set
    export OCI_DATABASE_OCID="ocid1.database.oc1.eu-frankfurt-1.antheljsxs5lciqahi6ndmhgcqyc5ahdnsru27nxqf7oizgkzuplep2v5iza"
    # (and all other OCIDs — see .bash_profile on Mac)


## 5. Phase 0 status

Step 0.1 — YAML configuration files — Complete.
Step 0.2 — Error handling — Complete. 45 tests passing.
Step 0.3 — Logging utility — Complete.
Step 0.4 — Configuration loader — Complete. 32 tests passing.

Step 0.5 — SQL database setup — MOSTLY COMPLETE.

    Completed 2026-05-09:
    - Tablespaces TBS_SNOMED and TBS_SNOMED_STAGE created and verified
    - Schemas SNOMED and SNOMED_STAGE created with NO_EXPIRY_PROFILE
    - All grants applied and verified
    - Cross-schema grant: SELECT ANY TABLE ON SCHEMA snomed_stage TO snomed
    - Verified via dba_users, dba_sys_privs, dba_schema_privs

    Remaining:
    - 26ai patch: failed, pending resolution with Oracle support
      DB fully operational on 23ai in the meantime
    - Auto-backups: currently DISABLED (disabled before patch attempt)
      MUST re-enable after patch or explicitly as a separate step:
        oci db database update --database-id $OCI_DATABASE_OCID \
            --auto-backup-enabled true \
            --auto-backup-window SLOT_TWO \
            --recovery-window-in-days 7
    - Python 3.12 upgrade: deferred, not blocking
    - Git commit to close Step 0.5: pending

Step 0.6 — Database connection helper — Pending. Not blocked by 26ai.
Step 0.7 — Bash pipeline orchestrator — Pending. Blocked on Step 0.6.


## 6. db_connection.py design (Step 0.6)

File location: src/common/db_connection.py
All Oracle communication goes through this module exclusively.
Uses oracledb thin mode only.

Functions:
    _get_credentials(cfg, schema) -> tuple
    get_connection(cfg, schema) -> oracledb.Connection
    open_connection(cfg, schema) -> context manager
    execute_ddl(conn, sql) -> None
    execute_batch(conn, sql, data, batch_size) -> tuple
    test_connection(cfg, schema="production") -> True
    get_pool(cfg, schema) -> raises NotImplementedError

Testing: mock on Ubuntu, real connection with SNOMED_TEST_REAL_DB=true on OCI.


## 7. Arc project CLI

Version 2.1. Cross-machine file relay using OCI Linux VM as passive dropbox.
Located in project_embeddings/arc/ — to be extracted to own repo after Phase 0.

Files:
    arc_lib.sh, arc_send.sh, arc_get.sh, arc_openlink.sh,
    arc_status.sh, arc_setup.sh

Config: ~/.arc_config on each machine:
    ARC_RELAY_HOST="ara"
    ARC_RELAY_TRANSFER="/home/opc/transfer"
    ARC_LOCAL_TRANSFER="${HOME}/transfer"
    ARC_SSH_KEY=""

Transfer directories on OCI (passive relay):
    ~/transfer/inbox/
    ~/transfer/outbox/

Status: tested end-to-end on Mac and Ubuntu 2026-05-09.
Magic link workflow confirmed working.
arc_setup.sh run on both machines. Symlinks in ~/bin.

Known issues to fix:
- Shell detection on Mac (uses bash not zsh despite zsh being default)
- Outbox cleanup — no --delete, files accumulate
- SET VERIFY OFF missing in run_sql_setup.sh heredoc (passwords shown)

Arc future repo: separate Git repository after Phase 0 closes.


## 8. Firefox and Orca accessibility

Status: WORKING as of 2026-05-09.
Authenticated on claude.ai via Firefox on Ubuntu.
Magic link workflow via arc confirmed working.

Key rules:
- Always start Orca before Firefox
- Press Enter on input fields to switch to Focus mode before typing
- Use Firefox ESR from APT, not snap
- USB tethering to iPhone preferred over café WiFi (no captive portal)

Clipboard workflow on Ubuntu:
    xclip -o > ~/clip.txt    # clipboard to file
    xclip -i < ~/clip.txt    # file to clipboard
Install: sudo apt install xclip


## 9. Git status (as of 2026-05-09)

Repository: git@github.com:arachnet-project/project_embeddings.git
All three machines in sync on main branch.
Latest commit: "chore: restore run_tests.sh to correct location"

Git incident (API key): RESOLVED. History cleaned. Remote clean.

Workflow: Ubuntu pushes. OCI and Mac pull only.


## 10. Oracle 26ai patch — status

See docs/runbooks/patch_26ai.md for full details.

Current state: FAILED. DB on 23.7.0.25.01, fully operational.
Precheck: SUCCEEDED (2026-05-09)
Apply: FAILED after ~2 minutes (2026-05-09), reason unknown
Oracle support: informed (email to Slavomír Seno, Viktor Nemec, Filip Rodr)

CRITICAL REMINDER: automatic backups are currently DISABLED.
Re-enable before leaving the system unattended for more than a day.
Command: see Section 5, Step 0.5 remaining items.

Next steps on 26ai:
1. Wait for Oracle support response from Slavomír Seno
2. Try January patch (23.26.1.0.0) as alternative
3. Check OCI console patch history for more detail


## 11. Backup configuration

Auto-backup: currently DISABLED (must re-enable)
Window: SLOT_TWO (02:00-04:00 UTC = 04:00-06:00 Prague CEST)
Full backup: every Sunday
Retention: 7 days
Destination: Object Storage (does not use DB disk)
Last successful backup: 2026-05-09 "pre-26ai-patch-manual-backup", 3GB, ACTIVE


## 12. UZIS correspondence

See docs/uzis_correspondence.md for full details.
See docs/contacts.md for contact information.

Summary:
- Czech SNOMED CT RF2 package does not exist yet
- Release date unknown
- Translation covers FSN, PT, synonyms — quality varies
- Email drafted to MUDr. Molinari requesting development sample
- Molinari's email address unknown — find before sending


## 13. Immediate next actions (in order)

1.  Re-enable automatic backups on OCI (CRITICAL — currently disabled):
        oci db database update --database-id $OCI_DATABASE_OCID \
            --auto-backup-enabled true \
            --auto-backup-window SLOT_TWO \
            --recovery-window-in-days 7

2.  Find MUDr. Molinari's email address and send draft email.

3.  Send email to Slavomír Seno (Oracle) about 26ai patch findings.

4.  Git commit to close Step 0.5:
        git add -A
        git commit -m "chore: Step 0.5 complete — schemas, grants verified"
        git push
    Then on OCI and Mac: git pull

5.  Write docs/todo_step_0_6.md.

6.  Begin Step 0.6 — db_connection.py.
    Can be done on Ubuntu with mocked tests — no OCI needed.

7.  Resolve 26ai patch with Oracle support.

8.  Extract arc to own repository after Phase 0.

9.  Reconstruct docs/todo.md.

10. Add LICENSE (BUSL 1.1) to repository.


## 14. Open questions and pending decisions

- 26ai patch failure root cause — waiting for Oracle support
- Automatic backups currently disabled — re-enable immediately
- MUDr. Molinari email address unknown
- docs/todo.md empty — reconstruct
- LICENSE file not yet added
- Python 3.12 upgrade deferred — revisit after Phase 0
- arc CLI not yet in own repo — after Phase 0
- SNOMED_TEST_REAL_DB=true tests not run since schemas created
- run_sql_setup.sh: SET VERIFY OFF missing — passwords shown in output
- OCI security hardening pending: fail2ban, cron audit, log rotation
- UZIS namespace process for Arachnet extension authoring not initiated


## 15. Notes for LLMs reading this summary

- Do not suggest f-strings — .format() only
- Do not suggest pytest — plain _report/_summarise pattern
- Jan is blind — uses Orca screen reader on Ubuntu, VoiceOver on Mac
- arc scripts use readlink -f for symlink-safe SCRIPT_DIR
- Git incident is resolved — do not raise it again
- Auto-backups are DISABLED — flag this if not addressed
- OCI DB is on private subnet — access only via bastion (ara)
- Ubuntu pushes to git, OCI and Mac pull only
- Magic link workflow: Claude.ai sends login link → arc relays via OCI → Ubuntu opens
- 26ai patch failed — DB is healthy on 23ai, not blocked for development
