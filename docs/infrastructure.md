# Infrastructure Reference
# docs/infrastructure.md
# =========================================
# Version: 1.1
# Last updated: 2026-04-28
# Purpose: Permanent reference for all infrastructure parameters,
#          OCIDs, connection details, and environment variables.
#
# IMPORTANT: Never store passwords or API keys in this file.
#            This file is committed to Git.
#            Store only variable names, not values.
#            OCIDs are not sensitive — safe to commit.


## 1. OCI Compartments

Three compartments separate network, database, and compute resources.

Network compartment (NETWORK_COMPARTMENT):
    Purpose:  VCN, gateways, route tables, security groups
    OCID:     ocid1.compartment.oc1..aaaaaaaas44wrtja532252pvu7qytiojxrjlaythkic2untvfdgywmky5wba

Database compartment (DB_COMPARTMENT):
    Purpose:  Oracle Base Database Service
    OCID:     ocid1.compartment.oc1..aaaaaaaat5cqzee4lqphqnikbot2ps6xbpvurnrb3fichc7zaqnhaniwac3a

Linux VM compartment (VM_COMPARTMENT):
    Purpose:  Compute VM running Oracle Linux 9
    OCID:     ocid1.compartment.oc1..aaaaaaaakxu7mjj5b2bi5qgp23xborkef2b3wib2y5rb54mz4w2lij5qrdhq


## 2. Network

VCN (Arachnet VCN):
    CIDR:     10.0.0.0/16
    DNS:      arachworknet
    OCID:     ocid1.vcn.oc1.eu-frankfurt-1.amaaaaaaxs5lciqafzwtg6cicgr2yz3jdckqna2pwkktmhmo5x2t5tghqduq

Public subnet:
    CIDR:     10.0.0.0/24
    DNS:      web
    AD:       FLaW:EU-FRANKFURT-1-AD-1
    OCID:     ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaa7mvxrpbslznmsvu4f4wfg26vpyeuukc2zxcu7wykqsktw7uq2xea

Private subnet:
    CIDR:     10.0.1.0/24
    DNS:      db
    AD:       FLaW:EU-FRANKFURT-1-AD-1
    OCID:     ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaaz2vbyy3zvu33m7w7n5wbi6vssill6kswjgyawirchvxjhctualca

Internet gateway (arachnet_inet_gateway):
    OCID:     ocid1.internetgateway.oc1.eu-frankfurt-1.aaaaaaaavhniqwahy44td4q6mjqhpqxzvh2oojn34xtty2xpnqmtbfs6v2aa

NAT gateway (Arachnet NAT Gateway):
    OCID:     ocid1.natgateway.oc1.eu-frankfurt-1.aaaaaaaa6rw36s5evllquvlqs47ysn7kbs5xlrqdim5lz3ip4ka6jskwsewa

Public route table:
    Routes:   0.0.0.0/0 via internet gateway
    OCID:     ocid1.routetable.oc1.eu-frankfurt-1.aaaaaaaasn5u3u5k4btuvq7syrqkr7q2px5edzcifadxvvlrm3cn7vltex7q

Private route table:
    Routes:   0.0.0.0/0 via NAT gateway
    OCID:     ocid1.routetable.oc1.eu-frankfurt-1.aaaaaaaax7b4vv5dxuhtn36v2fqkhwfxovknfsnwbefnzbx65q6njkxzljkq

NSG — Apache Server:
    OCID:     ocid1.networksecuritygroup.oc1.eu-frankfurt-1.aaaaaaaahi52t2a4mg3w6brxnkjbtevna3twyxbd22qazklhk26eqgnaasca

NSG — Private:
    OCID:     ocid1.networksecuritygroup.oc1.eu-frankfurt-1.aaaaaaaagkokj4hc6mcseaeqwikh5lsh6fpt37ixxkzho6kaw4sup3ei5ria

Bastion (Oracle-SSH-Bastion):
    OCID:     ocid1.bastion.oc1.eu-frankfurt-1.amaaaaaaxs5lciqadr55vcxsawyo5sezv4gseug5mzjhgoaneb7mmsdhjgaq


## 3. Compute instance (Linux VM)

Name:           arachnetwebserver
Shape:          VM.Standard.A2.Flex (2 OCPU, 8 GB RAM)
OS:             Oracle Linux 9
Public IP:      130.61.83.236
Subnet:         Public subnet (10.0.0.0/24)
SSH user:       opc
SSH:            ssh opc@130.61.83.236
Project root:   /home/opc/project_embeddings
SQLcl:          ~/sqlcl/bin/sql
OCID:           ocid1.instance.oc1.eu-frankfurt-1.antheljsxs5lciqc4ijpahg7wwyq2q2kdyfhgk46mtjykx5rqjpa3rjcemsq

OS maintenance:
    sudo dnf update    — run periodically for security patches
    sudo reboot        — reboot after major updates
    Last dnf update:   pending (aborted 2026-04-20, needs re-run with y)


## 4. Oracle Database

DB System name:     (fill in display name from OCI console)
Shape:              VM.Standard.E5.Flex (1 OCPU, 256 GB storage)
Edition:            Standard Edition 2 (SE2)
Version:            23ai, 23.7.0.25.01 — upgrade to 26ai pending
Subnet:             Private subnet (10.0.1.0/24)
DB System OCID:     ocid1.dbsystem.oc1.eu-frankfurt-1.antheljsxs5lciqauoq75aacnx67osrmi3z6tfk22rrogj5lzn5a6x3tnwea
Database OCID:      (retrieve via: oci db database list --db-system-id <db_system_ocid>)

