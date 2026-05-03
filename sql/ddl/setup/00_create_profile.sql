-- =============================================================================
-- Arachnet Clinical Embeddings — Create non-expiry profile
-- sql/ddl/setup/00_create_profile.sql
-- =============================================================================
-- Purpose:
--   Creates the NO_EXPIRY_PROFILE Oracle profile used by application schemas.
--   Run this file only on a fresh database instance where NO_EXPIRY_PROFILE
--   does not already exist.
--
--   On the production OCI instance this profile was created manually during
--   initial database setup and SYS and SYSTEM were assigned to it at that
--   time. Skip this file on any instance where NO_EXPIRY_PROFILE already
--   exists.
--
-- Target:  Oracle 23ai / 26ai (OCI Base Database Service)
-- Run as:  SYSDBA
-- Prereqs: none
--
-- Changes v1.2:
--   - FAILED_LOGIN_ATTEMPTS changed from UNLIMITED to 10 — unlimited gave no
--     protection against brute force from a compromised internal host.
--   - PASSWORD_LOCK_TIME set to 1/24 (1 hour) for automatic unlock so that
--     a locked-out service account does not require manual DBA intervention.
--
-- Author: Jan Mura
-- Version: 1.2
-- Last modified: 2026-05-01
-- =============================================================================

-- ---------------------------------------------------------------------------
-- NO_EXPIRY_PROFILE
-- Disables password expiry for application service accounts.
-- Appropriate for schemas accessed only from within a private VCN subnet
-- with no public endpoint exposure.
-- A modest lockout threshold (10 attempts, 1-hour auto-unlock) is retained
-- as a defence-in-depth measure against internal compromise.
-- ---------------------------------------------------------------------------
CREATE PROFILE NO_EXPIRY_PROFILE LIMIT
    PASSWORD_LIFE_TIME      UNLIMITED
    PASSWORD_REUSE_TIME     UNLIMITED
    PASSWORD_REUSE_MAX      UNLIMITED
    FAILED_LOGIN_ATTEMPTS   10
    PASSWORD_LOCK_TIME      1/24
    PASSWORD_GRACE_TIME     UNLIMITED;
