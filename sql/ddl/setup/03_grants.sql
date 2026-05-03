-- =============================================================================
-- Arachnet Clinical Embeddings — Grant privileges to application schemas
-- sql/ddl/setup/03_grants.sql
-- =============================================================================
-- Purpose:
--   Grants the minimum required privileges to the snomed and snomed_stage
--   schemas. Must be run after 02_create_schemas.sql.
--
--   Cross-schema read access: the snomed user is granted SELECT on all
--   current and future tables in snomed_stage using the Oracle 23ai/26ai
--   schema-level privilege. This single statement covers all tables that
--   exist now and any tables added to snomed_stage in the future — no
--   re-running or maintenance required.
--
-- Target:  Oracle 23ai / 26ai (OCI Base Database Service)
-- Run as:  SYSDBA
-- Prereqs: 02_create_schemas.sql
--
-- Author: Jan Mura
-- Version: 1.2
-- Last modified: 2026-05-01
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Production schema privileges
-- ---------------------------------------------------------------------------
GRANT CREATE SESSION     TO &&ORACLE_SNOMED_USER;
GRANT CREATE TABLE       TO &&ORACLE_SNOMED_USER;
GRANT CREATE VIEW        TO &&ORACLE_SNOMED_USER;
GRANT CREATE SEQUENCE    TO &&ORACLE_SNOMED_USER;
GRANT CREATE PROCEDURE   TO &&ORACLE_SNOMED_USER;

-- Tablespace quota: unlimited on the assigned tablespace, zero on SYSTEM
-- to prevent accidental writes outside the application tablespace.
ALTER USER &&ORACLE_SNOMED_USER QUOTA UNLIMITED ON TBS_SNOMED;
ALTER USER &&ORACLE_SNOMED_USER QUOTA 0         ON SYSTEM;

-- ---------------------------------------------------------------------------
-- Stage schema privileges (ingestion target — no VIEW or PROCEDURE needed)
-- ---------------------------------------------------------------------------
GRANT CREATE SESSION     TO &&ORACLE_SNOMED_STAGE_USER;
GRANT CREATE TABLE       TO &&ORACLE_SNOMED_STAGE_USER;
GRANT CREATE SEQUENCE    TO &&ORACLE_SNOMED_STAGE_USER;

ALTER USER &&ORACLE_SNOMED_STAGE_USER QUOTA UNLIMITED ON TBS_SNOMED_STAGE;
ALTER USER &&ORACLE_SNOMED_STAGE_USER QUOTA 0         ON SYSTEM;

-- ---------------------------------------------------------------------------
-- Cross-schema SELECT: snomed reads all tables in snomed_stage
--
-- Oracle 23ai/26ai schema-level privilege: one statement grants SELECT on
-- all existing tables AND any tables added to snomed_stage in the future.
-- No maintenance needed when new tables are created in snomed_stage.
-- ---------------------------------------------------------------------------
GRANT SELECT ANY TABLE ON SCHEMA &&ORACLE_SNOMED_STAGE_USER
    TO &&ORACLE_SNOMED_USER;
