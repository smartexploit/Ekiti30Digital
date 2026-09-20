# Ask Ekiti — Knowledge Base Design (v0.1)

**Owner:** Member 3, AI & Data Lead
**Status:** Draft for founding-team review
**Companion file:** `Ask_Ekiti_Source_Inventory.xlsx` (source inventory, first documents, evaluation starter set)

---

## 1. Principles

1. **No source, no fact.** Every factual statement in the knowledge base (KB) traces to a named, checkable source.
2. **Verified only.** Ask Ekiti retrieves from documents with `status: verified`. Drafts never reach the assistant.
3. **Refuse rather than guess.** If nothing verified supports an answer, Ask Ekiti says so. It never falls back on the LLM's general memory.
4. **Small and right beats big and wrong.** Launch with a small verified set and grow it.
5. **Separate facts from opinion.** Citizen stories and Ekiti 2056 visions are not facts and are not in the KB index at launch.

---

## 2. Directory structure

```
knowledge/
├── _meta/
│   ├── KB_SPEC.md              (this document)
│   ├── document_template.md
│   └── source_inventory.csv    (exported from the spreadsheet)
├── history/        state creation, era summaries, milestones, pre-1996 background
├── government/     governors/administrators, MDAs, laws, budgets
├── lgas/           one file per LGA (16 files)
├── tourism/        one file per site or cluster
├── culture/        festivals, traditional councils, languages, food, arts
├── education/      institutions, statistics
├── agriculture/    crops, programmes, statistics
├── health/         facilities, programmes, statistics
└── statistics/     population, economy, poverty, other datasets
```

**Naming:** `category/slug.md`, lowercase, hyphenated. Examples: `history/state-creation-1996.md`, `lgas/ado-ekiti.md`.

**One file, one topic.** A file covers one entity, event or dataset so it can be cited precisely and re-verified independently.

---

## 3. Document format

Markdown with YAML front matter.

```markdown
---
id: lga-ado-ekiti
title: Ado-Ekiti Local Government Area
category: lgas
doc_type: entity            # entity | event | dataset | background
source_name: Constitution of the Federal Republic of Nigeria, First Schedule
source_url: https://...
archive_url: https://web.archive.org/...   # snapshot, so citations survive link rot
source_tier: A              # A | B | C | D  (see section 4)
publication_date: 1999-05-29
last_verified: 2026-09-21
verified_by: <name or handle>
status: draft               # draft | needs_review | verified | retired
period_covered: 1996-2026
lgas: [ado-ekiti]
tags: [lga, headquarters]
---

## Summary
Two to three sentences, self-contained.

## Facts
- Each fact as its own line, with an inline source key if it differs from the file-level source. [S1]

## Sources
- [S1] Full citation, URL, access date.
```

Required by the master overview: title, content, source, source URL, publication date, last-verified date, category. This design adds `id`, `doc_type`, `source_tier`, `status`, `verified_by`, `archive_url`, `period_covered`, `lgas` and `tags` for filtering and audit.

**Copyright:** store summaries and structured facts with links. Do not paste full articles.

---

## 4. Source tiers

| Tier | Meaning | Examples | Rule |
|---|---|---|---|
| **A** | Official or primary | Constitution, gazettes, state government, INEC, NBS, NPC | One source suffices |
| **B** | Academic or institutional | Universities, NUC, research institutes, agency reports | One source suffices if the author or institution is named |
| **C** | Reputable news or secondary | National newspapers, established outlets | Two independent agreeing sources |
| **D** | Oral or community knowledge | Elders, palace records, local historians | Verification-team sign-off plus a written corroboration where possible; always labelled as such in answers |

Ask Ekiti shows the tier with the citation so users can judge reliability.

---

## 5. Lifecycle

`draft` → `needs_review` → `verified` → (indexed for Ask Ekiti)

- **Contributor** writes the file and opens a pull request.
- **Verification team** checks each fact against its source and sets `verified_by` and `last_verified`.
- **AI & Data** ingests only `verified` files.
- **Re-verification:** volatile facts (office holders, statistics) get re-checked on a schedule. Files not verified in 12 months are flagged.
- **Retired:** superseded or disproven documents are kept for audit but excluded from retrieval.

The founding meeting must decide who has authority to mark a document `verified` (agenda item 10 in the master overview).

---

## 6. Structured data vs narrative text

