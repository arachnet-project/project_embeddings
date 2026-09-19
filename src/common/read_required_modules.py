# ARC_FILE: src/common/read_required_modules.py
# =============================================================================
# Arachnet Clinical Embeddings — Print required Python modules from JSON
# =============================================================================
# Purpose:
#   Reads config/required_modules.json and prints each entry under
#   required_modules to stdout, one per line, as "import_name,package_name".
#   Used by scripts/bootstrap.sh to check that required Python packages
#   are installed in the active venv.
#
#   Deliberately reads JSON, not YAML: this helper is called from
#   check_python_modules, which is the function that PROVES PyYAML is
#   installed in the first place. It cannot depend on PyYAML to read
#   its own module list without becoming circular. json is Python
#   standard library, so no such dependency exists here.
#
#   Output protocol: bootstrap.sh parses each line via
#   `IFS=',' read -r module package`, a two-field split. module is
#   never interpolated into Python source: bootstrap passes it as
#   sys.argv[1] to a fixed importlib.import_module(...) one-liner.
#   import_name is still restricted to a valid dotted Python
#   identifier here as defense in depth — a non-identifier value has
#   no legitimate use as a module name regardless of how safely it's
#   passed.
#   Neither field may contain a comma or embedded newline/carriage
#   return, since either would corrupt line-based parsing downstream.
#
# Usage:
#   python3 src/common/read_required_modules.py
#   python3 src/common/read_required_modules.py --config PATH
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
import json
import keyword
import sys
from pathlib import Path

# =============================================================================
# Module-level constants
# =============================================================================
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config" / "required_modules.json"


class RequiredModulesError(Exception):
    """Raised when the required-modules registry cannot be loaded or
    fails validation. The message is safe to print to stderr."""


# --- load_registry ---
def load_registry(config_path: Path) -> object:
    """Read and parse the JSON registry file at config_path.

    Returns whatever value the JSON document contains at its top
    level; the caller is responsible for validating its shape.

    Raises RequiredModulesError with a concise, credential-safe message
    on any failure: missing file, unreadable file, invalid UTF-8, or
    malformed JSON.
    """
    if not config_path.exists():
        raise RequiredModulesError(
            "file not found: {}".format(config_path)
        )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise RequiredModulesError(
            "failed to parse {}: {}".format(config_path, exc)
        ) from exc
    except UnicodeDecodeError as exc:
        raise RequiredModulesError(
            "invalid UTF-8 in {}: {}".format(config_path, exc)
        ) from exc
    except OSError as exc:
        raise RequiredModulesError(
            "failed to read {}: {}".format(config_path, exc.strerror or exc)
        ) from exc
    return data
# --- end load_registry ---


# --- _is_valid_dotted_identifier ---
def _is_valid_dotted_identifier(value: str) -> bool:
    """Return True if value is a valid dotted Python identifier, e.g.
    "yaml" or "package.submodule", with every component a legal
    identifier and not a reserved keyword."""
    parts = value.split(".")
    if not parts or any(not part for part in parts):
        return False
    for part in parts:
        if not part.isidentifier() or keyword.iskeyword(part):
            return False
    return True
# --- end _is_valid_dotted_identifier ---


# --- validate_registry ---
def validate_registry(data: object, config_path: Path) -> list[tuple[str, str]]:
    """Validate the parsed registry and return a list of
    (import_name, package_name) tuples.

    Raises RequiredModulesError describing the first problem found.
    The complete registry is validated before any entry is returned,
    so callers never receive a partially valid list.
    """
    if not isinstance(data, dict) or "required_modules" not in data:
        raise RequiredModulesError(
            "'required_modules' key not found in {}".format(config_path)
        )

    modules = data["required_modules"]
    if not isinstance(modules, list) or len(modules) == 0:
        raise RequiredModulesError(
            "'required_modules' is not a non-empty list in {}".format(
                config_path
            )
        )

    forbidden_chars = (",", "\n", "\r")
    seen_import_names = set()
    result = []

    for index, entry in enumerate(modules, start=1):
        if (
            not isinstance(entry, dict)
            or "import_name" not in entry
            or "package_name" not in entry
        ):
            raise RequiredModulesError(
                "entry {} in {} missing 'import_name' or "
                "'package_name'".format(index, config_path)
            )

        import_name = entry["import_name"]
        package_name = entry["package_name"]

        for label, value in (
            ("import_name", import_name),
            ("package_name", package_name),
        ):
            if not isinstance(value, str):
                raise RequiredModulesError(
                    "entry {} in {}: '{}' is not a string".format(
                        index, config_path, label
                    )
                )
            if not value:
                raise RequiredModulesError(
                    "entry {} in {}: '{}' is empty".format(
                        index, config_path, label
                    )
                )
            if value != value.strip():
                raise RequiredModulesError(
                    "entry {} in {}: '{}' has leading or trailing "
                    "whitespace".format(index, config_path, label)
                )
            if any(ch in value for ch in forbidden_chars):
                raise RequiredModulesError(
                    "entry {} in {}: '{}' contains a comma or line "
                    "break, which would corrupt the output protocol"
                    .format(index, config_path, label)
                )

        if not _is_valid_dotted_identifier(import_name):
            raise RequiredModulesError(
                "entry {} in {}: 'import_name' ({!r}) is not a valid "
                "dotted Python identifier".format(
                    index, config_path, import_name
                )
            )

        if import_name in seen_import_names:
            raise RequiredModulesError(
                "duplicate import_name '{}' in {}".format(
                    import_name, config_path
                )
            )
        seen_import_names.add(import_name)

        result.append((import_name, package_name))

    return result
# --- end validate_registry ---


# --- print_registry ---
def print_registry(entries: list[tuple[str, str]]) -> None:
    """Print validated (import_name, package_name) entries, one per
    line, as "import_name,package_name"."""
    for import_name, package_name in entries:
        print("{0},{1}".format(import_name, package_name))
# --- end print_registry ---


# --- main ---
def main() -> None:
    """Parse arguments, load and validate the registry, and print it.

    Exits with code 1 and a message on stderr if the registry cannot
    be loaded or fails validation. Nothing is printed to stdout unless
    every entry validates successfully.
    """
    parser = argparse.ArgumentParser(
        description="Print required Python modules from the JSON registry."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=_DEFAULT_CONFIG_PATH,
        help="Path to required_modules.json (default: %(default)s). "
             "For test isolation; bootstrap.sh always uses the default.",
    )
    args = parser.parse_args()

    try:
        data = load_registry(args.config)
        entries = validate_registry(data, args.config)
    except RequiredModulesError as exc:
        print("read_required_modules: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    print_registry(entries)
# --- end main ---


if __name__ == "__main__":
    main()