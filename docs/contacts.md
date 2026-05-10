# docs/contacts.md
# ============================================================
# Arachnet Clinical Terminology Embeddings — Project Contacts
# Version: 1.0
# Last updated: 2026-05-09
# ============================================================

## Oracle

| Name | Email | Role | Notes |
|------|-------|------|-------|
| Slavomír Seno | slavomir.seno@oracle.com | Oracle support engineer | Primary technical contact, very helpful |
| Viktor Nemec | viktor.nemec@oracle.com | Oracle support | On the 26ai patch thread |
| Filip Rodr | filip.rodr@oracle.com | Oracle support | On the 26ai patch thread |

### Oracle notes
- Oracle support has been responsive and helpful throughout
- 26ai patch attempt 2026-05-09: APPLY failed, Slavomír informed
- Correct CLI mechanism for Base DB System patching documented in
  docs/runbooks/patch_26ai.md

---

## UZIS (Ústav zdravotnických informací a statistiky ČR)

National Institute of Health Information and Statistics.
Official authority for SNOMED CT in the Czech Republic.

| Name | Email | Role | Notes |
|------|-------|------|-------|
| MUDr. Irena Molinari | unknown | Head of Czech SNOMED CT translation | Direct contact, medical doctor |
| MUDr. Miroslav Zvolský | Miroslav.Zvolsky@uzis.cz | Head of standardisation department | Molinari's boss, more technically aware |

### UZIS notes
- UZIS is the official national SNOMED CT authority for Czech Republic
- Czech translation status: in progress, release date unknown
- Translation covers: FSN, PT, additional synonyms
- Other refsets: not created
- RF2 package: does not exist yet
- Access when released: unrestricted
- Quality: variable — multiple agencies worked on translation
- Development sample requested 2026-05-09 (email to Molinari, CC Zvolský)
- Confidentiality commitment made: no publication before official release

### Meeting history
- ~2025: Jan offered help with RF2 packaging — declined by UZIS
- 2026: Phone/online conversation with MUDr. Molinari
  - Confirmed translation scope: claimed all international concepts
  - Confirmed elements: FSN, PT, synonyms
  - No other refsets planned
  - Release timeline: vague, unknown even to Molinari
  - No follow-up meeting scheduled

---

## Arachnet Project z.s.

| Name | Email | Role |
|------|-------|------|
| Jan Mura | jan.mura@volny.cz | Owner, sole developer |

---

## SNOMED International

- Website: https://www.snomed.org
- Release notifications: Arachnet added to release notification list (confirmed by Molinari)
- Namespace process for Czech extension authoring: open question, not yet initiated
