-- =============================================================================
-- Arachnet Clinical Embeddings — Create tablespaces
-- sql/ddl/setup/01_create_tablespaces.sql
-- =============================================================================
-- Purpose:
--   Creates the permanent tablespaces required by the production and stage
--   application schemas. Must be run before 02_create_schemas.sql.
--
-- Run as:  SYSDBA
-- Prereqs: none
--
-- Author: Jan Mura
-- Version: 1.1
-- Last modified: 2026-04-20
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Production tablespace — holds active validated SNOMED CT data
-- ---------------------------------------------------------------------------
CREATE TABLESPACE TBS_SNOMED
    DATAFILE SIZE 1G
    AUTOEXTEND ON NEXT 512M
    MAXSIZE UNLIMITED;

-- ---------------------------------------------------------------------------
-- Stage tablespace — holds in-progress ingestion data before swap
-- ---------------------------------------------------------------------------
CREATE TABLESPACE TBS_SNOMED_STAGE
    DATAFILE SIZE 1G
    AUTOEXTEND ON NEXT 512M
    MAXSIZE UNLIMITED;
