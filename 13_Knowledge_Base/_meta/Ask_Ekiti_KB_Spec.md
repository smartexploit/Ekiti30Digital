# Ask Ekiti — Knowledge Base Design (v0.3)

**Owner:** Member 3, AI & Data Lead
**Related issue:** #3  |  **Pull request:** #11
**Status:** Revised draft, updated after review. Not approved. Nothing here is merged to `main`. PR #11 stays open until the final approval review.
**Companion file:** `Ask_Ekiti_Source_Inventory.xlsx`

**How this document is organised**

- **Part A** is the knowledge base itself: content rules, sources, verification and how Ask Ekiti may answer. It is independent of any technology.
- **Part B** is a *non-binding* implementation proposal. Member 2 keeps the freedom to decide the final backend.
- **Part C** is the decision record: what the team has confirmed and what is still open.

## Changes from v0.1

| Review point | Where addressed |
|---|---|
| 1. Define "verified"; official sources first; conflicts flagged, not overridden | A5, A6 |
| 2. Tier C: multiple sources by default, documented exceptions allowed | A7 |
| 3. Future-dated example verification date | A3 (placeholder, plus a validation rule) |
| 4. Separate KB structure from implementation | Part A vs Part B |
| 5. Connect KB to folders `01_History` to `14_Source_Documents`, avoid duplicates | A2 |
| 6. Verification authority model | A8 |
| 7. Traceable source inventory, primary vs secondary | A4 and the spreadsheet |
| 8. No unsupported model-generated facts; say when knowledge is insufficient | A1, A9 |

## Changes in v0.3 (team decisions and workbook alignment)

| Change | Where |
|---|---|
| Verification Lead named (Member 8, Victor Ogunyemi); senior reviewer named (Member 1, Faith Ogunlade); Yoruba reviewer role added | A8 |
| Government content confirmed under `01_History/government/`; pre-1996 background included at launch and kept separate from the timeline | A2, A10 |
| English and Yoruba supported; new answer rule and front-matter fields | A3, A9 (rule 9), A11, B1 |
| Tier D (oral/community) not used at launch | A4, A5 |
| Source-record fields and status meanings aligned with the workbook | A4 |
| Part C converted into a decision record | Part C |

---

# PART A — The Knowledge Base

## A1. Principles

1. **No source, no fact.** Every factual statement traces to a registered source that another person can find and check.
2. **Verified only.** Ask Ekiti uses only documents whose status is `verified`.
3. **No unsupported model output.** Ask Ekiti must never present model-generated or unsupported information as fact. The language model's general knowledge is not a source.
4. **Say when knowledge is insufficient.** If the verified KB cannot adequately support an answer, the assistant says so. It does not guess or fill gaps.
5. **Official sources first, but not blindly.** Official and primary sources have priority, yet a documented conflict always goes to review (A6).
6. **Small and right beats big and wrong.** Launch with a small verified set and grow it.
7. **Facts and opinion stay separate.** Citizen stories and Ekiti 2056 visions are not facts and are not used for factual answers.

---

## A2. How research enters the KB (no duplicate copies)

**Rule: write once, reference everywhere.** A source or a fact lives in one place. Everything else links to it by ID.

**Flow**

```
Original source
   → 14_Source_Documents   (stored once; given a Source ID, e.g. SRC-004; listed in the Source Inventory)
   → 15_Research_Notes     (optional working notes; never used by Ask Ekiti)
   → topic file in 01–09   (the canonical content; cites Source IDs; standard front matter)
   → review (A8)           (status becomes verified only after review)
   → KB manifest in 13     (list of verified files that Ask Ekiti may use)
   → Ask Ekiti
```

**Role of each folder** (confirmed by the team)

| Folder | Role | Used by Ask Ekiti? |
|---|---|---|
| `01_History` | Topic files: history and state creation; government content in `01_History/government/`; pre-1996 background in `01_History/pre-1996/` | Yes, once verified |
| `02_LGAs` | One file per LGA | Yes, once verified |
| `03_Timeline` | One file per timeline event, 1996–2026 only | Yes, once verified |
| `04_Tourism` | Sites and attractions | Yes, once verified |
| `05_Culture` | Festivals, traditions, languages | Yes, once verified |
| `06_Education` | Institutions and education facts | Yes, once verified |
| `07_Health` | Facilities and health facts | Yes, once verified |
| `08_Agriculture` | Crops, programmes, facts | Yes, once verified |
| `09_Statistics` | Datasets and statistical summaries | Yes, once verified |
| `10_Photographs` | Images. Captions may cite sources | No (media, not facts) |
| `11_Citizen_Stories` | Unverified submissions | No |
| `12_Ekiti_2056` | Citizen visions | No |
| `13_Knowledge_Base` | This spec, the file template, the manifest and the source-registry export. **Holds no copies of content.** | n/a |
| `14_Source_Documents` | Original sources (PDFs, scans, datasets) stored once, each with a Source ID | Referenced, never copied |
| `15_Research_Notes` | Working notes. Facts are promoted into a topic file only after sources are registered | No |
| `16_Media`, `17_Design`, `18_Project_Documentation` | Not KB content | No |

