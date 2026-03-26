# exceptions.py
# Project-specific exception hierarchy for Arachnet Clinical Embeddings.
# All project exceptions inherit from SnomedBaseError.
# Each exception class carries its exit code as a class attribute (exit_code).
# Bash wrappers retrieve the exit code via the Python exit() call — see
# error_codes.md for the full exit code reference and usage conventions.
#
# Usage from Python:
#   from src.common.exceptions import SnomedConfigError
#   raise SnomedConfigError("project.yaml", "project.data_release")
#
# Usage from Bash (via run.sh):
#   The orchestrator catches non-zero exit codes and maps them to log messages.
#   Exit codes are defined as class attributes and documented in error_codes.md.
#
# Convention: fail fast, fail loudly.
#   - Never catch and suppress a SnomedBaseError subclass silently.
#   - A bare except: pass is forbidden anywhere in the project.
#   - finally blocks for resource cleanup are permitted — exceptions must
#     still propagate after cleanup.
#
# Last modified: 2026-03-26


class SnomedBaseError(Exception):
    """
    Base class for all Arachnet Clinical Embeddings project exceptions.

    Attributes:
        exit_code (int): The process exit code this exception maps to.
                         Used by the Bash orchestrator to log and propagate
                         failures correctly.
        message (str):   Human-readable error description.
        detail (str):    Optional additional context — file names, key names,
                         SQL statements, table names, etc. Never contains
                         credential values.
    """

    exit_code: int = 1  # Default — overridden in all subclasses

    def __init__(self, message: str, detail: str = ""):
        self.message = message
        self.detail = detail
        full_message = f"{message} | {detail}" if detail else message
        super().__init__(full_message)

    def __str__(self) -> str:
        if self.detail:
            return f"[exit {self.exit_code}] {self.message} | {self.detail}"
        return f"[exit {self.exit_code}] {self.message}"


class SnomedConfigError(SnomedBaseError):
    """
    Raised when configuration loading or validation fails.
    Exit code: 1

    Covers:
      - Missing mandatory key in a YAML file
      - YAML parse error (malformed file)
      - OmegaConf interpolation resolution failure
      - Type mismatch (e.g. string where integer expected)
      - Unresolvable active_environment value

    Args:
        message (str): Description of the configuration problem.
        detail (str):  Identifying information — file name, key name, line
                       number, or interpolation path. Never a credential value.

    Example:
        raise SnomedConfigError(
            "Missing mandatory key",
            "file=project.yaml key=project.data_release"
        )
    """

    exit_code: int = 1


class SnomedDBConnectionError(SnomedBaseError):
    """
    Raised when a database connection cannot be established or a credential
    cannot be resolved.
    Exit code: 2

    Covers:
      - TNS resolution failure
      - Authentication failure
      - Network timeout reaching the database
      - Missing or empty password environment variable
      - Connection pool initialisation failure

    Args:
        message (str): Description of the connection problem.
        detail (str):  Schema name, TNS alias, Oracle error code. Never
                       contains credential values — not in logs, not in
                       exception detail, not anywhere.

    Example:
        raise SnomedDBConnectionError(
            "Failed to connect after 1 retry",
            "schema=snomed tns_alias=ARADB ORA-12541"
        )
    """

    exit_code: int = 2


class SnomedDDLError(SnomedBaseError):
    """
    Raised when a DDL statement (CREATE, DROP, ALTER, RENAME) fails.
    Exit code: 3

    Covers:
      - Table or schema creation failure
      - Schema rename failure during stage-to-production swap
      - Tablespace not found
      - Insufficient privileges for DDL

    Args:
        message (str): Description of the DDL failure.
        detail (str):  The SQL statement that failed and the Oracle error code.
                       Truncate very long statements to a readable summary.

    Example:
        raise SnomedDDLError(
            "Schema rename failed during swap",
            "sql='ALTER SESSION SET...' ORA-01031"
        )
    """

    exit_code: int = 3


class SnomedLoadError(SnomedBaseError):
    """
    Raised when a data load operation fails.
    Exit code: 4

    Covers:
      - executemany() batch insert failure
      - RF2 file not found or unreadable
      - RF2 file encoding error
      - Row count mismatch between RF2 source and loaded table
      - Truncate failure before load

    When raised from a batch insert failure, the transaction for the
    affected table is rolled back before this exception is raised.
    The batch number and table name must be included in detail so
    that partial load state can be diagnosed from the logs.

    Args:
        message (str): Description of the load failure.
        detail (str):  Table name, batch number, RF2 file path, or Oracle
                       error code as appropriate.

    Example:
        raise SnomedLoadError(
            "Batch insert failed — transaction rolled back",
            "table=sct_relationship batch=47 ORA-01400"
        )
    """

    exit_code: int = 4


class SnomedValidationError(SnomedBaseError):
    """
    Raised when a blocking validation check fails before the
    stage-to-production schema swap.
    Exit code: 5

    Covers:
      - RF2-to-table row count mismatch (primary completeness check)
      - Minimum row count floor not met (secondary backstop)
      - Unexpected empty table
      - Not all tables loaded in this run
      - Referential integrity violation (when promoted to blocking)

    The swap is never performed if this exception is raised.
    The stage schema is left intact for inspection and diagnosis.

    Args:
        message (str): Description of the validation failure.
        detail (str):  Check name, table name, expected vs actual counts,
                       or integrity rule that failed.

    Example:
        raise SnomedValidationError(
            "Row count mismatch — swap refused",
            "table=sct_concept rf2_rows=371432 loaded_rows=371001"
        )
    """

    exit_code: int = 5
