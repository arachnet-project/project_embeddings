# ARC_FILE: src/common/read_required_dirs.py
# =============================================================================
# Arachnet Clinical Embeddings — Print required directories from YAML
# =============================================================================
# Purpose:
#   Reads config/directory_structure.yaml and prints each entry under
#   required_directories, one per line, to stdout. Used by
#   scripts/bootstrap.sh to check and create required directories.
#
#   Output protocol: bootstrap.sh reads each line as a relative
#   directory path, joins it onto PROJECT_ROOT, and may create it with
#   mkdir -p. Each entry must therefore be a relative path (no leading
#   "/"), contain no ".." or "." or empty path component, and contain
#   no ASCII control character (including NUL, which bash command
#   substitution silently drops, and CR/LF, which would corrupt the
#   line-based protocol). Validation here is a first line of defense;
#   bootstrap.sh performs its own independent checks as well (defense
#   in depth).
#
# Usage:
#   python3 src/common/read_required_dirs.py
#   python3 src/common/read_required_dirs.py --config PATH
#
#   The --config option is for test isolation only. bootstrap.sh always
#   calls this script with no arguments and relies on the production
#   default below.
#
# Target platforms: Oracle Linux 9, Ubuntu. Unix/Linux only.
# Author:  Jan Mura
# Version: 2.0
# Last modified: 2026-09-02
# =============================================================================
# --- Standard library ---
import argparse
import sys
from pathlib import Path

# --- Third-party (pip install required) ---
import yaml

# =============================================================================
# Module-level constants
# =============================================================================
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config" / "directory_structure.yaml"


class RequiredDirsError(Exception):
    """Raised when the required-directories registry cannot be loaded
    or fails validation. The message is safe to print to stderr."""


# --- load_registry ---
def load_registry(config_path: Path) -> object:
    """Read and parse the YAML registry file at config_path.

    Returns whatever value the YAML document contains at its top
    level; the caller is responsible for validating its shape.

    Raises RequiredDirsError with a concise message on any failure:
    missing file, unreadable file, invalid UTF-8, or malformed YAML.
    """
    if not config_path.exists():
        raise RequiredDirsError(
            "file not found: {}".format(config_path)
        )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise RequiredDirsError(
            "failed to parse {}: {}".format(config_path, exc)
        ) from exc
    except UnicodeDecodeError as exc:
        raise RequiredDirsError(
            "invalid UTF-8 in {}: {}".format(config_path, exc)
        ) from exc
    except OSError as exc:
        raise RequiredDirsError(
            "failed to read {}: {}".format(config_path, exc.strerror or exc)
        ) from exc
    return data
# --- end load_registry ---


# --- _is_safe_relative_path ---
def _is_safe_relative_path(value: str) -> bool:
    """Return True if value is a safe relative directory path: no
    leading slash, and no "..", "." or empty component. Splits on the
    literal string rather than using PurePosixPath, which silently
    normalizes away empty and "." components before they can be
    inspected.
    """
    if value.startswith("/"):
        return False
    parts = value.split("/")
    return all(part not in ("", ".", "..") for part in parts)
# --- end _is_safe_relative_path ---


# --- _contains_control_char ---
def _contains_control_char(value: str) -> bool:
    """Return True if value contains any ASCII control character
    (0x00-0x1F) or DEL (0x7F), including NUL, CR, and LF."""
    return any(ord(ch) < 32 or ord(ch) == 127 for ch in value)
# --- end _contains_control_char ---


# --- validate_registry ---
def validate_registry(data: object, config_path: Path) -> list[str]:
    """Validate the parsed registry and return a list of directory
    path strings.

    Raises RequiredDirsError describing the first problem found. The
    complete registry is validated before any entry is returned, so
    callers never receive a partially valid list.
    """
    if not isinstance(data, dict) or "required_directories" not in data:
        raise RequiredDirsError(
            "'required_directories' key not found in {}".format(config_path)
        )

    dirs = data["required_directories"]
    if not isinstance(dirs, list) or len(dirs) == 0:
        raise RequiredDirsError(
            "'required_directories' is not a non-empty list in {}".format(
                config_path
            )
        )

    seen = set()
    result = []

    for index, entry in enumerate(dirs, start=1):
        if not isinstance(entry, str):
            raise RequiredDirsError(
                "entry {} in {} is not a string".format(index, config_path)
            )
        if not entry:
            raise RequiredDirsError(
                "entry {} in {} is empty".format(index, config_path)
            )
        if entry != entry.strip():
            raise RequiredDirsError(
                "entry {} in {} has leading or trailing whitespace"
                .format(index, config_path)
            )
        if _contains_control_char(entry):
            raise RequiredDirsError(
                "entry {} in {} contains a control character, which is "
                "unsafe for the line-based protocol".format(
                    index, config_path
                )
            )
        if not _is_safe_relative_path(entry):
            raise RequiredDirsError(
                "entry {} in {}: '{}' is not a safe relative directory "
                "path (must not be absolute, and must not contain '..', "
                "'.', or empty components)".format(index, config_path, entry)
            )
        if entry in seen:
            raise RequiredDirsError(
                "duplicate directory entry '{}' in {}".format(
                    entry, config_path
                )
            )
        seen.add(entry)

        result.append(entry)

    return result
# --- end validate_registry ---


# --- print_registry ---
def print_registry(entries: list[str]) -> None:
    """Print validated directory paths, one per line."""
    for entry in entries:
        print(entry)
# --- end print_registry ---


# --- main ---
def main() -> None:
    """Parse arguments, load and validate the registry, and print it.

    Exits with code 1 and a message on stderr if the registry cannot
    be loaded or fails validation. Nothing is printed to stdout unless
    every entry validates successfully.
    """
    parser = argparse.ArgumentParser(
        description="Print required directories from the YAML registry."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=_DEFAULT_CONFIG_PATH,
        help="Path to directory_structure.yaml (default: %(default)s). "
             "For test isolation; bootstrap.sh always uses the default.",
    )
    args = parser.parse_args()

    try:
        data = load_registry(args.config)
        entries = validate_registry(data, args.config)
    except RequiredDirsError as exc:
        print("read_required_dirs: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    print_registry(entries)
# --- end main ---


if __name__ == "__main__":
    main()
