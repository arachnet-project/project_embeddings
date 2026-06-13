# ARC_FILE: config/templates/python_header.py
# path/to/filename.py
# One-line description.
# Extended explanation if needed. May span multiple lines.
# Each continuation line begins with a hash and a space.
#
# Usage:
#   from src.common.module import public_function
#   result = public_function(arg)
#
# Environment variables:
#   SNOMED_EXAMPLE — what it controls. Default: value.
#   Remove this section entirely if the module reads no env vars.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: <version>
# Last modified: YYYY-MM-DD
# --- Replace everything above with actual content before committing. ---
# --- Delete any header sections that do not apply, e.g. env vars.   ---
# =============================================================================

# --- Standard library ---

# --- Third-party (pip install required) ---

# --- Project ---

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_EXAMPLE_CONSTANT = "value"

# ---------------------------------------------------------------------------
# Internal functions
# ---------------------------------------------------------------------------

# --- _private_function ---
def _private_function(param: str) -> str:
    """One-line summary.

    Longer explanation if needed.

    Parameters
    ----------
    param : str
        Description of param.

    Returns
    -------
    str
        Description of return value.

    Raises
    ------
    SnomedConfigError
        When and why.
    """
    pass
# --- end _private_function ---

# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

# --- public_function ---
def public_function(param: str) -> str:
    """One-line summary.

    Longer explanation if needed.

    Parameters
    ----------
    param : str
        Description of param.

    Returns
    -------
    str
        Description of return value.

    Raises
    ------
    SnomedConfigError
        When and why.
    """
    pass
# --- end public_function ---
