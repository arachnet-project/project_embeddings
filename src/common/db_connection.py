# =============================================================================
# Arachnet Clinical Terminology Embeddings — Oracle database connection
# src/common/db_connection.py
# =============================================================================
# Purpose:
#   All Oracle database communication goes through this module exclusively.
#   No other module imports oracledb directly.
#
#   Supports three schemas:
#     snomed       — active, validated SNOMED CT data (production)
#     snomed_stage — ingestion and validation target (stage)
#     sys          — DBA-level operations, setup only (AS SYSDBA)
#
#   Schema names in code match Oracle usernames exactly.
#   No mapping or translation layer needed.
#
#   Uses oracledb thin mode only. No Oracle client installation needed.
#   Credentials are never stored in cfg — only the environment variable
#   names are in cfg. Actual values are read from the environment at
#   connection time.
#
# Usage:
#   from src.common.db_connection import open_connection, test_connection
#
#   with open_connection(cfg, "snomed") as conn:
#       execute_batch(conn, sql, data, batch_size)
#       conn.commit()
#
# Author:  Jan Mura
# Version: 1.1
# =============================================================================

# --- Standard library ---
import os
import time
from collections.abc import Generator
from contextlib import contextmanager

# --- Third-party (pip install required) ---
import oracledb
from omegaconf import DictConfig

# --- Project ---
from src.common.exceptions import (
    SnomedConfigError,
    SnomedDBConnectionError,
    SnomedDDLError,
    SnomedLoadError,
)
from src.common.logger import get_logger

# =============================================================================
# Module-level constants
# =============================================================================

# Schema names match Oracle usernames exactly.
# snomed       — production schema, normal ingestion and query operations
# snomed_stage — stage schema, ingestion target before validation and swap
# sys          — SYSDBA, used only for DDL setup (tablespaces, grants, etc.)
_VALID_SCHEMAS = ("snomed", "snomed_stage", "sys")

# Seconds to wait before retrying a failed connection attempt.
_RETRY_WAIT_SECONDS = 2

# Maximum characters of a DDL statement to log at DEBUG level.
# Long CREATE TABLE statements are truncated to keep logs readable.
_DDL_LOG_MAX_LENGTH = 200

# =============================================================================
# Module-level logger
# =============================================================================

_logger = get_logger(__name__)

# =============================================================================
# Private helpers
# =============================================================================

# --- _get_credentials ---
def _get_credentials(cfg: DictConfig, schema: str) -> tuple:
    """Resolve Oracle credentials for the requested schema.

    Reads the environment variable names from cfg, then fetches the actual
    password from the environment. The TNS alias is read directly from cfg
    as a plain value — it is not a secret.

    The password value is never logged or stored beyond the return value
    of this function.

    Parameters
    ----------
    cfg : DictConfig
        Fully loaded project configuration. Relevant paths:
            cfg.database.tns_alias
            cfg.database.snomed.user
            cfg.database.snomed.password_env_var
            cfg.database.snomed_stage.user
            cfg.database.snomed_stage.password_env_var
            cfg.database.sys.user
            cfg.database.sys.password_env_var
    schema : str
        One of "snomed", "snomed_stage", "sys".

    Returns
    -------
    tuple
        (username, password, tns_alias) — all plain strings.

    Raises
    ------
    SnomedConfigError
        If schema is not one of the valid values, or if a required
        configuration key is missing or null.
    SnomedDBConnectionError
        If the password environment variable is not set or is empty.
    """
    if schema not in _VALID_SCHEMAS:
        raise SnomedConfigError(
            "Unknown schema {!r}.".format(schema),
            "valid_schemas={} hint=check caller".format(
                ", ".join(_VALID_SCHEMAS)
            ),
        )

    try:
        db_cfg           = cfg.database[schema]
        username         = db_cfg.user
        password_env_var = db_cfg.password_env_var
        tns_alias        = cfg.database.tns_alias
    except Exception as exc:
        raise SnomedConfigError(
            "Missing configuration for schema {!r}.".format(schema),
            "cfg_path=database.{} error={} hint=check database.yaml".format(
                schema, exc
            ),
        ) from exc

    if not username:
        raise SnomedConfigError(
            "Username is empty for schema {!r}.".format(schema),
            "cfg_path=database.{}.user".format(schema),
        )

    if not tns_alias:
        raise SnomedConfigError(
            "TNS alias is empty.",
            "cfg_path=database.tns_alias hint=check database.yaml",
        )

    password = os.environ.get(password_env_var, "")
    if not password:
        raise SnomedDBConnectionError(
            "Password environment variable not set or empty.",
            "schema={} env_var={} hint=check ~/.bashrc".format(
                schema, password_env_var
            ),
        )

    _logger.debug(
        "Credentials resolved: schema=%r user=%r tns_alias=%r",
        schema, username, tns_alias,
    )

    return username, password, tns_alias
