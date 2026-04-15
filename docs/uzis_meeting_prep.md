# Meeting Preparation — UZIS Online Meeting
## Czech SNOMED CT National Extension
## Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-04-10
**Participants:** Jan Mura (Arachnet Project z.s.)
                 MUDr. Irena Molinari (UZIS)
                 Mr. Zvolský (UZIS, Department of Standardisation)

---

## Before the Meeting

### Technical preparation

- Have `docs/uzis_correspondence.md` open for reference
- Have `config/ingestion.yaml` open — specifically the
  `national_extensions` section
- Have `config/database.yaml` open — specifically the `tables` section
- Have a text file ready to record answers, identifiers, and commitments

### What to send UZIS before the meeting

Send a brief agenda email so they can prepare:

"Dear MUDr. Molinari and Mr. Zvolský,

Thank you for agreeing to meet. To make our discussion as productive as
possible, here are the main topics I would like to cover:

1. Module identifier (moduleId) for the Czech extension
2. Complete list of reference sets in the current Czech package
3. Release schedule and alignment with SNOMED International
4. Access to the current package for development
5. Process for future release access
6. Brief introduction to the Arachnet project

I look forward to our conversation.

Jan Mura, Arachnet Project z.s."

---

## Opening — Introduction (2 minutes)

Introduce yourself and the project briefly. Keep it to 3 or 4 sentences.
Do not go into technical detail at this stage.

Suggested opening:

"Thank you for your time. I am Jan Mura, founder of Arachnet Project z.s.,
a Czech non-profit organisation. I am building a clinical terminology
embedding platform based on SNOMED CT, intended to support clinical decision
support tools for Czech healthcare. We are particularly focused on
accessibility for visually impaired healthcare professionals, which is also
a personal motivation for me as I am blind myself. The Czech national
extension is an important part of making the platform relevant to Czech
clinical practice, which is why I wanted to speak with you directly."

---

## Topic 1 — Module Identifier (5 minutes)

**What you want to establish:**
Whether the Czech extension moduleId is a stable fixed SCTID that does not
change between releases.

**Open with:**
"I would like to clarify my understanding of the module identifier for the
Czech extension. In SNOMED CT, the moduleId identifies the authoring
organisation and should remain constant across all release versions, while
the effectiveTime on individual components changes with each release.
Is this correct for the Czech extension?"

**If they confirm it is stable:**
"Could you tell me the moduleId SCTID, or confirm it will be included in
the distribution package?"

Record the value immediately.

**If they say it changes:**
"Could you help me understand in what way it changes? I want to make sure
our ingestion pipeline handles it correctly. For example, does the Czech
extension use different modules for different types of content — such as
one module for Czech descriptions and another for Czech-specific concepts?"

**What to record:**
- Czech extension moduleId SCTID (or multiple if several modules are used)
- Whether it is included in the package or needs to be requested separately

---

## Topic 2 — Complete Refset Inventory (5 minutes)

**What you want to establish:**
Which reference sets are in the current Czech package beyond the language
acceptability refset. This affects whether your current 17-table database
structure is sufficient.

**Open with:**
"Your email mentioned that the Czech extension may contain additional
reference sets depending on the release. Could you give me an overview of
which reference sets are currently included? I am particularly interested
in whether there are any national subset refsets, mappings to Czech-specific
classification systems such as DRG codes, or clinical domain groupings."

**Follow-up if they mention a non-standard map format:**
"Could you describe the file format for that mapping? Specifically, does it
follow the standard RF2 simple map or extended map format, or does it use
a different column structure?"

This matters because a non-standard format would require a new table in
your database registry.

**What to record:**
- Complete list of refsets in the current package
- File format for any map refsets
- Whether any refsets use non-standard RF2 formats

---

## Topic 3 — Release Schedule (3 minutes)

**What you want to establish:**
How often the Czech extension is released and how it aligns with the
SNOMED International monthly cycle.

**Open with:**
"SNOMED International now releases monthly. What is the Czech extension
release schedule? Is it released at the same time as the international
release, or on a separate cycle?"

**Follow-up:**
"When a new international release is published, how long does it typically
take for the corresponding Czech extension release to follow?"

