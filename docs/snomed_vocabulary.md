# ARC_FILE: docs/snomed_vocabulary.md
# SNOMED CT — Reference Vocabulary
# docs/snomed_vocabulary.md
#
# Author:  Jan Mura, Arachnet Project z.s.
# Version: 0.4
# Updated: 2026-05-22
#
# Purpose:
#   Reference definitions of SNOMED CT terminology used by ACE.
#
# Scope:
#   SNOMED CT concepts and terminology only.
#
# Exclusions:
#   Implementation detail, storage models, graph structures,
#   embedding methodology, pipeline behaviour, and operational
#   processing rules.
#
# Structure:
#   Terms are ordered by dependency. Each definition relies only
#   on terms defined above it.
#
# Status:
#   Living document. Terms are added as required by project phases.

---

## Core Components

### Concept
A unit of clinical meaning within SNOMED CT.

### Description
A textual representation attached to a concept.

### Fully Specified Name (FSN)
The unique and unambiguous description assigned to a concept
within a language or dialect. An FSN includes a semantic tag.

### Semantic Tag
The parenthetical suffix in a Fully Specified Name indicating
the broad category of the concept. Example: *(disorder)*,
*(procedure)*, *(body structure)*.

### Preferred Term
The preferred description for a concept within a language
reference set.

### Synonym
An alternative description associated with a concept.

### Relationship
A directed association between two concepts: a source concept
and a target concept. The type of a relationship is an
attribute.

### Attribute
A concept used as the type of a relationship.

---

## Concept Model

### IS-A Relationship
A relationship stating that a concept is a subtype of another
concept.

### Defining Relationship
A relationship contributing to the formal definition of a
concept.

### Relationship Group
A numeric identifier used to associate relationships that must
be interpreted together.

---

## Reference Sets

### Reference Set (Refset)
A collection of references to SNOMED CT components used for a
defined purpose.

### MRCM (Machine Readable Concept Model)
A set of reference sets defining rules governing the permitted
use of attributes within the SNOMED CT concept model.

### MRCMDomain
An MRCM reference set defining the sets of concepts within
which a given attribute is applicable.

### MRCMAttributeDomain
An MRCM reference set defining the association between an
attribute and its permitted domains, including grouping and
cardinality constraints.

### MRCMAttributeRange
An MRCM reference set defining the permitted target concepts
of an attribute.

### MRCMModuleScope
An MRCM reference set defining the modules to which MRCM
rules apply.