# --- end _get_credentials ---


# =============================================================================
# Public functions
# =============================================================================

# --- get_connection ---
def get_connection(cfg: DictConfig, schema: str) -> oracledb.Connection:
    """Open and return a direct Oracle database connection.

    Resolves credentials via _get_credentials, then connects using
    oracledb in thin mode. Retries once after _RETRY_WAIT_SECONDS if
    the first attempt fails.

    When schema is "sys", connects AS SYSDBA. For all other schemas,
    connects as a normal user. The caller does not need to know this
    distinction.

    autocommit is always False. The caller is responsible for
    commit and rollback.

    Parameters
    ----------
    cfg : DictConfig
        Fully loaded project configuration.
    schema : str
        One of "snomed", "snomed_stage", "sys".

    Returns
    -------
    oracledb.Connection
        Open database connection. The caller must close it when done,
        or use open_connection() which closes it automatically.

    Raises
    ------
    SnomedConfigError
        If credentials cannot be resolved from cfg.
    SnomedDBConnectionError
        If the connection fails after one retry.
    """
    username, password, tns_alias = _get_credentials(cfg, schema)

    # Build connection arguments as a dict so we can conditionally
    # add mode=AUTH_MODE_SYSDBA for sys without duplicating the call.
    connect_kwargs = {
        "user":       username,
        "password":   password,
        "dsn":        tns_alias,
        "autocommit": False,
    }

    if schema == "sys":
        connect_kwargs["mode"] = oracledb.AUTH_MODE_SYSDBA

    _logger.debug(
        "Connecting to Oracle: schema=%r user=%r dsn=%r sysdba=%r",
        schema, username, tns_alias, schema == "sys",
    )

    last_exc = None
    for attempt in (1, 2):
        try:
            conn = oracledb.connect(**connect_kwargs)
            _logger.info(
                "Connected to Oracle: schema=%r user=%r dsn=%r attempt=%d",
                schema, username, tns_alias, attempt,
            )
            return conn
        except oracledb.DatabaseError as exc:
            last_exc = exc
            _logger.warning(
                "Connection attempt %d failed: schema=%r error=%s",
                attempt, schema, exc,
            )
            if attempt == 1:
                _logger.debug(
                    "Waiting %d seconds before retry.",
                    _RETRY_WAIT_SECONDS,
                )
                time.sleep(_RETRY_WAIT_SECONDS)

    raise SnomedDBConnectionError(
        "Failed to connect to Oracle after 2 attempts.",
        "schema={} user={} dsn={} error={}".format(
            schema, username, tns_alias, last_exc
        ),
    )
# --- end get_connection ---


# --- open_connection ---
@contextmanager
def open_connection(
    cfg: DictConfig,
    schema: str,
) -> Generator[oracledb.Connection, None, None]:
    """Open an Oracle connection and guarantee it is closed on exit.

    A @contextmanager wrapper around get_connection(). Intended as the
    standard way to obtain a connection throughout the project. Direct
    use of get_connection() is permitted only when a context manager is
    not appropriate.

    The caller is responsible for commit and rollback within the block.
    The connection is always closed on exit, whether the block succeeds
    or raises an exception.

    Parameters
    ----------
    cfg : DictConfig
        Fully loaded project configuration.
    schema : str
        One of "snomed", "snomed_stage", "sys".

    Yields
    ------
    oracledb.Connection
        Open database connection.

    Raises
    ------
    SnomedConfigError
        If credentials cannot be resolved from cfg.
    SnomedDBConnectionError
        If the connection fails after one retry.
    """
    conn = get_connection(cfg, schema)
    try:
        yield conn
    finally:
        conn.close()
        _logger.debug(
            "Connection closed: schema=%r", schema,
        )
# --- end open_connection ---
