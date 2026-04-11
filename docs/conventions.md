# Development Conventions — Arachnet Clinical Embeddings

**Project:** Arachnet Clinical Embeddings
**Owner:** Jan Mura, Arachnet Project z.s.
**Document version:** 1.2
**Date:** 2026-04-06
**Status:** Agreed

---

## Purpose

This document defines mandatory conventions for all source files in the
Arachnet Clinical Embeddings project. Conventions apply across all phases
and all file types unless a specific exception is noted.

Every file produced from Step 0.4 onward must follow these conventions
before it is committed to the repository.

Note: Files produced before Step 0.4 (Steps 0.1 through 0.3) are not
retrofitted. They stand as written. If a pre-0.4 file is substantially
revised in a later step, conventions should be applied at that point.

---

## Python files

### Target version

Python 3.10.12 minimum. All syntax and standard library usage must be
compatible with Python 3.10. Do not use features introduced in 3.11 or
later unless explicitly noted.

### File header

Every Python file begins with a header block. The header is a contiguous
block of hash-prefixed comment lines with no blank lines between them.
The header ends with a blank line before the first import.

Required header fields in order:

1. Filename — bare filename only, no path.
2. One-line description of the module's purpose.
3. Longer explanation if needed — may span multiple comment lines.
4. Usage example — how to import and call the module's public interface.
5. Environment variables — list any env vars the module reads, with
   defaults and effect. Omit this section if the module reads no env vars.
6. Target platforms line.
7. Last modified date in ISO format YYYY-MM-DD.

Example:

    # config_loader.py
    # Configuration loader for Arachnet Clinical Embeddings.
    # Loads project.yaml, merges included files, resolves interpolation,
    # validates mandatory keys, and exposes the resolved config object.
    #
    # Usage:
    #   from src.common.config_loader import load_config
    #   cfg = load_config()
    #
    # Environment variables:
    #   SNOMED_LOG_DIR   — passed through to logger
    #   SNOMED_LOG_LEVEL — passed through to logger
    #
    # Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
    # Last modified: 2026-04-06

### Vim template

A Python header and function template is kept at:

    config/templates/python_header.py

When creating a new Python file in Vim, this template is inserted
automatically via the following autocommand in ~/.vimrc:

    autocmd BufNewFile *.py 0r /home/jan/project_embeddings/config/templates/python_header.py

After the template is inserted, fill in the filename, description,
and last modified date manually. Delete any sections that do not apply,
for example the environment variables section if the module reads none.
Replace the placeholder function stubs with real functions.

### Imports

Imports appear after the file header, separated from it by one blank line.
Three groups in order, each separated by one blank line:

1. Standard library imports, alphabetical order.
2. Third-party imports, alphabetical order.
3. Project-internal imports, alphabetical order.

Example:

    import os
    import sys
    from pathlib import Path

    from omegaconf import OmegaConf, OmegaConfBaseException

    from src.common.exceptions import SnomedConfigError
    from src.common.logger import get_logger

### Module-level constants

Constants appear after imports, separated by one blank line.

The section is introduced by a dashed comment line:

    # ---------------------------------------------------------------------------
    # Module-level constants
    # ---------------------------------------------------------------------------

Constants are UPPER_SNAKE_CASE. Module-private constants have a leading
underscore. Public constants do not.

### Section markers

All major sections within a file are introduced by a dashed comment line
of this form:

    # ---------------------------------------------------------------------------
    # Section name
    # ---------------------------------------------------------------------------

Standard section names in order of appearance:

- Module-level constants
- Internal functions (if any private helpers exist)
- Public interface

Additional sections may be added when a module's structure warrants it,
for example: Mandatory keys, CLI export, Validation.

### Function block markers

Every function definition is wrapped in block markers immediately outside
the def line. This makes functions locatable in a terminal with a screen
reader without visual scanning.

    # --- function_name ---
    def function_name(...):
        ...
    # --- end function_name ---

The marker uses the exact function name. No spaces inside the dashes
other than around the name.

### Docstrings

Every public function has a docstring. Private functions (leading
underscore) have a docstring if their behaviour is non-obvious.

Docstring format:

    """
    One-line summary.

    Longer explanation if needed.

    Args:
        param_name: Description. Type information is in the signature.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When and why this is raised.
    """

Do not repeat type information in the docstring body if it is already
in the function signature.

### String formatting

Use .format() for all string interpolation. Do not use f-strings.

Correct:
    msg = "Key {} not found in section {}.".format(key, section)

Incorrect:
    msg = f"Key {key} not found in section {section}."

### Logging calls

Use percent-style formatting in logging calls. Do not use .format()
or f-strings inside logger calls. The logging module defers string
interpolation, which avoids building the string when the message will
not be emitted at the current log level.

Correct:
    logger.info("Loading RF2 file: %s", filepath)
    logger.error("Batch insert failed: %s", detail)

Incorrect:
    logger.info("Loading RF2 file: {}".format(filepath))
    logger.info(f"Loading RF2 file: {filepath}")

### Indentation

Four spaces. No tabs.

### Exception handling

No silent exception suppression. The construct except: pass is forbidden.

finally blocks are permitted for resource cleanup. The exception must
still propagate after cleanup.

Catch the most specific exception type available. Catch broad exceptions
such as Exception only as a last resort, and always log the error before
re-raising or converting to a project exception type.

### Project exception types

Raise project-defined exceptions from src.common.exceptions rather than
built-in exceptions wherever a specific error category applies. See
docs/error_codes.md for the full hierarchy and exit codes.

---

## YAML files

### File header

Every YAML file begins with a header block of hash-prefixed comment
lines covering:

1. Filename.
2. One-line description.
3. Any important notes about how the file is used or loaded.
4. Last modified date.

### Section markers

Sections within a YAML file are introduced by a dashed comment line:

    # ---------------------------------------------------------------------------
    # Section name
    # ---------------------------------------------------------------------------

### Required keys

Keys that are mandatory for correct operation are marked with an inline
comment:

    key: value    # REQUIRED

### Metadata block

A metadata block is recommended but not required in YAML files. It is
most useful in files that are expected to evolve across releases.

If a metadata block is present, all four fields must be filled in
correctly:

    metadata:
      created_by: "Jan Mura"
      created_on: "YYYY-MM-DD"
      config_version: "1.0"
      last_modified: "YYYY-MM-DD"

Note: config_version is aspirational until the config loader validates
it. Keep it accurate regardless.

### Passwords and credentials

Never store credential values in any YAML file. Reference the name of
the environment variable that holds the credential:

    password_env_var: "SNOMED_DB_PASSWORD"    # REQUIRED

---

## Bash files

### Executable scripts

Every executable Bash script begins with:

    #!/usr/bin/env bash
    set -euo pipefail
    export LC_ALL=C.UTF-8

LC_ALL=C.UTF-8 is set in executable scripts only, not in sourced
libraries.

### Sourced libraries

Sourced Bash libraries do not set shell options or locale. They may be
sourced by scripts that have already set their own options.

### File header

Same structure as Python file headers, using hash-prefixed comment lines.

---

## General rules applying to all file types

### Line endings

Unix line endings only (LF). No CRLF.

### Trailing whitespace

No trailing whitespace on any line.

### File encoding

UTF-8 throughout.

### Last modified date

Every file header carries a last modified date. Update it whenever the
file is meaningfully changed.

