# ARC_FILE: docs/snomed_vocabulary.md
# SNOMED CT — Reference Vocabulary
# docs/snomed_vocabulary.md
#
# Author: Jan Mura, Arachnet Project z.s.
# Version: 0.5
# Updated: 2026-11-17
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

## Concept

In SNOMED CT, a concept represents a distinct clinical idea. The concept is the meaning itself, separate from the words used to express it.

## Concept Definition

In SNOMED CT, a concept definition is a set of one or more formal logical statements that partially or sufficiently specify a concept’s meaning. It can state that the concept is a subtype of one or more broader concepts and can state characteristics that distinguish it from those broader concepts.

## Expression

In SNOMED CT, an expression is a structured representation of a clinical idea using references to one or more SNOMED CT concepts. The structure specifies how the referenced concepts’ meanings are combined or related. Where permitted, an expression may also include values written directly into its structure, such as numbers or text, rather than references to concepts.

## Precoordinated Expression

In SNOMED CT, a precoordinated expression represents a clinical idea by reference to one existing SNOMED CT concept.

## Concrete Value

In SNOMED CT, a concrete value is a number, text string, or Boolean value represented directly in an expression, rather than by a reference to a concept.

## Description

In SNOMED CT, a description is a component record that associates a human-readable term with a concept. One concept may have multiple descriptions.

## Description Type

In SNOMED CT, a description type indicates whether a description is a Fully Specified Name, a synonym, or a definition.

## Fully Specified Name (FSN)

In SNOMED CT, a Fully Specified Name (FSN) is a description type intended to express a concept’s meaning unambiguously and independently of context. It ends with a parenthetical label indicating the concept’s broad semantic category. The complete FSN, including its parenthetical label, is unique among active SNOMED CT descriptions.

## Semantic Tag

In SNOMED CT, a semantic tag is the parenthetical label at the end of an FSN. It indicates the broad semantic domain of the concept, such as disorder, procedure, or body structure.

## Synonym

In SNOMED CT, a synonym is a description type that expresses the meaning of a concept using a word or phrase in a specified language. A concept may have multiple synonyms, and the same word or phrase may be used as a synonym for more than one concept.

## Relationship

In SNOMED CT, a relationship is an association between a source concept and a destination concept. The relationship record also identifies the type of association.

## Relationship Type

In SNOMED CT, a relationship type is a concept that identifies the kind of association represented by a relationship.

## IS-A Relationship

In SNOMED CT, an IS-A relationship states that the source concept is a subtype of the destination concept. IS-A relationships connect concepts into hierarchies, linking more specific concepts to broader concepts.

## SNOMED CT Concept Model (Concept Model)

In SNOMED CT, the Concept Model is the set of rules that determines which relationships may be used between particular types of SNOMED CT concepts.

## Postcoordinated Expression

In SNOMED CT, a postcoordinated expression represents a clinical idea using two or more concept references in a structure that specifies how their meanings are related or refined. The structure must follow the rules of the SNOMED CT Concept Model.

## Attribute

In SNOMED CT, an attribute is a concept that represents a characteristic used to define or refine the meaning of another concept or expression.

## Attribute–Value Pair

In SNOMED CT, an attribute–value pair combines an attribute with a value to specify a characteristic of a concept or clinical idea. The attribute identifies the characteristic being specified; the value supplies it. Where permitted, the value may be represented by a concept, an expression, or a concrete value.

## Attribute Relationship

In SNOMED CT, an attribute relationship is a relationship whose type is an attribute, such as Finding site or Associated morphology. It specifies the value of a defining characteristic of the source concept and is distinct from an IS-A relationship.

## Defining Relationship

In SNOMED CT, a defining relationship expresses a condition that must be true of every instance of its source concept.

## Relationship Group

In SNOMED CT, a relationship group is one or more attribute–value pairs grouped within a concept definition or a postcoordinated expression. When a group contains multiple pairs, the grouping indicates that they should be interpreted together as related characteristics of the concept. A group can contain only one pair.

## Range

