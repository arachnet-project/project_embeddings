# Arachnet Clinical Embeddings — Coding Conventions
# docs/conventions.md
# =========================================
# Version: 1.3
# Last updated: 2026-04-14
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
