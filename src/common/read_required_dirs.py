# ARC_FILE: src/common/read_required_dirs.py
# src/common/read_required_dirs.py
# =============================================================================
# Arachnet Clinical Embeddings — Print required directories from YAML
# =============================================================================
# Purpose:
#   Reads config/directory_structure.yaml and prints each entry under
#   required_directories on its own line to stdout. Used by
#   scripts/bootstrap.sh to check and create required directories.
#
# Usage:
#   python3 src/common/read_required_dirs.py
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 1.0
# Last modified: 2026-06-08
# =============================================================================

# --- Standard library ---
import sys
from pathlib import Path

# --- Third-party (pip install required) ---
import yaml

# =============================================================================
# Module-level constants
# =============================================================================

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config" / "directory_structure.yaml"


# --- main ---
def main() -> None:
    """Print required directories, one per line, to stdout.

    Reads config/directory_structure.yaml relative to the project root
    and prints each entry under required_directories.

    Exits with code 1 and a message on stderr if the file is missing,
    cannot be parsed, or does not contain required_directories.
    """
    if not _CONFIG_PATH.exists():
        print(
            "read_required_dirs: file not found: {}".format(_CONFIG_PATH),
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(_CONFIG_PATH, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(
            "read_required_dirs: failed to parse {}: {}".format(
                _CONFIG_PATH, exc
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    if not isinstance(data, dict) or "required_directories" not in data:
        print(
            "read_required_dirs: 'required_directories' key not found "
            "in {}".format(_CONFIG_PATH),
            file=sys.stderr,
        )
        sys.exit(1)

    dirs = data["required_directories"]
    if not isinstance(dirs, list):
        print(
            "read_required_dirs: 'required_directories' is not a list "
            "in {}".format(_CONFIG_PATH),
            file=sys.stderr,
        )
        sys.exit(1)

    for d in dirs:
        print(d)
# --- end main ---


if __name__ == "__main__":
    main()
