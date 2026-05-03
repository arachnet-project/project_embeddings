-- =============================================================================
-- Arachnet Clinical Embeddings — Create tablespaces
-- sql/ddl/setup/01_create_tablespaces.sql
-- =============================================================================
-- Purpose:
--   Creates the permanent tablespaces required by the production and stage
--   application schemas. Must be run before 02_create_schemas.sql.
--
-- Target:  Oracle 23ai / 26ai (OCI Base Database Service)
-- Run as:  SYSDBA
-- Prereqs: none
--
-- Changes v1.2:
--   - Added explicit EXTENT MANAGEMENT LOCAL AUTOALLOCATE and
--     SEGMENT SPACE MANAGEMENT AUTO clauses. Oracle defaults to these values
--     but making them explicit improves documentation clarity and avoids
--     any ambiguity when reviewing the schema on a non-default instance.
--
-- Author: Jan Mura
-- Version: 1.2
-- Last modified: 2026-05-01
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Production tablespace — holds active validated SNOMED CT data
-- ---------------------------------------------------------------------------
CREATE TABLESPACE TBS_SNOMED
    DATAFILE SIZE 1G
    AUTOEXTEND ON NEXT 512M MAXSIZE UNLIMITED
    EXTENT MANAGEMENT LOCAL AUTOALLOCATE
    SEGMENT SPACE MANAGEMENT AUTO;

-- ---------------------------------------------------------------------------
-- Stage tablespace — holds in-progress ingestion data before swap
-- ---------------------------------------------------------------------------
CREATE TABLESPACE TBS_SNOMED_STAGE
    DATAFILE SIZE 1G
    AUTOEXTEND ON NEXT 512M MAXSIZE UNLIMITED
    EXTENT MANAGEMENT LOCAL AUTOALLOCATE
    SEGMENT SPACE MANAGEMENT AUTO;
