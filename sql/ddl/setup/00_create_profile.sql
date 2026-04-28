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
-- Run as:  SYSDBA
-- Prereqs: none
--
-- Author: Jan Mura
-- Version: 1.1
-- Last modified: 2026-04-20
-- =============================================================================

-- ---------------------------------------------------------------------------
-- NO_EXPIRY_PROFILE
-- Disables password expiry and lockout for application service accounts.
-- Appropriate for schemas accessed only from within a private VCN subnet
-- with no public endpoint exposure.
-- ---------------------------------------------------------------------------
CREATE PROFILE NO_EXPIRY_PROFILE LIMIT
    PASSWORD_LIFE_TIME      UNLIMITED
    PASSWORD_REUSE_TIME     UNLIMITED
    PASSWORD_REUSE_MAX      UNLIMITED
    FAILED_LOGIN_ATTEMPTS   UNLIMITED
    PASSWORD_LOCK_TIME      UNLIMITED
    PASSWORD_GRACE_TIME     UNLIMITED;