**Rules to prevent duplication**

1. **Sources:** store each original once in `14_Source_Documents` (or link to the URL if we do not keep a copy). One row per source in the Source Inventory. Topic files refer to it by `SRC-###`, and never paste its full text.
2. **Content:** the topic file in `01`–`09` *is* the KB document. There is no second copy in `13`.
3. **Manifest:** `13_Knowledge_Base/kb_manifest.csv` lists each KB document (id, path, status, verification date). It is generated from the files' front matter by a script, so nobody maintains it by hand. Ask Ekiti uses only rows with status `verified`.
4. **Timeline events:** the file in `03_Timeline` is the canonical record. The website's timeline data is generated from it and is not typed a second time.
5. **Check before you create:** before starting a new source record or topic file, search the Source Inventory and manifest. The pull-request checklist includes "no duplicate source or document".
6. **Government content** (governors, administrators, ministries, laws, institutions) lives in `01_History/government/` (confirmed by the team).
7. **Pre-1996 background** lives in `01_History/pre-1996/`, is marked `period_covered: pre-1996` and `doc_type: background`, and is kept out of the 1996–2026 timeline: no files in `03_Timeline` and no timeline-event records.

---

## A3. Document format

Each KB document is a Markdown file with YAML front matter. Fields marked required must be present.

```yaml
---
id: lga-example                 # required, unique
title: Example title            # required
category: lgas                  # required: history | government | lgas | tourism | culture | education | agriculture | health | statistics
doc_type: entity                # entity | event | dataset | background
source_ids: [SRC-000]           # required; every ID must exist in the Source Inventory
source_name: <from registry>    # required for display; must match the registry
source_url: <from registry>     # required for display; must match the registry
publication_date: YYYY-MM-DD    # date the source was published
source_tier: A                  # A | B | C | D (see A4)
status: draft                   # draft | needs_review | conflict | verified | retired
verified_by:                    # blank until verified; never the author
last_verified: YYYY-MM-DD       # PLACEHOLDER. Set only when a real verification is finished
verification_note:              # required for Tier C exceptions, Tier D, and resolved conflicts
tier_c_exception: false         # true only with a recorded reason (A7)
period_covered: 1996-2026       # use pre-1996 for pre-1996 background documents
language: en                    # en | yo (language of the body text)
translation_of:                 # for a Yoruba translation: id of the English original
translation_reviewed_by:        # Yoruba reviewer (see A8); blank until reviewed
lgas: []
tags: []
---
```

**Date rule:** `last_verified` is the actual date the verification was completed. It is filled in by the reviewer, never by the author, and never with a future date. A document cannot be marked `verified` while the field still holds the placeholder or a date after today. The validation script rejects both.

**Body:** a short summary, the facts (each traceable to a Source ID), and a source list. The Source Inventory is the single source of truth for source details, so the front-matter copies must match it.

**Copyright:** store short summaries and structured facts with links. Do not paste full articles.

---

## A4. Sources: class and tier

Every source is recorded as **primary/official**, **secondary**, or **oral/community**, and given a reliability tier.

| Tier | Class | Meaning | Examples |
|---|---|---|---|
| **A** | Primary / official | Issued by the body responsible for the record | Constitution, gazettes, census tables from the National Population Commission, state government statements, INEC declarations, regulator lists |
| **B** | Secondary | Academic or institutional analysis | University publications, peer-reviewed work, agency reports, published histories |
| **C** | Secondary | News and general secondary reporting | National newspapers, established outlets |
| **D** | Oral / community | Elders, palace records, local knowledge | Interviews, community accounts. **Not used at launch** (team decision); to be introduced in a later phase once the verification and attribution workflow is mature |

