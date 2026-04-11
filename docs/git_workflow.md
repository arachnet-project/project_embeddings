

=== BEGIN FILE: docs/git_workflow.md ===
# Git Workflow — Arachnet Clinical Embeddings

**Document version:** 1.2
**Date:** 2026-04-10

---

## Overview

The project uses Git with GitHub as the remote repository, accessed via
SSH on all machines. Two machines are in active use:

Machine / Role / OS:
Ubuntu (primary dev machine) / Development / Ubuntu
OCI Frankfurt VM / Production / Oracle Linux 9

Mac Studio (when acquired) will be used for Phase 3 ML/embedding
computations only — it is not a development or pipeline machine.

All machines share the same repository. Changes flow via GitHub — never
directly between machines. The workflow is: commit and push on the
working machine, pull on all other machines before starting work.

For the full development and testing cycle, see `docs/dev_workflow.md`.

---

## Commit message convention

The project follows Conventional Commits format.

Prefix / When to use:
feat: — New feature or new file (production code)
fix: — Bug fix
docs: — Documentation only
test: — Test scripts or test protocol documents
chore: — Setup, config, dependency updates
refactor: — Code restructuring without behaviour change

Examples:

    feat: Step 0.3 logger.sh complete
    fix: catch yaml.parser.ParserError in _load_yaml_file
    docs: update phase0_foundation.md Step 0.3 complete
    test: Step 0.3 logger tested and passing all platforms
    chore: add .gitignore entries for test output

For machine-specific setup work, prefix with the machine name:

    [ubuntu] chore: configure .bashrc and venv
    [oci] chore: verify TNS_ADMIN and tnsnames.ora

---

## Branch strategy

For a single-developer project, working directly on main is acceptable.
Rule: only push to main when the code works and tests pass.

When a future developer joins, adopt this minimal branch strategy:

- main — stable, tested code only
- dev/<name> — personal working branch for in-progress work
- Merge to main via pull request after tests pass on both platforms

---

## Initial setup on a new machine

Follow these steps in order when setting up the project on a new machine.

### 1. Generate SSH key for GitHub

    ssh-keygen -t ed25519 -C "your_email@example.com"
    cat ~/.ssh/id_ed25519.pub

Copy the output and add it to GitHub:
Settings → SSH and GPG keys → New SSH key

Test the connection:

    ssh -T git@github.com

Expected: Hi username! You've successfully authenticated...

### 2. Clone the repository

Ubuntu:

    mkdir -p /home/jan
    cd /home/jan
    git clone git@github.com:yourusername/project_embeddings.git

OCI:

    cd /home/opc
    git clone git@github.com:yourusername/project_embeddings.git

### 3. Set environment variables in .bashrc

Add the following to ~/.bashrc. Adjust paths for the machine.

Ubuntu:

    # Arachnet Clinical Embeddings
    export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
    export SNOMED_LOG_LEVEL="INFO"
    export LC_ALL=C.UTF-8
    export SNOMED_DB_PASSWORD=""
    export SNOMED_STAGE_DB_PASSWORD=""
    export SNOMED_ADMIN_DB_PASSWORD=""
    source /home/jan/project_embeddings/venv/bin/activate

OCI:

    # Arachnet Clinical Embeddings
    export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
    export SNOMED_LOG_LEVEL="INFO"
    export TNS_ADMIN="/path/to/tns/admin"
    export LC_ALL=C.UTF-8
    export SNOMED_DB_PASSWORD=""
    export SNOMED_STAGE_DB_PASSWORD=""
    export SNOMED_ADMIN_DB_PASSWORD=""
    source /home/opc/project_embeddings/venv/bin/activate

Apply immediately:

    source ~/.bashrc

### 4. Create and populate the virtual environment

    cd project_embeddings
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

Note: current Python version is 3.10.12. Upgrade to 3.12 is planned
before Phase 1. Use whatever python3 version is available on the
machine at setup time.

### 5. Verify the setup

    python tests/test_logger_py.py
    bash tests/test_logger_sh.sh

All tests must pass before proceeding.

### 6. Set execute permissions

    chmod +x scripts/common/logger.sh
    chmod +x tests/test_logger_sh.sh

---

## Files that must never be committed

- venv/ — virtual environment, machine-specific
- log/ — log files, machine-specific
- .env — if created, contains credentials
- env_setup.sh — if created, contains local paths or credentials
- Any file containing actual password values
- Session JSON or transcript files from Claude sessions

If you accidentally stage a sensitive file:

    git reset HEAD <filename>

If you accidentally commit a sensitive file, contact the repository
owner immediately — the commit history must be rewritten.

---

## For a new developer joining the project

1. Request repository access from Jan Mura (Arachnet Project z.s.).
2. Follow the Initial setup steps above for your machine.
3. Read in order before writing any code:
   - docs/phase0_foundation.md — phase structure and step status
   - docs/conventions.md — all coding and file conventions
   - docs/error_codes.md — exception hierarchy and exit codes
   - docs/directory_structure.md — project layout
   - docs/dev_workflow.md — development and testing cycle
4. All new code must follow the conventions in docs/conventions.md.
5. Run all tests in tests/ before pushing any code.
6. Use conventional commit messages as described above.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
=== END FILE: docs/git_workflow.md ===

