# ARC_FILE: docs/road_map.md
# Arachnet Clinical Embeddings — Project Roadmap
# docs/road_map.md
#
# Author:  Jan Mura, Arachnet Project z.s.
# Version: 1.2
# Updated: 2026-05-22

---

## Phase 0 — Foundation & Infrastructure
**Nature:** Engineering prerequisite. No clinical output.
**Status:** In progress.

Shared utilities, configuration, logging, database connection,
and bootstrap script. Establishes conventions and tooling that
all subsequent phases depend on.

Detail: `docs/phase0_foundation.md`

---

## Phase 1 — RF2 Ingestion Pipeline
**Nature:** Data engineering. Authoritative SNOMED store established.
**Status:** Pending Phase 0 completion.

Load SNOMED CT RF2 release files into Oracle. Covers schema design,
DDL, bulk load pipeline, versioning, inactive concept handling,
staging schema pattern (load → validate → swap), and Parquet export
for downstream processing.

Key decisions already made:
- Staging schema (snomed_stage → snomed swap) in place from Phase 0
- Oracle is the single authoritative source
- Parquet export serves Phase 3 embedding pipeline, not Phase 1 alone
- Inactive concepts are retained, flagged, not discarded

---

## Phase 2 — MRCM & Semantic Policy Layer
**Nature:** Ontology governance. Architectural centrepiece. Design gate.
**Status:** Pending Phase 1 completion.

Import MRCM reference sets into Oracle. Map MRCM rules (domain,
attribute, range, grouping, cardinality) to the relationship policy
layer. Enforce semantic constraints before any relationship becomes
an embedding input.

Separation of concerns:
- MRCM answers: is this relationship ontologically valid?
- Policy layer answers: how does this relationship behave
  computationally (cost, decay, traversal, weighting)?

---

## Phase 3 — Embedding Engine
**Nature:** ML computation. GPU-accelerated local compute.
**Status:** Pending Phase 2 completion.

Produce clinically safe, explainable embeddings from three signals:
- Graph / ontology embeddings (IS-A hierarchy, SNOMED structure)
- Text embeddings (descriptions, FSNs, synonyms)
- Relationship-weighted embeddings (policy-governed, domain-specific)

Embedding strategy is research-governed. Detail in ANTHEA.

Embeddings are stored in Oracle 23ai vector indexes.

---

## Phase 4 — Query & Inference Layer
**Nature:** Platform capability. First externally demonstrable output.
**Status:** Pending Phase 3 completion.

Semantic search, similarity, and reasoning over the embedding store.
Oracle 23ai VECTOR_DISTANCE and DBMS_VECTOR_CHAIN as core primitives.
Hybrid queries: vector + relational + graph. Path-based inference.
Confidence and provenance tracking.

This phase produces the first API surface and the basis for
institutional demonstrations and monetisation discussions.

---

## Phase 5 — Testing & QA
**Nature:** Integration and regression certification. Not a starting point.
**Status:** Pending Phase 4 completion.

Unit and integration tests are distributed throughout all phases.
This phase is the full pipeline regression: end-to-end ingestion,
validation, graph construction, embedding, and search against a
complete SNOMED release. Includes MRCM compliance tests and
performance testing at scale.

Produces the test record required for clinical correctness claims
and regulatory positioning.

---

## Phase 6 — Compliance, Audit & Governance
**Nature:** Formal certification pass. Not a starting point.
**Status:** Pending Phase 5 completion.

Compliance and audit are distributed concerns present from Phase 0
onward (error codes, logging, staging schema, data lineage). This
phase is the end-to-end review and hardening pass: verify the audit
trail is complete, consistent, and defensible across the whole
pipeline. Required before regulated or institutional deployment.

Covers: audit logging, versioned outputs, reproducibility controls,
data lineage, SNOMED licence enforcement, alignment with EU AI Act
and healthcare IT governance standards.

---

## Phase 7 — Documentation & Packaging
**Nature:** Institutional readiness.
**Status:** Ongoing throughout; formal completion after Phase 6.

Developer documentation, consumer documentation, executive
whitepaper, investor / due diligence pack. Documentation structure
defined — content is accumulated throughout the project.

Three documentation tracks:
- Engineering / project docs (docs/project/)
- Executive / institutional whitepaper (docs/executive/)
- Investor / due diligence pack (docs/investors/)

---

## Phase 8 — Productisation & API
**Nature:** Optional post-monetisation phase.
**Status:** Deferred. Scope to be defined after Phase 4.

Expose the query and inference layer as a service. Institutional
deployment model, licensing, API governance. Scope and architecture
to be defined once Phase 4 is complete and first users are identified.

---

## Dependency Chain

    Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
                                                ↓
                                   Phase 5 → Phase 6
                                                ↓
                                            Phase 7
                                                ↓
                                            Phase 8

Phase 2 is a design gate — Phase 3 architecture cannot be
committed until Phase 2 design is complete.

Phases 5 and 6 are certification phases, not starting points.
Testing (5) produces the evidence; Compliance (6) certifies it.
Phase 7 documentation accumulates throughout; formal completion
requires Phases 5 and 6 to be done.

---

## Estimated Effort (Indicative)

| Phase                     | Hours         |
|---------------------------|---------------|
| 0 — Foundation            | 40–60         |
| 1 — RF2 Ingestion         | 80–120        |
| 2 — MRCM & Policy         | 100–150       |
| 3 — Embedding Engine      | 200–300       |
| 4 — Query & Inference     | 120–180       |
| 5 — Testing & QA          | 80–120        |
| 6 — Compliance & Audit    | 60–100        |
| 7 — Documentation         | 40–60         |
| 8 — Productisation        | TBD           |
| **Total (excl. Phase 8)** | **720–1,090** |

Estimates by Jan Mura, solo developer, based on Phase 0 actuals
and prior SNOMED ingestion experience.