**Not accepted as KB sources:** Wikipedia and other wikis or tertiary summaries, AI-generated text, and unsourced social media posts. They may be used to find leads, but the lead must be traced to a real source before use.

**Cautions**

- **Official website does not mean every page is official.** A reader's letter or comment hosted on a government site is not an official statement. Record the type of page.
- **A copy is not the original.** If an official document is found on another site, record both the original publisher and where the copy is hosted. Check that the copy is the current version (for example, the Constitution has been amended).
- **Provisional vs final.** Statistics and results may exist in provisional and final versions. Record which one was used.

**What every source record must let a colleague trace** (Source Inventory columns): source ID, record stage (identified or source needed), title, source type, primary/secondary/oral, publisher or owner, URL or document location, whether that location is the original or a hosted copy (and the host), publication date of the source, tier, topic/category, status, verification date, verifier, corroboration (Tier C), verification note, and conflicts or notes.

For a *source record*, "Verified" means a reviewer opened the source and confirmed its title, publisher, location, class and tier, and that it is the authentic, current version. Verification of a *document's claims* (A5) is recorded in the document's front matter. Tier D sources must not appear in the launch inventory as anything other than deferred (priority P3).

---

## A5. What "verified" means

A document may be marked `verified` only when **all** of these are true:

1. **Sources registered.** Every source has a Source Inventory record with title, type, class, publisher, and URL or location.
2. **Claims traced.** A reviewer opened each source and checked the document's names, dates, numbers and wording against it (not a summary, and not another AI's output).
3. **Tier rule met.** Tier A and B: one qualifying source. Tier C: two independent sources, or a documented exception (A7). Tier D: Verification Lead sign-off (applies only once Tier D is introduced; not used at launch).
4. **Conflict check done.** The reviewer searched for conflicting sources and recorded the result ("none found" or the conflict).
5. **No open conflict.** Any conflict is resolved and recorded (A6), or the document is handled as disputed.
6. **Independent reviewer.** The reviewer is not the author.
7. **Decision recorded.** `verified_by`, a real `last_verified` date, and (where required) a `verification_note` giving the reasoning.
8. **Front matter valid.** The validation script passes.

AI tools may help draft, but AI output is never a source, and anything an AI drafted is checked against the sources like any other text.

**Priority of official sources.** Where an official primary source exists for a type of fact, it is the preferred basis. Examples: constitutional and legal text, election outcomes (INEC declarations, and court judgments where a court changed the outcome), census figures (National Population Commission and its gazettes), and government office holders and dates (state government and gazette records). **A single official source does not automatically settle a question when a documented conflict exists.**

---

## A6. Conflicts

**What counts:** two or more credible sources disagree on a material fact (a date, name, number, or a spelling that changes meaning). This includes two official sources disagreeing with each other.

**Process**

1. **Flag it.** Set the record and document to `conflict`, and describe the disagreement in the Source Inventory notes.
2. **Investigate the cause.** Typical causes: provisional versus final data, different definitions, transcription errors, outdated pages.
3. **Decide.** The Verification Lead decides, and the reasoning is recorded in `verification_note`:
   - **Resolved:** one source prevails, with the reason stated (for example, final results supersede provisional results). The document may then be verified.
   - **Unresolved:** either publish a "sources differ" document that states each position with its citation, or keep the item out of Ask Ekiti.
4. **Ask Ekiti never picks silently.** For a disputed item it presents each position with its source.

**Worked example found while building the inventory:** the 2006 population of Ekiti State is given differently by different sources. The State Government's "About Ekiti" page, a secondary compilation of National Population Commission data, and Wikipedia do not all agree. The primary candidates for settling it are the National Population Commission's 2006 Priority Tables and the Federal Government gazette that published the final census results. The item is marked `Conflict` in the inventory until a reviewer checks them. No figure should be used before then. A second open conflict concerns the names of the early administrators, which differ between the state's own pages and other sources (SRC-010).

---

## A7. Tier C rule

**Default:** Tier C material needs **two or more independent sources**. "Independent" means different publishers doing their own reporting. Two outlets republishing the same press release or wire story count as one.

**Documented exceptions:** one authoritative source may suffice when it is clearly authoritative for that fact (for example, a specialist institutional publication, or a named official statement carried by a reputable outlet when the original is unavailable).

**An exception is valid only if:**

1. the reviewer writes the reasoning in `verification_note`;
2. the Verification Lead approves it;
3. the document is marked `tier_c_exception: true`, so exceptions can be counted and audited; and
4. no conflict exists for that fact.