**What to record:**
- Czech extension release frequency (monthly, quarterly, other)
- Alignment or offset relative to international release
- Typical lag time between international and Czech release

---

## Topic 4 — Current Package Access (3 minutes)

**What you want to establish:**
Whether you can obtain the current Czech extension package now for
development and testing before production deployment.

**Open with:**
"For development and testing purposes, it would be very helpful to have
access to the current Czech extension package. Is this possible through
the MLDS portal, or would you send it directly?"

**What to record:**
- How to obtain the current package
- Any conditions or steps required for access
- Package format (zip file, specific folder structure)

---

## Topic 5 — Future Release Access (2 minutes)

**What you want to establish:**
The standard process for accessing future releases once the platform is
in production.

**Open with:**
"For our production system, we will need to update the Czech extension
with each new release. What is the recommended process — downloading from
the MLDS portal, a direct download link, or another channel?"

**What to record:**
- Standard access process for future releases
- Whether a standing agreement or annual renewal is required
- Any notification process beyond the email list we discussed

---

## Topic 6 — Namespace for Future Extension Authoring (optional, 3 minutes)

**Raise this only if the conversation is going well and time permits.**
Do not raise it as a commitment — frame it as interest in understanding
the process.

**Open with:**
"One longer-term question — Arachnet is interested in potentially
contributing new SNOMED CT content in the future, specifically for
musculoskeletal disorders relevant to physiotherapy and for concepts
related to visually impaired healthcare professionals. Could you briefly
explain what the process would be for obtaining a namespace identifier
for extension authoring? We are not ready to start this immediately, but
we would like to understand the pathway."

**What to record:**
- Process for obtaining a namespace
- Role of UZIS vs SNOMED International in the process
- Any prerequisites or requirements

---

## Closing (2 minutes)

Summarise the key outcomes and confirm next steps.

"Thank you both for your time. To summarise what we have agreed:

- [state the moduleId or confirm it will be in the package]
- [state the refset list or confirm you will receive documentation]
- [confirm the release schedule]
- [confirm how to access the current package]
- [confirm the notification list registration]

Are there any other points you would like to raise or any information
about the Czech extension that would be useful for our project?"

Close with:

"I will send you a brief summary of our discussion by email after the
meeting. Thank you again for your support — the Czech national extension
is an important part of making this platform genuinely useful for Czech
healthcare."

---

## After the Meeting

### Immediately after

Write up the key information recorded during the meeting while it is
fresh. Do not rely on memory.

Update `docs/uzis_correspondence.md` with:
- Czech extension moduleId(s)
- Complete refset list
- Release schedule
- Package access method
- Any other identifiers or commitments

### Within 24 hours

Send a follow-up email to MUDr. Molinari and Mr. Zvolský summarising
the discussion and confirming any commitments made on both sides.

Template:

"Dear MUDr. Molinari and Mr. Zvolský,

Thank you for today's meeting. I would like to confirm the key points
we discussed:

1. [moduleId confirmation]
2. [refset list or reference to documentation they will send]
3. [release schedule]
4. [package access]
5. [notification list]

Please let me know if I have misunderstood anything or if there is
anything to add.

With kind regards,
Jan Mura
Arachnet Project z.s."

### Update project configuration

Once you have the moduleId and the package:

1. Update `ingestion.yaml` — fill in `national_extensions.extensions`:
   - `module_id` — Czech extension moduleId SCTID
   - `language_refset_id` — Czech language refset SCTID
   - `rf2_folder` — path to Czech package under data volume
   - `files` — list of RF2 files in the package

2. Update `database.yaml` if any new table entries are needed for
   non-standard Czech refsets.

3. Update `docs/uzis_correspondence.md` key identifiers table.

4. Commit all changes:
   ```
   git add config/ingestion.yaml config/database.yaml
   git add docs/uzis_correspondence.md
   git commit -m "chore: update Czech extension config after UZIS meeting"
   git push
   ```

---

## Quick Reference — Key Questions

If the conversation goes off track, return to these five questions:

1. Is the Czech moduleId a stable fixed SCTID? What is it?
2. What refsets are in the current Czech package beyond language?
3. What is the Czech extension release schedule?
4. How do I access the current package for development?
5. How do I access future releases in production?

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.

Czech national SNOMED CT affiliate licence administered by UZIS.
