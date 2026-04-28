

=== BEGIN FILE: sql/ddl/setup/02_create_schemas.sql ===
-- =============================================================================
-- Arachnet Clinical Embeddings — Create application schemas
-- sql/ddl/setup/02_create_schemas.sql
-- =============================================================================
-- Purpose:
--   Creates the snomed and snomed_stage Oracle users with correct tablespace
--   assignments and the NO_EXPIRY_PROFILE password profile. Assigns both
--   users to NO_EXPIRY_PROFILE so passwords do not expire.
--   Must be run after 01_create_tablespaces.sql.
--
--   IMPORTANT: This file contains a placeholder password CHANGEME_BEFORE_USE.
--   Change both passwords immediately after running this script.
--   Never commit real passwords to version control.
--
-- Run as:  SYSDBA
-- Prereqs: 01_create_tablespaces.sql
--          NO_EXPIRY_PROFILE must exist (run 00_create_profile.sql on fresh
--          instances; skip on OCI where the profile already exists).
--
-- Author: Jan Mura
-- Version: 1.1
-- Last modified: 2026-04-20
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Production schema — active, validated SNOMED CT data
-- ---------------------------------------------------------------------------
CREATE USER snomed
    IDENTIFIED BY CHANGEME_BEFORE_USE   -- Change immediately after running
    DEFAULT TABLESPACE TBS_SNOMED
    TEMPORARY TABLESPACE TEMP
    PROFILE NO_EXPIRY_PROFILE;

-- ---------------------------------------------------------------------------
-- Stage schema — ingestion and validation target before production swap
-- ---------------------------------------------------------------------------
CREATE USER snomed_stage
    IDENTIFIED BY CHANGEME_BEFORE_USE   -- Change immediately after running
    DEFAULT TABLESPACE TBS_SNOMED_STAGE
    TEMPORARY TABLESPACE TEMP
    PROFILE NO_EXPIRY_PROFILE;

-- ---------------------------------------------------------------------------
-- Assign both schemas to NO_EXPIRY_PROFILE explicitly.
-- The PROFILE clause in CREATE USER above sets the profile at creation time.
-- These ALTER USER statements make the assignment visible and auditable as
-- a separate explicit step, and serve as the correct command to run if
-- accounts were created without the profile clause on an existing instance.
-- ---------------------------------------------------------------------------
ALTER USER snomed PROFILE NO_EXPIRY_PROFILE;
ALTER USER snomed_stage PROFILE NO_EXPIRY_PROFILE;
=== END FILE: sql/ddl/setup/02_create_schemas.sql ===
