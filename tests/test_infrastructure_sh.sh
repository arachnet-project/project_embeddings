#!/usr/bin/env bash
# =============================================================================
# Arachnet Clinical Embeddings — Infrastructure OCID verification
# scripts/test_infrastructure.sh
# =============================================================================
# Purpose:
#   Verifies all OCI OCIDs in infrastructure.md are valid and resolvable.
#   Retrieves the database OCID from the DB System.
#   Prints a summary of pass/fail results.
#   On success, prints export statements ready to paste into ~/.bashrc.
#
# Usage:
#   Run from Mac or Linux VM with OCI CLI configured:
#       bash scripts/test_infrastructure.sh
#
#   On Mac: uses OCI CLI at /opt/homebrew/bin/oci or wherever installed.
#   On Linux VM: OCI CLI must be installed and configured.
#
# Prerequisites:
#   - OCI CLI installed and configured (~/.oci/config)
#   - Internet access to OCI API endpoints
#
# Exit code 0 if all checks pass. Exit code 1 if any check fails.
#
# Author: Jan Mura
# Version: 1.0
# =============================================================================

set -uo pipefail
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# OCIDs from infrastructure.md
# ---------------------------------------------------------------------------

OCI_VCN_COMPARTMENT_OCID="ocid1.compartment.oc1..aaaaaaaas44wrtja532252pvu7qytiojxrjlaythkic2untvfdgywmky5wba"
OCI_DB_COMPARTMENT_OCID="ocid1.compartment.oc1..aaaaaaaat5cqzee4lqphqnikbot2ps6xbpvurnrb3fichc7zaqnhaniwac3a"
OCI_LINUX_COMPARTMENT_OCID="ocid1.compartment.oc1..aaaaaaaakxu7mjj5b2bi5qgp23xborkef2b3wib2y5rb54mz4w2lij5qrdhq"
OCI_VCN_OCID="ocid1.vcn.oc1.eu-frankfurt-1.amaaaaaaxs5lciqafzwtg6cicgr2yz3jdckqna2pwkktmhmo5x2t5tghqduq"
OCI_PUBLIC_SUBNET_OCID="ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaa7mvxrpbslznmsvu4f4wfg26vpyeuukc2zxcu7wykqsktw7uq2xea"
OCI_PRIVATE_SUBNET_OCID="ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaaz2vbyy3zvu33m7w7n5wbi6vssill6kswjgyawirchvxjhctualca"
OCI_VM_COMPUTE_INSTANCE_OCID="ocid1.instance.oc1.eu-frankfurt-1.antheljsxs5lciqc4ijpahg7wwyq2q2kdyfhgk46mtjykx5rqjpa3rjcemsq"
OCI_DB_SYSTEM_OCID="ocid1.dbsystem.oc1.eu-frankfurt-1.antheljsxs5lciqauoq75aacnx67osrmi3z6tfk22rrogj5lzn5a6x3tnwea"
OCI_BASTION_OCID="ocid1.bastion.oc1.eu-frankfurt-1.amaaaaaaxs5lciqadr55vcxsawyo5sezv4gseug5mzjhgoaneb7mmsdhjgaq"

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------

_pass=0
_fail=0
_failed_labels=""
OCI_DATABASE_OCID=""

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

pass() {
    local label="$1"
    printf "PASS: %s\n" "${label}"
    _pass=$((_pass + 1))
}

fail() {
    local label="$1"
    local reason="$2"
    printf "FAIL: %s — %s\n" "${label}" "${reason}" >&2
    _fail=$((_fail + 1))
    if [[ -z "${_failed_labels}" ]]; then
        _failed_labels="${label}"
    else
        _failed_labels="${_failed_labels}, ${label}"
    fi
}

check_oci_cli() {
    if ! command -v oci &>/dev/null; then
        printf "ERROR: OCI CLI not found on PATH.\n" >&2
        printf "Install it or check your PATH.\n" >&2
        exit 1
    fi
    printf "OCI CLI: %s\n" "$(oci --version 2>&1 | head -1)"
}

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

