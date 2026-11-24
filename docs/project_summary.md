# ARC_FILE: docs/project_summary.md
# ACE — Project Summary

**Updated:** 2026-11-24
**Session close-out:** Pending review, commit, push, and verification
**Prepared by:** Current assistant; based on repository output and information supplied by Jan Mura
**Current phase:** Phase 0 — Foundation and Infrastructure
**Phase status:** In progress

---

## Project context

Arachnet Clinical Embeddings (ACE) is a SNOMED CT terminology and semantic-search project using Oracle, Python, and Bash. It is owned by Arachnet Project z.s. and developed by Jan Mura. ANTHEA is the parallel theoretical project.

The project is governed by `docs/dev_workflow.md` and the two control documents `docs/project_summary.md` and `docs/todo.md`. Phase 0 remains in progress. The interrupted Step 0.6 `--real-db` design work remains the next engineering priority after this post-workshop documentation close-out.

## Scope of this update

This update records the completed SNOMED CT vocabulary work, the outcome of the UZIS workshop on 2026-11-23, and the agreed return to Phase 0 engineering after the post-workshop control-document close-out.

## Work completed

### SNOMED CT vocabulary

`docs/snomed_vocabulary.md` was updated from version 0.4 to version 0.5, dated 2026-11-17. It contains the reviewed glossary entries for SNOMED CT concepts, descriptions, expressions, relationships, reference sets, and the Machine Readable Concept Model (MRCM).

Jan approved the vocabulary changes, including the flat entry structure with the previous broad section headings removed. The repository now reports HEAD `584045f2ca8dd9fc172ff9ef7eca1d235281780e`, with commit message `docs: update SNOMED vocabulary for UZIS workshop`. The 2026-11-24 repository check showed a clean working tree on `main`, aligned with `origin/main`.

### UZIS workshop

Jan attended the UZIS workshop “Implementace SNOMED CT” on 2026-11-23. He could not pose his prepared questions during the session because VoiceOver was turned off so as not to disturb the presentation, and he therefore could not enter the questions in the Teams chat.

A SNOMED International representative invited follow-up contact. The representative also mentioned user groups, but it was not clear whether the relevant group already exists or is still planned. Jan intends to ask MUDr. Irena Molinari at UZIS for the appropriate SNOMED International contact and clarification.

The workshop raised questions about storing SNOMED CT release content in a database and automating the release-ingestion process. The exact process discussed was not confirmed. ACE’s Phase 1 planning should clarify supported release checking and downloads, the Oracle import and storage design, and any applicable licensing conditions before commercial use.

## Decisions and current direction

* The UZIS vocabulary update is completed and recorded in `docs/snomed_vocabulary.md`; its material outcome is preserved in this summary.
* The post-workshop follow-up is recorded in `docs/todo.md`. No response from UZIS or SNOMED International has yet been recorded.
* Phase 0 remains the immediate engineering priority. The workshop follow-up and Phase 1 ingestion questions do not expand Step 0.6 or block its completion.
* Phase 1 planning must address loading RF2 release content into ACE’s queryable Oracle store. RF2 is the release distribution input; the detailed automated ingestion process remains to be designed and verified.
* No code or tests were changed or run as part of the post-workshop documentation work.

## Repository state

At the 2026-11-24 check, the repository was `/home/jan/project_embeddings` on Ubuntu, branch `main`, at:

    584045f2ca8dd9fc172ff9ef7eca1d235281780e

The working tree was clean, and `main` was aligned with `origin/main`. This status was checked before the post-workshop control-document edits in this summary and `docs/todo.md`.

## Unresolved work

The following remain recorded in `docs/todo.md`:

* Finish the `--real-db` design and implementation work for Step 0.6.
* Resolve the OCI Python environment discrepancy and the Oracle Thin-mode/NNE question.
* Review the available Step 0.5 real-Oracle verification evidence.
* Prepare and send the UZIS follow-up email, then record any confirmed contact, user-group, or implementation guidance.
* Plan Phase 1 SNOMED CT release ingestion, Oracle storage, supported automation, and applicable licensing.

## Immediate next step

Review the updated `docs/project_summary.md` and `docs/todo.md` against the development workflow and repository state. Then commit and push the approved control-document changes from Ubuntu and verify the resulting repository state. After this close-out, open a separate engineering session and resume the `--real-db` design in `docs/todo.md` §2.2.
