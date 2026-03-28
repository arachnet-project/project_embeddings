# Git Workflow — Arachnet Clinical Embeddings

**Document version:** 1.1
**Date:** 2026-03-28

---

## Overview

The project uses Git with GitHub as the remote repository, accessed via
SSH on all machines. Two machines are in active use for development and
production:

| Machine | Role | OS |
|---------|------|----|
| MacBook Air Intel | Dev primary | Ubuntu |
| OCI Frankfurt VM | Production | Oracle Linux 9 |

Mac Studio (when acquired) will be used for Phase 3 ML/embedding
computations only — it is not a development or pipeline machine.

All machines share the same repository. Changes flow via GitHub — never
directly between machines. The workflow is: commit and push on the
working machine, pull on all other machines before starting work.

The project targets Unix/Linux only. Oracle Linux 9 is the primary
production platform.

---

## Daily workflow

### Starting work on any machine

Always pull before making any changes:

```bash
cd project_embeddings
git pull
```

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

The project follows Conventional Commits format.

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
fix: remove LC_ALL from logger.sh sourced library
docs: update phase0_foundation.md Step 0.3 complete
test: Step 0.3 logger tested and passing all platforms
chore: add .gitignore entries for test output
```

For machine-specific setup work, prefix with the machine name:
```
[ubuntu] chore: configure .bashrc and venv
[oci] chore: verify TNS_ADMIN and tnsnames.ora
```

---

## Branch strategy

For a single-developer project, working directly on `main` is acceptable.
Rule: only push to `main` when the code works and tests pass.

When a future developer joins, adopt this minimal branch strategy:

- `main` — stable, tested code only
- `dev/<name>` — personal working branch for in-progress work
- Merge to `main` via pull request after tests pass on both platforms

---

## Initial setup on a new machine

Follow these steps in order when setting up the project on a new machine.

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

Expected: `Hi username! You've successfully authenticated...`

### 2. Clone the repository

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

**Ubuntu:**
```bash
# Arachnet Clinical Embeddings
export SNOMED_LOG_DIR="/home/jan/project_embeddings/log"
export SNOMED_LOG_LEVEL="INFO"

# Locale — English system messages, UTF-8 encoding
export LC_ALL=C.UTF-8

# Database passwords — set these manually, never commit to Git
export SNOMED_DB_PASSWORD=""
export SNOMED_STAGE_DB_PASSWORD=""
export SNOMED_ADMIN_DB_PASSWORD=""           # setup only

# Activate virtual environment automatically
source /home/jan/project_embeddings/venv/bin/activate
```

**OCI:**
```bash
# Arachnet Clinical Embeddings
export SNOMED_LOG_DIR="/home/opc/project_embeddings/log"
export SNOMED_LOG_LEVEL="INFO"
export TNS_ADMIN="/path/to/tns/admin"

# Locale — English system messages, UTF-8 encoding
export LC_ALL=C.UTF-8

# Database passwords — set these manually, never commit to Git
export SNOMED_DB_PASSWORD=""
export SNOMED_STAGE_DB_PASSWORD=""
export SNOMED_ADMIN_DB_PASSWORD=""           # setup only

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

```bash
SNOMED_LOG_LEVEL=DEBUG bash tests/test_logger.sh
```

All pass criteria in `docs/test_logger_protocol.md` must be met before
proceeding.

### 6. Set execute permissions

```bash
chmod +x scripts/common/logger.sh
chmod +x tests/test_logger.sh
```

---

## Files that must never be committed

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
owner immediately — the commit history must be rewritten.

---

## For a new developer joining the project

1. Request repository access from Jan Mura (Arachnet Project z.s.).
2. Follow the Initial setup steps above for your machine.
3. Read in order before writing any code:
   - `docs/phase0_foundation.md`
   - `docs/error_codes.md`
   - `docs/directory_structure.md`
4. All new code must follow the conventions in `docs/phase0_foundation.md`:
   - Use `get_logger(__name__)` from `src/common/logger.py`
   - Raise only `SnomedBaseError` subclasses from `src/common/exceptions.py`
   - Begin all Bash scripts with `set -euo pipefail`
   - Set `export LC_ALL=C.UTF-8` at the top of every executable Bash script
   - Never store credentials in code or config files
5. Run all tests in `tests/` before pushing any code.
6. Use conventional commit messages as described above.

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