printf "========================================\n"
printf "Arachnet Infrastructure OCID Verification\n"
printf "Date: %s\n" "$(date '+%Y-%m-%dT%H:%M:%S')"
printf "========================================\n\n"

check_oci_cli

# ---------------------------------------------------------------------------
# Test 1 — Network compartment
# ---------------------------------------------------------------------------

printf "\nChecking compartments...\n"

result=$(oci iam compartment get \
    --compartment-id "${OCI_VCN_COMPARTMENT_OCID}" \
    --query "data.{name:name,state:\"lifecycle-state\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "ACTIVE"; then
    pass "network_compartment"
else
    fail "network_compartment" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 2 — DB compartment
# ---------------------------------------------------------------------------

result=$(oci iam compartment get \
    --compartment-id "${OCI_DB_COMPARTMENT_OCID}" \
    --query "data.{name:name,state:\"lifecycle-state\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "ACTIVE"; then
    pass "db_compartment"
else
    fail "db_compartment" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 3 — Linux VM compartment
# ---------------------------------------------------------------------------

result=$(oci iam compartment get \
    --compartment-id "${OCI_LINUX_COMPARTMENT_OCID}" \
    --query "data.{name:name,state:\"lifecycle-state\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "ACTIVE"; then
    pass "linux_compartment"
else
    fail "linux_compartment" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 4 — VCN
# ---------------------------------------------------------------------------

printf "\nChecking network resources...\n"

result=$(oci network vcn get \
    --vcn-id "${OCI_VCN_OCID}" \
    --query "data.{name:\"display-name\",state:\"lifecycle-state\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "AVAILABLE"; then
    pass "vcn"
else
    fail "vcn" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 5 — Public subnet
# ---------------------------------------------------------------------------

result=$(oci network subnet get \
    --subnet-id "${OCI_PUBLIC_SUBNET_OCID}" \
    --query "data.{name:\"display-name\",state:\"lifecycle-state\",cidr:\"cidr-block\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "AVAILABLE"; then
    pass "public_subnet"
else
    fail "public_subnet" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 6 — Private subnet
# ---------------------------------------------------------------------------

result=$(oci network subnet get \
    --subnet-id "${OCI_PRIVATE_SUBNET_OCID}" \
    --query "data.{name:\"display-name\",state:\"lifecycle-state\",cidr:\"cidr-block\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "AVAILABLE"; then
    pass "private_subnet"
else
    fail "private_subnet" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 7 — Compute instance (Linux VM)
# ---------------------------------------------------------------------------

printf "\nChecking compute instance...\n"

result=$(oci compute instance get \
    --instance-id "${OCI_VM_COMPUTE_INSTANCE_OCID}" \
    --query "data.{name:\"display-name\",state:\"lifecycle-state\",shape:shape}" \
    --output json 2>&1)

if echo "${result}" | grep -q "RUNNING"; then
    pass "linux_vm"
    printf "  VM state: RUNNING\n"
else
    fail "linux_vm" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 8 — DB System
# ---------------------------------------------------------------------------

printf "\nChecking Oracle DB System...\n"

result=$(oci db system get \
    --db-system-id "${OCI_DB_SYSTEM_OCID}" \
    --query "data.{name:\"display-name\",state:\"lifecycle-state\",version:version,shape:shape}" \
    --output json 2>&1)

if echo "${result}" | grep -q "AVAILABLE"; then
    pass "db_system"
    printf "  DB System: AVAILABLE\n"
    # Print version for information
    db_version=$(echo "${result}" | python3 -c \
        "import sys,json; d=json.load(sys.stdin); print(d.get('version','unknown'))" \
        2>/dev/null || echo "unknown")
    printf "  Version: %s\n" "${db_version}"
else
    fail "db_system" "${result}"
fi

# ---------------------------------------------------------------------------
# Test 9 — Retrieve database OCID from DB System
printf "\nRetrieving database OCID from DB System...\n"

OCI_DATABASE_OCID=$(oci db database list \
    --compartment-id "${OCI_DB_COMPARTMENT_OCID}" \
    --db-system-id "${OCI_DB_SYSTEM_OCID}" \
    --limit 10 \
    --output json \
    --query "data[?\"lifecycle-state\"=='AVAILABLE'] | [0].id" \
    --raw-output 2>/dev/null || echo "")

db_name=$(oci db database list \
    --compartment-id "${OCI_DB_COMPARTMENT_OCID}" \
    --db-system-id "${OCI_DB_SYSTEM_OCID}" \
    --limit 10 \
    --output json \
    --query "data[?\"lifecycle-state\"=='AVAILABLE'] | [0].\"db-name\"" \
    --raw-output 2>/dev/null || echo "unknown")

if [[ -n "${OCI_DATABASE_OCID}" && "${OCI_DATABASE_OCID}" != "None" ]]; then
    pass "database_ocid_retrieval"
    printf "  Database name: %s\n" "${db_name}"
    printf "  Database OCID: %s\n" "${OCI_DATABASE_OCID}"
else
    # Debug: show raw output to diagnose
    raw=$(oci db database list \
        --compartment-id "${OCI_DB_COMPARTMENT_OCID}" \
        --db-system-id "${OCI_DB_SYSTEM_OCID}" \
        --limit 10 \
        --output json 2>&1)
    fail "database_ocid_retrieval" "OCID empty — raw: ${raw}"
fi

# ---------------------------------------------------------------------------
# Test 10 — Bastion
# ---------------------------------------------------------------------------

printf "\nChecking bastion...\n"

result=$(oci bastion bastion get \
    --bastion-id "${OCI_BASTION_OCID}" \
    --query "data.{name:name,state:\"lifecycle-state\"}" \
    --output json 2>&1)

if echo "${result}" | grep -q "ACTIVE"; then
    pass "bastion"
else
    fail "bastion" "${result}"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

total=$((_pass + _fail))
printf "\n========================================\n"
printf "Total:  %d\n" "${total}"
printf "Passed: %d\n" "${_pass}"
printf "Failed: %d\n" "${_fail}"

if [[ "${_fail}" -gt 0 ]]; then
    printf "Failed: %s\n" "${_failed_labels}"
    printf "Overall: FAIL\n"
    printf "========================================\n"
    exit 1
fi

printf "Overall: PASS\n"
printf "========================================\n"

# ---------------------------------------------------------------------------
# Print export statements for ~/.bashrc
# ---------------------------------------------------------------------------

printf "\n\n"
printf "========================================\n"
printf "Add these exports to ~/.bashrc on OCI and Mac:\n"
printf "========================================\n"
printf "\n"
printf "# Arachnet OCI resource OCIDs\n"
printf "export OCI_VCN_COMPARTMENT_OCID=\"%s\"\n" "${OCI_VCN_COMPARTMENT_OCID}"
printf "export OCI_DB_COMPARTMENT_OCID=\"%s\"\n" "${OCI_DB_COMPARTMENT_OCID}"
printf "export OCI_LINUX_COMPARTMENT_OCID=\"%s\"\n" "${OCI_LINUX_COMPARTMENT_OCID}"
printf "export OCI_VCN_OCID=\"%s\"\n" "${OCI_VCN_OCID}"
printf "export OCI_PUBLIC_SUBNET_OCID=\"%s\"\n" "${OCI_PUBLIC_SUBNET_OCID}"
printf "export OCI_PRIVATE_SUBNET_OCID=\"%s\"\n" "${OCI_PRIVATE_SUBNET_OCID}"
printf "export OCI_VM_COMPUTE_INSTANCE_OCID=\"%s\"\n" "${OCI_VM_COMPUTE_INSTANCE_OCID}"
printf "export OCI_DB_SYSTEM_OCID=\"%s\"\n" "${OCI_DB_SYSTEM_OCID}"
printf "export OCI_BASTION_OCID=\"%s\"\n" "${OCI_BASTION_OCID}"
if [[ -n "${OCI_DATABASE_OCID}" ]]; then
    printf "export OCI_DATABASE_OCID=\"%s\"\n" "${OCI_DATABASE_OCID}"
fi
printf "\n"
printf "After adding to ~/.bashrc run: source ~/.bashrc\n"
printf "========================================\n"

exit 0
