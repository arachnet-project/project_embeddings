# Arachnet Clinical Embeddings — Coding Conventions
# docs/conventions.md
# =========================================
# Version: 1.4
# Last updated: 2026-04-20
# Applies from: Step 0.4 onward. No retrofitting of earlier files.
# Type annotations apply from _validate_mandatory_keys onward.
# No retrofitting of earlier functions.

## Python

### Indentation
Use 4 spaces. No tabs.

### String formatting
Use .format() for all string formatting. No f-strings.

### Logging calls
Use percent-style formatting in logging calls, for example:
    logger.info("Loaded %d records from %s", count, path)

### Type annotations
Add type annotations to all new function signatures from
_validate_mandatory_keys onward. Also keep type information in the
docstring Parameters and Returns sections.

Example signature:
    def load_config(config_dir: str = None) -> DictConfig:

Example with no return value:
    def _report(test_name: str, result: str, detail: str = "") -> None:

Do not retrofit type annotations to functions written before
_validate_mandatory_keys.

### Function block markers
All function definitions must be wrapped in block markers:

    # --- function_name ---
    def function_name(...):
        ...
    # --- end function_name ---

### Docstrings
All functions must have a docstring in NumPy style with at least
a one-line summary and Parameters and Returns sections where applicable.
Type information must appear in both the signature and the docstring.

Example:
    def example(path: str) -> DictConfig:
        """Load a YAML file and return a DictConfig.

        Parameters
        ----------
        path : str
            Absolute or relative path to the YAML file.

        Returns
        -------
        DictConfig
            Parsed configuration.
        """

### Imports
Standard library imports first, then third-party, then project imports.
One blank line between each group.
Use explicit imports, not wildcard imports.

### Error handling
Raise specific exception types with descriptive messages using .format().
Never raise a bare Exception.
Always chain exceptions with from exc where the original cause is relevant.

### Constants
Module-level constants in uppercase with underscores, for example:
    MANDATORY_KEYS = [...]

## File headers

Every Python file must start with a header block like this:

    # =============================================================================
    # Arachnet Clinical Embeddings — <description>
    # <path/to/file.py>
    # =============================================================================
    # Purpose:
    #   <one or two sentences>
    #
    # Usage:
    #   <example import or command>
    #
    # Author: Jan Mura
    # Version: <version>
    # =============================================================================

## YAML

Use 2-space indentation.
Use lowercase keys with underscores.
Add a comment above each section explaining its purpose.
Null values written as null, not ~.

## SQL

### File header
Every SQL file must start with a header block like this:

    -- =============================================================================
    -- Arachnet Clinical Embeddings — <description>
    -- <path/to/file.sql>
    -- =============================================================================
    -- Purpose:
    --   <one or two sentences>
    --
    -- Run as:  <role or user, e.g. SYSDBA, snomed, snomed_stage>
    -- Prereqs: <files that must have been run first, or "none">
    --
    -- Author: Jan Mura
    -- Version: <version>
    -- Last modified: <YYYY-MM-DD>
    -- =============================================================================

### Indentation
Use 4 spaces. No tabs.

### Keywords
Write all SQL keywords in uppercase: CREATE, TABLE, GRANT, ALTER, SELECT.
Write all Oracle built-in functions in uppercase: NVL, TO_DATE, SUBSTR.
Write schema names, table names, column names, and constraint names
in lowercase with underscores.

### Naming
Table names: lowercase with underscores, prefixed sct_ for SNOMED tables.
Column names: lowercase with underscores.
Constraint names: follow pattern <type>_<table>_<column(s)>,
  for example: pk_sct_concept_id, fk_sct_description_concept_id,
  idx_sct_concept_active.
Tablespace names: uppercase with underscores, prefixed TBS_,
  for example TBS_SNOMED, TBS_SNOMED_STAGE.
Profile names: uppercase with underscores,
  for example NO_EXPIRY_PROFILE.

### Comments
Use -- for all comments. No block comments.
Add a section comment above each logical group of statements.
Add an inline comment on the same line for any non-obvious clause.

### Statement termination
End every statement with a semicolon on its own line or at the end
of the last clause. No slash (/) terminator except in SQLPlus scripts
where required for PL/SQL blocks.

### Passwords in SQL files
Never store real passwords in SQL files.
Use the placeholder CHANGEME_BEFORE_USE for any CREATE USER statement.
Add a prominent comment warning the operator to change it immediately.

## Bash

Use set -euo pipefail at the top of every script.
Use lowercase variable names with underscores for local variables.
Use uppercase for environment variables.
Quote all variable expansions: "${variable}".

## Git

See docs/git_workflow.md for commit message format and branching rules.

## Testing

Test files use plain python with _report and _summarise pattern.
Run with: python tests/test_<name>_rN_py.py
No pytest. No conftest.py.
Per-round files named: test_<name>_rN_py.py where N is the round number.
Orchestrator file named: test_<name>_py.py, written after all rounds pass.
