# Git Workflow — Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-03-28

---

## Overview

The project uses Git with GitHub as the remote repository, accessed via
SSH on all machines. Three machines are in active use:

| Machine | Role | OS |
|---------|------|----|
| MacBook Pro M1 | Dev primary (transitioning to secondary) | macOS |
| MacBook Air Intel | Dev secondary (becoming primary) | Ubuntu |
| OCI Frankfurt VM | Production | Oracle Linux 9 |

All machines share the same repository. Changes flow via GitHub — never
directly between machines. The workflow is: commit and push on the working
machine, pull on all other machines before starting work.

---

## Daily workflow

### Starting work on any machine

Always pull before making any changes:

```bash
cd project_embeddings
git pull
```

This ensures you are working on the latest version from all machines.

### After finishing work

```bash
git add .
git commit -m "descriptive commit message"
git push
```

### On all other machines after a push

```bash
cd project_embeddings
git pull
```

---

## Commit message convention

The project follows Conventional Commits format. This makes the history
readable and supports future automation.

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or new file (production code) |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `test:` | Test scripts or test protocol documents |
| `chore:` | Setup, config, dependency updates |
| `refactor:` | Code restructuring without behaviour change |

Examples:
```
feat: Step 0.3 logger.sh complete
fix: correct logger.sh path in test_logger.sh
docs: update phase0_foundation.md Step 0.3 complete
test: Step 0.3 logger tested and passing all platforms
chore: add .gitignore entries for test output
```

For infrastructure or setup work specific to one machine, prefix with
the machine name in brackets before the conventional prefix:

```
[ubuntu] chore: configure .bashrc and venv
[oci] chore: verify TNS_ADMIN and tnsnames.ora
[macos] fix: update SNOMED_LOG_DIR path in .bashrc
```

---

## Branch strategy

For a single-developer project, working directly on `main` is acceptable.
When a future developer joins, adopt this minimal branch strategy:

- `main` — stable, tested code only. Never commit broken code here.
- `dev/<your-name>` — personal working branch for in-progress work.
- Merge to `main` via pull request after testing passes on all platforms.

Until a second developer joins, commit directly to `main` but follow
the rule: only push to `main` when the code works and tests pass.

---

## Initial setup on a new machine

Follow these steps in order when setting up the project on a new machine
for the first time.

### 1. Generate SSH key for GitHub

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

Copy the output and add it to GitHub:
Settings → SSH and GPG keys → New SSH key

Test the connection:
```bash
ssh -T git@github.com
```

Expected response: `Hi username! You've successfully authenticated...`

### 2. Clone the repository

**macOS:**
```bash
mkdir -p /Users/jan/arachnet/snomed
cd /Users/jan/arachnet/snomed
git clone git@github.com:yourusername/project_embeddings.git
```

**Ubuntu:**
```bash
mkdir -p /home/jan
cd /home/jan
git clone git@github.com:yourusername/project_embeddings.git
```

**OCI:**
```bash
cd /home/opc
git clone git@github.com:yourusername/project_embeddings.git
```

### 3. Set environment variables in `.bashrc`

Add the following to `~/.bashrc`. Adjust paths for the machine.

**macOS:**
```bash
# Arachnet Clinical Embeddings
export SNOMED_LOG_DIR="/Users/jan/arachnet/snomed/project_embeddings/log"
export SNOMED_LOG_LEVEL="INFO"
export TNS_ADMIN="/path/to/tns/admin"        # OCI only — skip on dev machines

# Database passwords — set these manually, never commit to Git
export SNOMED_DB_PASSWORD=""
export SNOMED_STAGE_DB_PASSWORD=""
export SNOMED_ADMIN_DB_PASSWORD=""           # Setup only

# Activate virtual environment automatically
source /Users/jan/arachnet/snomed/project_embeddings/venv/bin/activate
```

**Ubuntu:**
```bash
# Arachnet Clinical Embeddings
export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
export SNOMED_LOG_LEVEL="INFO"

# Database passwords — set these manually, never commit to Git
export SNOMED_DB_PASSWORD=""
export SNOMED_STAGE_DB_PASSWORD=""
export SNOMED_ADMIN_DB_PASSWORD=""

# Activate virtual environment automatically
source /home/jan/project_embeddings/venv/bin/activate
```

**OCI:**
```bash
# Arachnet Clinical Embeddings
export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
export SNOMED_LOG_LEVEL="INFO"
export TNS_ADMIN="/path/to/tns/admin"

# Database passwords — set these manually, never commit to Git
export SNOMED_DB_PASSWORD=""
export SNOMED_STAGE_DB_PASSWORD=""
export SNOMED_ADMIN_DB_PASSWORD=""

# Activate virtual environment automatically
source /home/opc/project_embeddings/venv/bin/activate
```

Apply immediately:
```bash
source ~/.bashrc
```

### 4. Create and populate the virtual environment

```bash
cd project_embeddings
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Verify the setup

Run the logger test to confirm the environment is working:

```bash
cd project_embeddings
SNOMED_LOG_LEVEL=DEBUG bash tests/test_logger.sh
```

All pass criteria in `docs/test_logger_protocol.md` must be met before
proceeding.

### 6. Set execute permissions on scripts

```bash
chmod +x scripts/common/logger.sh
chmod +x tests/test_logger.sh
```

---

## Files that must never be committed

The following are in `.gitignore` and must never be added to the
repository under any circumstances:

- `venv/` — virtual environment, machine-specific
- `log/` — log files, machine-specific
- `.env` — if created, contains credentials
- `env_setup.sh` — if created, contains local paths or credentials
- Any file containing actual password values

If you accidentally stage a sensitive file:
```bash
git reset HEAD <filename>
```

If you accidentally commit a sensitive file, contact the repository
owner immediately — the commit history must be rewritten to remove it.

---

## Syncing YAML config changes across machines

When a YAML config file changes (project.yaml, database.yaml,
ingestion.yaml), the change must be pulled on all machines before
running any pipeline scripts. Config changes are the most likely source
of cross-machine inconsistency.

After any config change, on each machine:
```bash
git pull
source ~/.bashrc
```

---

## For a new developer joining the project

1. Request repository access from Jan Mura (Arachnet Project z.s.).
2. Follow the Initial setup steps above for your machine.
3. Read `docs/phase0_foundation.md` before writing any code.
4. Read `docs/error_codes.md` to understand the error handling contract.
5. Read `docs/directory_structure.md` before creating any new files.
6. All new code must follow the conventions in `docs/phase0_foundation.md`:
   - Use `get_logger(__name__)` from `src/common/logger.py` for logging.
   - Raise only `SnomedBaseError` subclasses from `src/common/exceptions.py`.
   - Begin all Bash scripts with `set -euo pipefail`.
   - Never store credentials in code or config files.
7. Before pushing any code, run all tests in `tests/` and confirm they pass.
8. Use conventional commit messages as described above.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
