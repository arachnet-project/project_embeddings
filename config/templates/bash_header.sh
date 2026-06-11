# ARC_FILE: config/templates/bash_header.sh
# script_name.sh
# One-line description.
# Extended explanation if needed. May span multiple lines.
# Each continuation line begins with a hash and a space.
#
# Usage:
#   bash scripts/script_name.sh
#   source scripts/common/library.sh   # for sourced libraries only
#
# Environment variables:
#   SNOMED_EXAMPLE  — what it controls. Default: value.
#   Remove this section entirely if the script reads no env vars.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Last modified: YYYY-MM-DD
# --- Replace everything above with actual content before committing. ---
# --- Delete any header sections that do not apply, e.g. env vars.   ---
# =============================================================================
set -euo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXAMPLE_CONSTANT="value"

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

# --- function_name ---
function_name() {
    # One-line summary.
    # Args:
    #   $1 — description
    # Returns:
    #   0 on success, 1 on failure
    local arg="${1}"
}
# --- end function_name ---

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# --- main ---
main() {
    # Entry point.
    :
}
# --- end main ---

main "$@"
