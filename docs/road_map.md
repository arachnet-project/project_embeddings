# ARC_FILE: docs/road_map.md
# Arachnet Clinical Embeddings — Project Roadmap
# docs/road_map.md
#
# Author: Jan Mura, Arachnet Project z.s.
# Version: 1.3
# Updated: 2026-08-27

---

## Phase 0 — Foundation & Infrastructure

**Nature:** Engineering prerequisite. No clinical output.
**Status:** In progress.

Establish the shared infrastructure required by subsequent phases:

- YAML configuration.
- Error-handling conventions.
- Python and Bash logging.
- Configuration loading.
- Shared Oracle database-connection support.
- Local prerequisite bootstrap.
- Optional post-provisioning real-database verification.
- Phase 0 integration and conformance audit.

Phase 0 does not provision Oracle objects, create application tables,
or ingest SNOMED CT release files.

The `snomed` and `snomed_stage` staging pattern is established as an
architectural decision in Phase 0. Its Oracle implementation belongs
to Phase 1.

Detail: `docs/phase0_foundation.md`

---

## Phase 1 — RF2 Ingestion Pipeline

**Nature:** Data engineering. Authoritative SNOMED store established.
**Status:** Pending Phase 0 completion.

Provision the required Oracle structures and load SNOMED CT RF2
release files into Oracle.

Phase 1 owns:

- Oracle setup procedures.
- Profiles.
- Tablespaces.
- Application schemas.
- Grants.
- Application table definitions.
- RF2 bulk loading.
- Release versioning.
- Inactive concept handling.
- Staging, validation, and promotion.
- Parquet export for downstream processing.

Key decisions already made:

- The staging-schema pattern is designed in Phase 0 and implemented
  in Phase 1.
- `snomed_stage` is loaded and validated before data is promoted for
  production use in `snomed`.
- Oracle is the single authoritative source.
- Parquet export serves the Phase 3 embedding pipeline and is not an
  alternative authoritative store.
- Inactive concepts are retained and flagged rather than discarded.

The authoritative setup and ingestion commands must be selected from
the existing scripts and documented during Phase 1.

---

## Phase 0 and Phase 1 Runtime Order

Development phase numbering and runtime command order are related but
are not identical.

On a fresh installation, the intended order is:

1. Run local bootstrap to verify shared prerequisites.
2. Run the approved Phase 1 Oracle setup procedure.
3. Run real-database bootstrap to verify the provisioned application
   schemas.
4. Run the approved Phase 1 RF2 ingestion procedure.

Privileged SYSDBA access belongs to Phase 1 Oracle provisioning. It is
not required by local or real-database bootstrap.

No unified top-level orchestrator is introduced in Phase 0 without a
separate architectural decision.

---

## Phase 2 — MRCM & Semantic Policy Layer

**Nature:** Ontology governance. Architectural centrepiece. Design gate.
**Status:** Pending Phase 1 completion.

Import MRCM reference sets into Oracle. Map MRCM rules concerning
domain, attribute, range, grouping, and cardinality to the relationship
policy layer.

Enforce semantic constraints before any relationship becomes an
embedding input.

Separation of concerns:

- MRCM answers whether a relationship is ontologically valid.
- The policy layer determines how the relationship behaves
  computationally, including cost, decay, traversal, and weighting.

---

## Phase 3 — Embedding Engine

**Nature:** ML computation. GPU-accelerated local compute.
**Status:** Pending Phase 2 completion.

Produce clinically safe and explainable embeddings from three signals:

- Graph and ontology embeddings based on the IS-A hierarchy and other
  approved SNOMED structure.
- Text embeddings based on descriptions, fully specified names, and
  synonyms.
- Relationship-weighted embeddings governed by the semantic policy
  layer.

The embedding strategy is research-governed. Detailed research and
design are maintained in ANTHEA.

Embeddings are stored using Oracle vector capabilities.

---

## Phase 4 — Query & Inference Layer