| Question type | Handled by | Example |
|---|---|---|
| Entity facts | SQL lookup on `lgas`, `places`, `timeline_events` | "What is the headquarters of X LGA?" |
| Narrative or explanatory | Retrieval over KB chunks | "Tell me about the Ikogosi Warm Springs" |
| Mixed | Structured facts plus retrieved context | "Which LGAs have universities?" |

Structured tables and the KB share one `sources` record so a fact is never cited two different ways.

---

## 7. Retrieval and answering

**Pipeline** (from the master overview, refined): Question → FastAPI → query router → retriever → verified chunks → LLM → answer + sources → citation check.

1. **Router** decides structured lookup, narrative retrieval, or both.
2. **Retriever** uses hybrid search: Postgres full-text plus pgvector similarity, filtered to `status = verified`.
3. **Threshold:** if the best score is below a set value, return the refusal answer.
4. **Prompt rules:** answer only from the supplied documents; cite by document id; do not add outside facts; state uncertainty where sources disagree.
5. **Citation check (post-processing):** every cited id must be in the retrieved set. Otherwise the answer is discarded and regenerated or refused.

**Answer format**

> Ekiti State was created on 1 October 1996.
> **Source:** *[source name]*, [URL] — Tier A, last verified [date].

**Refusal format**

> I don't have a verified source for that yet. You can help by contributing information at [contribution link].

**Chunking:** split by heading or fact group (roughly 200–400 tokens). Each chunk inherits the parent's metadata (`id`, `source_name`, `source_url`, `source_tier`, `last_verified`).

---

## 8. Database mapping

`knowledge_documents` (as planned) holds one row per file:
`id, slug, title, category, doc_type, content, source_name, source_url, archive_url, source_tier, publication_date, last_verified, verified_by, status, period_start, period_end, lgas[], tags[], file_hash, updated_at`

Add `knowledge_chunks`: `id, document_id, chunk_index, text, embedding (pgvector)`.

Ingestion script: read files, validate front matter (reject if a required field is missing), hash the file, upsert changed documents, re-embed changed chunks only.

---

## 9. First documents

Full list with candidate sources, tiers and owners is in the spreadsheet (sheet **Source Inventory**). Launch set, in priority order:

1. State creation, 1 October 1996
2. The 16 LGAs (names, headquarters, coordinates)
3. Governors and administrators, 1996–2026
4. Population (2006 census; projections labelled as projections)
5. Tourism sites
6. Universities and other tertiary institutions
7. Hospitals and health facilities
8. Education, agriculture and economy statistics
9. 30–50 timeline milestones
10. Cultural festivals and traditional councils
11. Pre-1996 background (small set)

Target for launch: 16 LGA files, 30–50 event files, 20–30 place files, 15–25 general documents.

---

## 10. Evaluation

Build a **golden set of about 50 questions** before launch. Categories:

- **Answerable:** the KB contains a verified answer.
- **Unanswerable:** should be refused (for example, forecasts, unverified rumours).
- **False premise:** the question contains an error the assistant should correct.
- **Out of scope:** not about Ekiti; polite redirect.
- **Conflicting sources:** assistant should present the disagreement.

**Metrics:** citation correctness, groundedness (claims supported by retrieved text), correct-refusal rate, answer accuracy, and retrieval hit rate (right document in top 5).

Run the set on every KB or prompt change. Starter questions are in the spreadsheet (sheet **Eval Starter Set**).

---

## 11. Open decisions for the founding team

1. Who can mark a document `verified`?
2. Do we include a small pre-1996 background set at launch? (Recommended: yes.)
3. Language support at launch: English only, or also Yoruba?
4. Do we allow Tier D (oral) sources at launch, or only from week two?
5. Where is the source inventory kept so all teams can update it (this spreadsheet, or a GitHub CSV)?

---

## 12. Suggested sprint sequence

| Days | Work |
|---|---|
| 1–2 | Finalise template and tiers; team fills the source inventory; agree verification authority |
| 2–4 | Collect and verify launch documents (LGAs, creation, governors first) |
| 3–5 | Build ingestion script, `knowledge_chunks`, and retriever on the verified set |
| 5–6 | Wire Ask Ekiti with citations and refusal; run the golden set |
| 7 | Fix failures, freeze the launch KB, document how to contribute |

Per the master overview, the source inventory comes before any backend code.
