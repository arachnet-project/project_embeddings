-- =============================================================================
-- Arachnet Clinical Embeddings — Create application schemas
-- sql/ddl/setup/02_create_schemas.sql
-- =============================================================================
-- Purpose:
--   Creates the snomed and snomed_stage Oracle users with correct tablespace
--   assignments and the NO_EXPIRY_PROFILE password profile.
--   Must be run after 01_create_tablespaces.sql.
--
--   Passwords and user names are supplied via SQL*Plus substitution variables
--   sourced from environment variables. Set these in your shell (e.g. .bashrc)
--   before running:
--
--     export ORACLE_SNOMED_USER="SNOMED"
--     export ORACLE_SNOMED_PASSWORD=""          # fill in .bashrc
--     export ORACLE_SNOMED_STAGE_USER="SNOMED_STAGE"
--     export ORACLE_SNOMED_STAGE_PASSWORD=""    # fill in .bashrc
--
--   Use the provided run_setup.sh wrapper which injects these into SQL*Plus.
--   Never commit real passwords to version control.
--
-- Target:  Oracle 23ai / 26ai (OCI Base Database Service)
-- Run as:  SYSDBA
-- Prereqs: 01_create_tablespaces.sql
--          NO_EXPIRY_PROFILE must exist (run 00_create_profile.sql on fresh
--          instances; skip on OCI where the profile already exists).
--
-- Author: Jan Mura
-- Version: 1.2
-- Last modified: 2026-05-01
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Production schema — active, validated SNOMED CT data
-- ---------------------------------------------------------------------------
CREATE USER &&ORACLE_SNOMED_USER
    IDENTIFIED BY "&&ORACLE_SNOMED_PASSWORD"
    DEFAULT TABLESPACE TBS_SNOMED
    TEMPORARY TABLESPACE TEMP
    PROFILE NO_EXPIRY_PROFILE;

-- ---------------------------------------------------------------------------
-- Stage schema — ingestion and validation target before production swap
-- ---------------------------------------------------------------------------
CREATE USER &&ORACLE_SNOMED_STAGE_USER
    IDENTIFIED BY "&&ORACLE_SNOMED_STAGE_PASSWORD"
    DEFAULT TABLESPACE TBS_SNOMED_STAGE
    TEMPORARY TABLESPACE TEMP
    PROFILE NO_EXPIRY_PROFILE;