**Nature:** Platform capability. First externally demonstrable output.
**Status:** Pending Phase 3 completion.

Provide semantic search, similarity, and reasoning over the embedding
store.

Core capabilities include:

- Oracle vector-distance operations.
- Hybrid vector, relational, and graph queries.
- Path-based inference.
- Confidence tracking.
- Provenance tracking.

This phase produces the first API surface and the basis for
institutional demonstrations and monetisation discussions.

---

## Phase 5 — Testing & QA

**Nature:** Integration and regression certification. Not a starting point.
**Status:** Pending Phase 4 completion.

Unit and integration tests are distributed throughout all development
phases.

Phase 5 performs full-pipeline regression and certification across:

- RF2 ingestion.
- Validation.
- Graph construction.
- Semantic policy enforcement.
- Embedding generation.
- Search and inference.
- MRCM compliance.
- Performance at scale.

This phase produces the test record required for clinical correctness
claims and regulatory positioning.

---

## Phase 6 — Compliance, Audit & Governance

**Nature:** Formal certification pass. Not a starting point.
**Status:** Pending Phase 5 completion.

Compliance and audit are distributed concerns beginning in Phase 0,
including error codes, logging, staging design, reproducibility, and
data lineage.

Phase 6 performs the end-to-end review and hardening pass required
before regulated or institutional deployment.

It covers:

- Audit logging.
- Versioned outputs.
- Reproducibility controls.
- Data lineage.
- SNOMED CT licence enforcement.
- Alignment with the EU AI Act.
- Applicable healthcare IT governance standards.

Phase 5 produces the technical evidence. Phase 6 reviews and certifies
the complete governance and audit position.

---

## Phase 7 — Documentation & Packaging

**Nature:** Institutional readiness.
**Status:** Ongoing throughout; formal completion after Phase 6.

Documentation is accumulated throughout the project and formally
completed after testing and compliance certification.

Documentation tracks include:

- Engineering and project documentation.
- Executive and institutional whitepaper.
- Investor and due-diligence materials.
- Consumer and API documentation when applicable.

The final directory organization is governed by the approved project
documentation structure.

---

## Phase 8 — Productisation & API

**Nature:** Optional post-monetisation phase.
**Status:** Deferred. Scope to be defined after Phase 4.

Expose the query and inference layer as an institutional service.

Potential scope includes:

- Deployment models.
- Licensing.
- API governance.
- Access control.
- Service operations.
- Integration support.

The scope and architecture will be defined after Phase 4, when the
first demonstrable query capability exists and prospective users have
been identified.

---

## Dependency Chain

    Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
                                                ↓
                                   Phase 5 → Phase 6
                                                ↓
                                            Phase 7
                                                ↓
                                            Phase 8

Phase 2 is a design gate. Phase 3 architecture cannot be committed
until the Phase 2 design is complete.

Phases 5 and 6 are certification phases rather than starting points.
Testing in Phase 5 produces evidence; Phase 6 performs formal
governance and compliance review.

Phase 7 documentation accumulates throughout the project. Its formal
completion requires Phases 5 and 6 to be complete.

---

## Estimated Effort

The estimates are indicative and will be revised using evidence from
completed work.

| Phase | Description | Hours |
|---|---|---:|
| 0 | Foundation | 40–60 |
| 1 | RF2 ingestion | 80–120 |
| 2 | MRCM and policy | 100–150 |
| 3 | Embedding engine | 200–300 |
| 4 | Query and inference | 120–180 |
| 5 | Testing and QA | 80–120 |
| 6 | Compliance and audit | 60–100 |
| 7 | Documentation | 40–60 |
| 8 | Productisation | To be determined |
| **Total excluding Phase 8** | | **720–1,090** |

Estimates are by Jan Mura, solo developer, based on Phase 0 actuals
and prior SNOMED ingestion experience.
```

This revision deliberately stays project-wide. It does not duplicate the detailed Step 0.1–0.7 specifications.