What matters is that the decision and its reasoning are recorded.

---

## A8. Verification authority (confirmed by the team)

| Role | Who | What they may do |
|---|---|---|
| **Contributor / author** | Anyone on the team | Write drafts and open pull requests. May set `draft` or `needs_review`. Cannot verify their own work. |
| **Reviewer** | Members of the Verification & Editorial team (domain owners may review other teams' documents, not their own) | Check claims against sources. May mark Tier A and B documents `verified` when there is no conflict. |
| **Verification Lead** | **Member 8, Victor Ogunyemi** (agreed by the team for launch) | Decides conflicts, approves Tier C exceptions, and makes source-verification decisions, including "sources differ" documents. Final say on `verified` status. Tier D approvals apply only once Tier D is introduced. |
| **Domain owners** | Research & History, Geospatial, Culture & Tourism, etc. | Advise on accuracy in their area. Not the verifier for their own team's documents. |
| **AI & Data Lead** | **Member 3, Oluwadare Tobi Jayeola** | Validate front matter, generate the manifest, ingest only verified documents. Cannot mark anything `verified`. May pull a document from Ask Ekiti if it fails checks or produces unsafe answers. |
| **Technical Lead / senior reviewer** | **Member 1, Faith Ogunlade** | Senior reviewer for sensitive matters. Maintains the repository. Merges to `main` only after the required verification approval. Settles policy disputes. |
| **Yoruba reviewer** | **Member 1, Faith Ogunlade** | Reviews Yoruba wording and translations for accuracy. Does not verify facts: facts are verified against sources under A5. |

**Rules**

1. **Two-person rule:** author and verifier are always different people.
2. **The approval is the pull-request review** by a Verification-team member, plus the front-matter fields (`verified_by`, `last_verified`, `verification_note`).
3. **Enforcement in GitHub (suggestion):** a `CODEOWNERS` file requiring Verification-team review for `01`–`09` and `13`, and labels such as `needs-verification` and `verified`.
4. **Until the team has at least two verifiers**, a reviewer from another team acts as second reviewer for Tier A and B, and the Verification Lead handles everything else.
5. **Sensitive matters** are referred by the Verification Lead to the senior reviewer before a document is marked `verified`.
6. **Nothing is merged to `main` until the final approval review is complete.** PR #11 stays open.

---

## A9. Answer rules for Ask Ekiti (the content contract)

These rules apply to any implementation.

1. **Only verified content.** Answers come only from verified KB documents and structured data derived from them.
2. **No unsupported facts.** The assistant must not present model-generated or unsupported information as fact.
3. **Cite every factual claim.** Show the source, its class and tier, and the last-verified date.
4. **Insufficient knowledge.** If the verified KB cannot adequately support an answer, the assistant says that the available verified knowledge is insufficient. It does not invent or approximate an answer. Suggested wording: *"The available verified knowledge isn't enough to answer that yet."* It may invite the user to contribute information.
5. **Partial support.** Answer the supported part and say plainly that the rest is not covered.
6. **Conflicts.** Present each position with its source and state that sources differ.
7. **Time.** State the date the information was last verified and flag older items.
8. **Exclusions.** Citizen stories and Ekiti 2056 submissions are not used for factual answers.
9. **Language.** Ask Ekiti answers in English or Yoruba. A Yoruba answer must be based only on verified content, keep the same citations (source titles are not translated or altered) and the same insufficient-knowledge behaviour, and must not add facts or change any name, date or figure. Yoruba wording is treated as not yet human-reviewed until a Yoruba reviewer is assigned (A8).

**Answer format**

> [Answer in plain language.]
> **Source:** [title], [publisher], [URL] — [primary/secondary], Tier [X], last verified [date].

---

## A10. First documents

The launch set, with candidate sources and traceable source records, is in the spreadsheet (sheets **Source Inventory** and **First Documents**). In priority order:

1. State creation, 1 October 1996
2. The 16 LGAs (names, headquarters, coordinates)
3. Governors and administrators, 1996–2026
4. Population (blocked until the 2006 conflict in A6 is resolved)
5. Tourism sites
6. Universities and other tertiary institutions
7. Hospitals and health facilities
8. 30–50 timeline milestones
9. Education, economy and agriculture statistics
10. Pre-1996 background (small set, kept separate from the 1996–2026 timeline)
11. Cultural festivals and traditional councils

Launch target: 16 LGA files, 30–50 event files, 20–30 place files, and 15–25 other documents.

---

## A11. Evaluation

Build a **golden set of about 50 questions** before launch, in both English and Yoruba: answerable, unanswerable, false-premise, out-of-scope, conflicting-source and prompt-injection questions. A starter set, including Yoruba tests, is in the sheet **Eval Starter Set**.

**Measures:** citation correctness, groundedness (every claim supported by retrieved text), correct handling of "insufficient knowledge", correct handling of conflicts, and answer accuracy. Run the set after any change to the KB or the assistant's prompt or configuration.

---

# PART B — Implementation proposal (non-binding)

**Status:** This part is a suggestion only. **Member 2 has freedom to decide the final backend.** Part A does not depend on anything in Part B, and any implementation that meets the contract below is acceptable.

## B1. What any implementation must satisfy

1. Use only documents listed in the manifest with status `verified`.
2. Keep each retrievable passage linked to its document ID and source metadata.
3. Return citations with every factual answer (A9).
4. Return the "insufficient knowledge" response when support is inadequate.
5. Present both positions for conflicting or disputed items.
6. Re-ingest changed documents, and drop retired ones.
7. Keep an audit trail (which document versions an answer used).
8. Support English and Yoruba questions and answers under rule A9.9.

## B2. Suggested approach (one option)

- **Storage:** PostgreSQL with the planned `knowledge_documents` table, plus a `knowledge_chunks` table (document ID, chunk index, text, embedding).
- **Retrieval:** hybrid search (Postgres full-text plus vector similarity, for example with pgvector), filtered to `status = verified`.
- **Structured facts** (LGAs, office holders, dates) answered by direct table lookup rather than similarity search.
- **Chunking:** split by heading or fact group; each chunk inherits its document's metadata.
- **Guardrails:** a minimum-relevance threshold that triggers the insufficient-knowledge response; a prompt that restricts the model to retrieved passages; a post-check that every citation refers to a retrieved document.
- **Ingestion script:** validate front matter, reject missing required fields, placeholder or future dates on verified documents, and Source IDs not in the registry; generate the manifest; re-embed only changed files.

## B3. Acceptable alternatives

Any comparable design is fine, for example a different vector store, a managed search service, or a simpler keyword-only start for the MVP, as long as B1 is met.

---

# PART C — Decision record

Decisions confirmed by the team and relayed by Member 3. They are reflected in the sections shown.

| # | Decision | Outcome | Where reflected |
|---|---|---|---|
| 1 | Verification authority | **Confirmed.** Verification Lead: Member 8, Victor Ogunyemi (conflict decisions, Tier C exceptions, source-verification decisions). Senior reviewer for sensitive matters: Member 1, Faith Ogunlade (Technical Lead). | A8 |
| 2 | Folder mapping and government content | **Confirmed.** Government-related historical and reference content (governors, ministries, laws, institutions) lives in `01_History/government/`. | A2 |
| 3 | Pre-1996 background at launch | **Yes.** A small verified set is included at launch, kept clearly separate from the 1996–2026 timeline (`01_History/pre-1996/`, not in `03_Timeline`). | A2, A10 |
| 4 | Launch language | **English + Yoruba.** The reviewer has now been formally assigned, **Member 1, Faith Ogunlade** as the Yoruba Reviewer. | A3, A8, A9 (rule 9), A11 |
| 5 | Tier D (oral/community) sources | **Not at launch.** No Tier D material in the initial verified KB. To be introduced in a later phase once the verification and attribution workflow is mature. | A4, A5 |
| 6 | Backend implementation | **Member 2's engineering decision.** Part B remains a non-binding proposal. | Part B |

**Still open**

- Formal assignment of the Yoruba reviewer.
- Member 2's backend decision.
- Final approval review of this specification and the source-inventory workbook. PR #11 stays open, and nothing is merged to `main` until then.

## Suggested sequence for the launch sprint

| Days | Work |
|---|---|
| 1–2 | Team completes the Source Inventory (P1 blockers first). Verification Lead resolves the two open conflicts (A6). |
| 2–4 | Collect and verify the launch documents (LGAs, state creation, governors first). |
| 3–5 | Validation script and manifest. Backend integration per Member 2's design. |
| 5–6 | Connect Ask Ekiti with citations and the insufficient-knowledge response. Run the golden set. |
| 7 | Fix failures, freeze the launch KB, document how to contribute. |

The source inventory comes before any backend code, as the master overview requires.
