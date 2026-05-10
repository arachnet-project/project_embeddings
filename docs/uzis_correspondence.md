# docs/uzis_correspondence.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — UZIS Correspondence
# Version: 1.1
# Last updated: 2026-05-09
# ============================================================

## Overview

UZIS (Ústav zdravotnických informací a statistiky ČR) is the official
national authority for SNOMED CT in the Czech Republic. This document
records all correspondence and meeting notes relevant to the Arachnet
project.

---

## Contacts

- MUDr. Irena Molinari — head of Czech SNOMED CT translation
- MUDr. Miroslav Zvolský — head of standardisation, Molinari's boss
  miroslav.zvolsky@uzis.cz

See docs/contacts.md for full contact details.

---

## Czech SNOMED CT Translation — current state (as of 2026-05-09)

### What is confirmed
- Translation scope: all international SNOMED CT concepts (claimed,
  not precisely confirmed)
- Translated elements: FSN (Fully Specified Names), PT (Preferred Terms),
  additional synonyms
- Multiple agencies worked on the translation — quality may vary
- Language refset: exists, language code and publisher ID (ModuleId)
  provided by Molinari
- Other refsets: not created
- UZIS is the official national authority — release will be unrestricted

### What is unclear
- Exact number of translated concepts
- Whether all concepts are translated or only a clinical subset
- RF2 packaging status — translation exists somewhere but has not
  been assembled into RF2 format files
- Release date — unknown even to Molinari, could be months or over a year
- QA process — unclear if unified quality review was done across agencies
- Whether SNOMED International has officially registered the Czech extension

### Key risk for Arachnet
Czech language features cannot be built or tested until the RF2 package
exists. This is an external dependency outside Arachnet's control.
Development continues against the international English release.

---

## Meeting / Conversation History

### ~2025 — Initial meeting (Jan, Molinari, Zvolský)
- Jan offered help with RF2 packaging and technical work
- UZIS declined — they have internal resources
- Relationship remains cordial

### 2026 — Conversation with MUDr. Molinari
- Molinari confirmed translation scope and elements (see above)
- Release date: vague, no commitment
- No follow-up meeting scheduled
- Molinari was open but not precise about technical details
- Impression: the RF2 packaging work has not started or is very early

---

## Correspondence

### 2026-05-09 — Email to Molinari (draft)
Subject: Czech SNOMED CT translation — request for development sample
CC: MUDr. Zvolský

Request for a draft or partial sample of translation files for
development purposes. Confidentiality commitment included:
material will not be published or shared before official release.
Also offered help with RF2 packaging if useful to UZIS.

Status: draft, not yet sent. Molinari's email address unknown —
check email history or ask Zvolský.

---

## Open Questions

1. Can UZIS provide a development sample before official release?
2. What is the realistic release timeline?
3. Is the Czech extension officially registered with SNOMED International?
4. What is the complete refset inventory?
5. What is the ModuleId (SCTID) for the Czech extension?
6. Release schedule relative to SNOMED International releases?
7. Namespace process for Arachnet extension authoring?
