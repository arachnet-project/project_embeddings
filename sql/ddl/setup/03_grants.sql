-- =============================================================================
-- Arachnet Clinical Embeddings — Grant privileges to application schemas
-- sql/ddl/setup/03_grants.sql
-- =============================================================================
-- Purpose:
--   Grants the minimum required privileges to the snomed and snomed_stage
--   schemas. Must be run after 02_create_schemas.sql.
--
-- Run as:  SYSDBA
-- Prereqs: 02_create_schemas.sql
--
-- Author: Jan Mura
-- Version: 1.0
-- Last modified: 2026-04-20
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Production schema privileges
-- ---------------------------------------------------------------------------
GRANT CONNECT TO snomed;
GRANT RESOURCE TO snomed;
GRANT CREATE SESSION TO snomed;
GRANT UNLIMITED TABLESPACE TO snomed;
GRANT CREATE TABLE TO snomed;
GRANT CREATE VIEW TO snomed;
GRANT CREATE SEQUENCE TO snomed;
GRANT CREATE PROCEDURE TO snomed;

-- ---------------------------------------------------------------------------
-- Stage schema privileges
-- ---------------------------------------------------------------------------
GRANT CONNECT TO snomed_stage;
GRANT RESOURCE TO snomed_stage;
GRANT CREATE SESSION TO snomed_stage;
GRANT UNLIMITED TABLESPACE TO snomed_stage;
GRANT CREATE TABLE TO snomed_stage;
GRANT CREATE VIEW TO snomed_stage;
GRANT CREATE SEQUENCE TO snomed_stage;
GRANT CREATE PROCEDURE TO snomed_stage;
