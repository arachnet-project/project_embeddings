# UZIS Correspondence — Czech SNOMED CT National Extension
## Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-04-10
**Contact:** MUDr. Magdaléna Svetíková — wait, correction:
**Contact:** MUDr. Irena Molinari, UZIS
**Subject:** Czech SNOMED CT national extension — technical questions

---

## Background

UZIS (Ústav zdravotnických informací a statistiky ČR) is the Czech national
SNOMED CT affiliate administrator and the National Release Centre (NRC) for
the Czech Republic. All questions regarding the Czech national SNOMED CT
extension are directed to UZIS.

Arachnet Project z.s. uses SNOMED CT under an affiliate licence administered
by UZIS. The Czech national extension is planned for inclusion in the
Arachnet Clinical Embeddings platform from Phase 1 onward.

---

## UZIS Response — Summary of Points

### Point 1 — RF2 file list

**UZIS statement:**
The list of extended RF2 files is part of the Czech files package distributed
by NRC CR. The package follows the standards of SNOMED CT International.

**Analysis:**
Clear and confirmed. The Czech extension package contains a complete RF2
file list discoverable by examining the package. The package follows standard
SNOMED International RF2 structure — standard folder layout, standard file
naming, standard column layouts. No proprietary formats.

**Impact on project:**
No changes to ingestion pipeline design needed. Standard RF2 loader handles
the Czech extension without modification.

**Action required:** None. Obtain package via MLDS portal or directly from
UZIS.

---

### Point 2 — Module identifier (moduleId)

**UZIS statement:**
UZIS will provide the moduleId for the Czech extension. It could differ for
every release version.

**Analysis:**
The statement that moduleId differs per release is likely a misunderstanding.
ModuleId identifies the authoring organisation — in this case UZIS or the
Czech NRC — and should be a stable, fixed SCTID that does not change between
releases. What changes between releases is the `effectiveTime` column on
individual components, which records when each component was last modified.

Ms Molinari may be conflating moduleId with effectiveTime, or the Czech
extension may use multiple modules for different content types (e.g. one
module for Czech descriptions, another for Czech-specific concepts). In
the latter case there would be multiple moduleIds, but each would still
be stable.

**Impact on project:**
ModuleId is used in `ingestion.yaml` under `national_extensions` to
distinguish Czech extension components from international components at
query time. If the moduleId is genuinely stable, it can be hardcoded once
after the first load. If multiple modules are used, all need to be recorded.

**Action required:**
Clarify with UZIS at the online meeting. Proposed question:

"We expect the moduleId to be a stable, fixed SCTID identifying the Czech
NRC as the authoring organisation, remaining constant across all release
versions, while effectiveTime changes with each release. Could you confirm
whether this is correct? If the Czech extension uses multiple modules for
different content types, please provide the complete list of module SCTIDs."

---

### Point 3 — Language refset SCTID

**UZIS statement:**
The language refset identifier (SCTID) is defined as part of the Czech
national extension. UZIS will send it with the distribution package.

**Analysis:**
Clear and confirmed. The Czech language refset SCTID is a fixed defined
identifier included in the distribution package. This is consistent with
standard SNOMED CT practice — the language refset SCTID identifies the
Czech language acceptability refset and is stable across releases.

**Impact on project:**
The `language_refset_id` field in `ingestion.yaml` under `national_extensions`
will be filled in after receiving the package. It can be discovered by:

1. Checking the release notes document included in the package.
2. Querying `sct_refset_language` after the first load and identifying the
   refsetId that is not the English language refset SCTID `900000000000508004`.

**Action required:**
Record the Czech language refset SCTID in `ingestion.yaml` after the first
load. Document it in this file for reference.

Czech language refset SCTID: **to be filled after first load**

---

### Point 4 — Czech extension content

**UZIS statement:**
The Czech extension contains local (Czech) descriptions in the Description
RF2 file. It may also contain refsets according to the release.