In SNOMED CT, a range is the set of values permitted for a specified SNOMED CT attribute.

**Explanatory note:** Depending on the attribute, permitted values may be concepts, expressions, or concrete values.

## Domain

In SNOMED CT, a domain is a set of concepts that the Concept Model permits users to define or refine using a particular set of attributes and ranges.

## Cardinality

In SNOMED CT, cardinality specifies the minimum and maximum number of times an attribute may be used in a concept definition or expression. In-group cardinality specifies those limits within a single relationship group.

## SNOMED CT Component

In SNOMED CT, a component is a concept, description, or relationship.

## Reference Set (Refset)

In SNOMED CT, a Reference Set (Refset) is a standard format for representing and distributing a set of references to SNOMED CT components for a defined purpose.

**Explanatory note:** Depending on its type, a reference set can represent a subset of concepts, descriptions, or relationships, or associate referenced components with additional information such as ordering, associations, or mappings. It records which components are included and any additional information associated with them for the reference set’s purpose; it does not change the clinical meaning of the referenced concepts.

## Reference Set Member

In SNOMED CT, a reference set member is a row in a reference set release file. It identifies the reference set and the component it references, and may contain additional information depending on the reference set type.

## Language Reference Set (Language Refset)

In SNOMED CT, a Language Reference Set indicates which descriptions are preferred or acceptable for use in a particular language or dialect.

**Explanatory note:** It may also represent preferences for descriptions in a more specific context, such as a clinical specialty, organization, or department.

## Preferred Term (PT)

In SNOMED CT, a Preferred Term (PT) is the human-readable term associated with a synonym description that is marked as preferred for a concept in a specified language or dialect by the applicable Language Reference Set.

**Clarification:** Preferred Term is not a separate description type; it is the term in a synonym description designated as preferred by the applicable Language Reference Set.

## Module

In SNOMED CT, a module is a group of SNOMED CT components, reference set members, or both, managed, maintained, and distributed as a unit.

## Attribute Grouping

In SNOMED CT, attribute grouping is a Concept Model rule that specifies whether an attribute is treated as belonging to a relationship group when applied in a particular domain.

## Machine Readable Concept Model (MRCM)

In SNOMED CT, the Machine Readable Concept Model (MRCM) is a representation of rules from the SNOMED CT Concept Model in a form that software can process.

**Explanatory note:** The MRCM represents rules about domains and the attributes that may be applied in them, including their permitted ranges, cardinality, and grouping.

## MRCM Reference Set

In SNOMED CT, an MRCM reference set is a reference set type used to represent and distribute a particular kind of information in the Machine Readable Concept Model.

**Explanatory note:** SNOMED CT distributes the MRCM through four reference set types: the MRCM Domain Reference Set, which defines domains; the MRCM Attribute Domain Reference Set, which associates attributes with domains and specifies grouping and cardinality; the MRCM Attribute Range Reference Set, which specifies permitted values; and the MRCM Module Scope Reference Set, which specifies which MRCM reference sets apply to each module.

## MRCM Domain Reference Set

In SNOMED CT, an MRCM Domain Reference Set identifies the domains used by the MRCM and defines which concepts fall within each domain.

**Explanatory note:** Rules associating attributes with domains are recorded separately.

## MRCM Attribute Domain Reference Set

In SNOMED CT, an MRCM Attribute Domain Reference Set associates each attribute with the domain or domains in which it may be applied.

**Explanatory note:** It also specifies whether the attribute belongs to a relationship group and its minimum and maximum cardinality within a concept definition or expression and within a single relationship group.

## MRCM Attribute Range Reference Set

In SNOMED CT, an MRCM Attribute Range Reference Set specifies the range of values permitted for each attribute.

**Explanatory note:** Depending on the attribute, the permitted values may include SNOMED CT concepts, expressions, or concrete values.

## MRCM Module Scope Reference Set

In SNOMED CT, an MRCM Module Scope Reference Set specifies which MRCM Reference Sets apply to content in each SNOMED CT module.
