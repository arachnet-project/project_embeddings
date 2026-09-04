# ARC_FILE: docs/ace_architecture.md

# ACE — Conceptual Architecture: The Four-Layer Model

# Version: 0.1 (Draft)
# Status: Proposed — pending transfer to ANTHEA

## Purpose

This document records the four-layer conceptual model developed for
ACE's clinical embedding and reasoning approach, based on SNOMED CT.

It is a conceptual and research-oriented record, not an ACE
implementation specification. It is intended for eventual transfer
into the ANTHEA project, ACE's parallel theoretical research effort.

It contains no embedding construction detail, weighting strategy,
ranking algorithm, or other implementation-sensitive material.

## Overview

The model organizes clinical reasoning into four layers, moving from
authoritative source knowledge through validated structure, learned
representation, and finally user-facing search and reasoning.

## Layer 1 — Source of Truth

Based on SNOMED CT: concepts, descriptions, relationships, and
reference sets. This layer represents expert-authored clinical
knowledge.

Example attributes: finding site, associated morphology, causative
agent.

## Layer 2 — Rulebook

Based on SNOMED CT modeling constraints, principally the Machine
Readable Concept Model (MRCM). This layer validates allowed
relationships and attribute domains, and enforces model consistency.

It answers "Is this allowed?" before any learning takes place.

## Layer 3 — Learning Engine

Combines hierarchical structure, concept relationships, clinical
attributes, and clinical language into computable representations.
Neither purely linguistic nor purely mathematical — it integrates
ontology structure and language.

## Layer 4 — Search and Reasoning

The interaction point between user input, retrieved concepts, learned
representations, and clinical knowledge. Produces the results
presented to the user.

## Worked Example — Acute Appendicitis

Chosen as a demonstration concept for its clinical familiarity and
rich SNOMED relationships.

Attributes:
* Finding site = Appendix structure
* Associated morphology = Inflammation

## Attribute Propagation

A conceptual path through the four layers:

```
SNOMED CT Concept
    -> Rule Validation
    -> Representation Learning
    -> Search and Reasoning
```

Example signal mappings:

| SNOMED CT element     | Resulting signal    |
|------------------------|---------------------|
| Finding site            | Anatomical signal    |
| Associated morphology  | Pathological signal  |
| Hierarchy                | Taxonomic signal      |
| Descriptions             | Linguistic signal     |

## Scope

This document records the conceptual model as discussed and developed
prior to 2026-06-16. It does not include implementation detail,
roadmap, or predictions, and is not a source of authority for ACE
engineering decisions.