**Analysis:**
Confirmed. Czech descriptions load into `sct_description` alongside English
descriptions, distinguished by `languageCode = cs`. The existing 17-table
structure handles this with no changes needed.

The phrase "according to release" regarding additional refsets means refset
content may vary between releases. Some releases may include national subsets,
additional mappings, or clinical domain groupings beyond the language refset.

**Impact on project:**
Current table structure is likely sufficient. However if the Czech extension
includes a map refset in a non-standard format — for example a mapping to
Czech DRG codes or the Czech national diagnosis classification — a new table
entry in `database.yaml` may be needed.

**Action required:**
Ask at the online meeting for a complete list of refsets currently included
in the Czech extension beyond the language acceptability refset. Proposed
question:

"Could you provide an overview of which reference sets are currently included
in the Czech extension beyond the language acceptability refset? For example,
are there national subset refsets, ICD-10 mappings specific to Czech
healthcare, or clinical domain groupings? This will help us plan our database
structure."

---

### Point 5 — Release notifications

**UZIS statement:**
UZIS will add Arachnet to the notification list for new Czech extension
releases.

**Analysis:**
Clear and confirmed. This is the most important operational outcome of the
correspondence — it ensures Arachnet receives timely notification of new
releases and can update the platform accordingly.

**Impact on project:**
When a new Czech release notification arrives, the process is:
1. Download the new package from MLDS portal.
2. Update `data_release` in `project.yaml`.
3. Run the full ingestion pipeline — drop, reload, validate, swap.
4. Verify Czech descriptions and language refset are present in the new load.

**Action required:**
Confirm with UZIS that jan.mura@volny.cz is correctly registered on the
notification list.

---

### Point 6 — Online meeting offer

**UZIS statement:**
UZIS offers an online meeting to discuss remaining questions.

**Analysis:**
This is valuable and should be accepted promptly. A meeting allows resolution
of technical questions that are difficult to clarify by email — particularly
the moduleId question and the complete refset inventory.

**Action required:**
Accept the meeting offer. Prepare the agenda below.

---

## Meeting Agenda

Proposed questions for the UZIS online meeting:

**1. Module identifier clarification**
Confirm whether the Czech extension moduleId is a stable fixed SCTID across
all releases. If multiple modules are used, obtain the complete list.

**2. Complete refset inventory**
Obtain a list of all refsets included in the current Czech extension beyond
the language acceptability refset. Specifically ask about national subset
refsets, Czech-specific maps, and clinical domain groupings.

**3. Release schedule**
Confirm the Czech extension release schedule and whether it aligns with or
offsets from the SNOMED International monthly release cycle.

**4. Current package access**
Request the current Czech extension package for development and testing
purposes.

**5. Access process for future releases**
Confirm the recommended process for accessing future releases — MLDS portal,
direct download, or another channel.

**6. Namespace for future extension authoring (optional)**
If appropriate, mention that Arachnet Project z.s. is interested in
understanding the process for obtaining a namespace identifier for potential
future extension authoring — specifically for musculoskeletal disorders
relevant to physiotherapy and concepts specific to visually impaired
healthcare professionals.

---

## Project Context for UZIS

Arachnet Project z.s. is a Czech non-profit organisation building a clinical
terminology embedding platform using SNOMED CT on Oracle Database 23ai. The
platform is intended to support clinical decision support tools for Czech
healthcare, with a particular focus on accessibility for visually impaired
healthcare professionals. The Czech national extension is an important
component for making the platform relevant to Czech clinical practice.

SNOMED CT is used under affiliate licence administered by UZIS.

---

## Key Identifiers (to be completed)

| Item | Value |
|------|-------|
| Czech language refset SCTID | to be filled after first load |
| Czech extension moduleId(s) | to be confirmed with UZIS |
| Czech extension release schedule | to be confirmed with UZIS |
| MLDS package identifier | to be confirmed |

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.

Czech national SNOMED CT affiliate licence administered by UZIS.