Connection:
    TNS alias:        ARADB
    TNS_ADMIN:        must be set in ~/.bashrc on Linux VM
    SQLcl command:    ~/sqlcl/bin/sql sys/<password>@ARADB as sysdba
    Access:           Linux VM only — no public IP on DB VM

Schemas:
    snomed          production schema, RF2 tables, TBS_SNOMED
    snomed_stage    stage schema, ingestion swap, TBS_SNOMED_STAGE
    SNOMED_TEST     legacy test schema (pre-project, for reference)
    SYS             system administrator
    SYSTEM          system administrator

Tablespaces:
    TBS_SNOMED        1G initial, autoextend 512M, no maximum
    TBS_SNOMED_STAGE  1G initial, autoextend 512M, no maximum

Profile:
    NO_EXPIRY_PROFILE   PASSWORD_LIFE_TIME UNLIMITED
                        Assigned to: SYS, SYSTEM, SNOMED_TEST
                        Will be assigned to SNOMED and SNOMED_STAGE
                        after SQL setup scripts are run

Account status (2026-04-20):
    SYS          OPEN   NO_EXPIRY_PROFILE
    SYSTEM       OPEN   NO_EXPIRY_PROFILE
    SNOMED_TEST  OPEN   NO_EXPIRY_PROFILE
    SNOMED       not yet created
    SNOMED_STAGE not yet created


## 5. Environment variables

Set in ~/.bashrc on each machine. Never store values in this file.

All machines:
    ANTHROPIC_API_KEY       Claude API key (from console.anthropic.com)
    SNOMED_LOG_DIR          Log directory
                            Ubuntu: /home/jan/project_embeddings/log
                            OCI:    /home/opc/project_embeddings/log
    SNOMED_LOG_LEVEL        DEBUG | INFO | WARNING | ERROR  (default INFO)
    LC_ALL                  C.UTF-8

OCI Linux VM only:
    TNS_ADMIN               Path to directory containing tnsnames.ora
    SNOMED_DB_PASSWORD      Password for snomed schema
    SNOMED_STAGE_DB_PASSWORD Password for snomed_stage schema
    SNOMED_ADMIN_DB_PASSWORD SYS password for sql_setup.sh

OCI Linux VM — OCID exports (add after running test_infrastructure.sh):
    OCI_DB_COMPARTMENT_OCID
    OCI_DB_SYSTEM_OCID
    OCI_DATABASE_OCID       (retrieved by test script)
    OCI_VM_COMPUTE_INSTANCE_OCID
    OCI_LINUX_COMPARTMENT_OCID

Optional (command line or ~/.bashrc on OCI):
    SNOMED_TEST_REAL_DB     true | false (default false)
                            Enables real Oracle tests in run_tests.sh


## 6. OCI CLI

Mac Studio:     version 3.79.0
Linux VM:       (install if needed: see OCI documentation)
Config:         ~/.oci/config on each machine

Key commands:

List databases in DB compartment:
    oci db database list \
        --compartment-id $OCI_DB_COMPARTMENT_OCID \
        --query "data[*].{name:\"db-name\",id:id,version:\"db-version\"}" \
        --output table

Check 26ai availability for DB System:
    oci db version list \
        --compartment-id $OCI_DB_COMPARTMENT_OCID \
        --db-system-id $OCI_DB_SYSTEM_OCID \
        --query "data[*].version" \
        --output table

Oracle upgrade precheck:
    oci db database upgrade-with-db-version \
        --database-id $OCI_DATABASE_OCID \
        --action PRECHECK \
        --db-version 23.26.0.0.0

Oracle upgrade:
    oci db database upgrade-with-db-version \
        --database-id $OCI_DATABASE_OCID \
        --action UPGRADE \
        --db-version 23.26.0.0.0

Monitor work request:
    oci work-requests work-request get \
        --work-request-id <work-request-ocid> \
        --query "data.{status:status,percent:\"percent-complete\"}" \
        --output table


## 7. Budget

Budget OCID:        ocid1.budget.oc1.eu-frankfurt-1.amaaaaaaxs5lciqa7qt4l6daqqhw6g3q2nowgcsebatiamlhueeo7gl5udaq
Alert rule OCID:    ocid1.alertrule.oc1..aaaaaaaa2vvyp7amsyztf4il3mj5o2t6mmwnfckysae6v4sxxx67curhpa4q
Period:             Monthly
Amount:             (fill in from OCI console)


## 8. Maintenance log

2025-02-02  OCI compartments created (NETWORK, DB, VM)
2025-02-03  VCN, subnets, gateways created
2025-02-15  NSG rules added
2025-02-20  Bastion created
2025-03-12  Oracle DB System created (23ai SE2)
2026-04-20  SYS and SYSTEM assigned to NO_EXPIRY_PROFILE
2026-04-20  sudo dnf update started — aborted, needs re-run
2026-04-20  OCI CLI upgraded to 3.79.0 on Mac
2026-04-28  infrastructure.md created, OCIDs documented


## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.

Czech national SNOMED CT affiliate licence administered by UZIS.
