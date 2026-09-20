# Citizen Contribution Workflow — Decisions Log

Issue: #8 · Owner: Member 8 · Status: **DRAFT — proposals awaiting confirmation**

## Purpose

This log records design decisions for the My Ekiti Story and Ekiti 2056 contribution workflow, so engineering and the research/content leads work from one agreed set of rules.

## Sources and precedence

1. **Issue #8** (authoritative for required tasks and fields)
2. **CONTRIBUTING.md** §4 (research contributions), §5 (citizen stories), §10 (content review)
3. Earlier internal draft workflow (v1.0), used as a base

Where sources conflict, Issue #8 takes precedence.

Decision status: **ADOPTED** = project principle, **PROPOSED** = awaiting confirmation, **CONFIRMED** = agreed.

---

## D1. Three separate checks — ADOPTED

Moderation, verification and editorial approval are separate stages with separate records.

| Check | Question | Owner |
|---|---|---|
| Moderation | Should this enter the review process at all? (safety, spam, abuse, privacy) | Member 8 |
| Verification | Is this factual claim adequately supported? | Research/content leads |
| Editorial | Is it clear, fairly attributed, and free of misleading edits? | Member 8 + designated reviewer |

No submission moves directly from citizen submission to PUBLIC.

## D2. Status model — PROPOSED

Each submission carries three status fields.

**Lifecycle `status`:** `PENDING`, `IN_MODERATION`, `IN_CLASSIFICATION`, `IN_VERIFICATION`, `IN_EDITORIAL_REVIEW`, `NEEDS_REVISION`, `APPROVED`, `PUBLIC`, `REJECTED`, `WITHDRAWN`, `UNPUBLISHED`

**`verification_status`:** `NOT_STARTED`, `NOT_REQUIRED`, plus the outcomes in D4.

**`editorial_status`:** `NOT_REVIEWED`, `REVIEWED`, `REVISION_REQUESTED`.

Naming conflicts resolved:
- `NEEDS_REVISION` is used instead of "REVISION REQUIRED" (machine-friendly, consistent underscores).
- **Escalation is an assignment (`escalated_to`), not a lifecycle status.** The submission stays in its current stage while a specialist reviews it.
- `UNPUBLISHED` (hidden pending review) is added for published items that raise a privacy or harm concern (see D12).

Full transition table: Phase 2 / Phase 5.

## D3. Classification — PROPOSED

Values: `PERSONAL_ACCOUNT`, `FACTUAL_CLAIM`, `OPINION`, `VISION_PROPOSAL`, `MIXED`.

Separate flag: `sensitive` (true/false) for potentially harmful allegations about named people or institutions. It can apply to any classification.

Ekiti 2056 submissions default to `VISION_PROPOSAL`.

## D4. Verification is per claim — PROPOSED

A story may contain several factual claims. Verification is recorded **per claim**, not per story. Each claim record holds: claim text, source, source type (level 1–4), date/context, limitations, outcome, reviewer.

Outcomes: `VERIFIED`, `ATTRIBUTED`, `OPINION_VISION`, `NEEDS_EVIDENCE`, `UNSUPPORTED_FALSE`.

A story can be published as a personal/community account even when some claims stay `ATTRIBUTED`. It is never labelled verified history unless the claim is `VERIFIED`.

## D5. Source hierarchy — PROPOSED

- **Level 1:** official sources (government, official institutional records/publications)
- **Level 2:** recognised authoritative sources (NBS, educational institutions, museums, archives, recognised organisations)
- **Level 3:** reputable secondary sources (established publications, credible historical references)
- **Level 4:** community evidence (interviews, photographs, documents, first-hand testimony), used as evidence and attributed, not treated as independently verified

Consistent with CONTRIBUTING.md §4. Conflicting sources are documented, not silently resolved (CONTRIBUTING.md §11).

## D6. Submission fields — PROPOSED

**My Ekiti Story**

| Field | Required | Public |
|---|---|---|
| Name | Yes | Per credit choice |
| Contact (email or phone/WhatsApp) | Yes | **Never** |
| Location / LGA (16-LGA list) | Yes | Yes |
| Story title | Yes | Yes |
| Story | Yes | Yes |
| Year / period (with "not sure" option) | Yes | Yes |
| Photo / media | Optional | If approved |
| Permission to publish | Yes | No |
| Contributor credit choice (D7) | Yes | Applied |
| Confirmation: 18+ (D9) | Yes | No |
| Confirmation: right to share media | If media | No |
| Review status | System | No |

**Ekiti 2056**

| Field | Required | Public |
|---|---|---|
| Name | Yes | Per credit choice |
| Contact | Yes | **Never** |
| Location / LGA | Yes | Yes |
| Vision / idea | Yes | Yes |
| Category | Yes | Yes |
| Why it matters | Yes | Yes |
| Photo / media | Optional | If approved |
| Permission to publish | Yes | No |
| Contributor credit choice | Yes | Applied |
| Confirmation: 18+ | Yes | No |
| Review status | System | No |

Changes from the v1.0 draft:
- Added Why It Matters, Permission, Credit and Review Status to Ekiti 2056 (required by Issue #8).
- Added Contact, which is needed for revision requests, follow-up and anonymous handling.
- Removed **age range** from launch scope (data minimisation, minors).

System-generated on submission: Submission ID, timestamp, type, statuses, assigned reviewer.

## D7. Contributor credit — PROPOSED

The contributor chooses one option at submission, stored on the record:
1. Full name + LGA
2. First name + LGA
3. Anonymous (see D8)

## D8. Anonymous submissions — PROPOSED

- Anonymous is an opt-in choice, never the default.
- Internal record keeps identity and contact for moderation, follow-up and verification.
- Public record shows "Anonymous contributor" + LGA (LGA may be withheld if it would identify the person).
- Identifying details inside the text (names, unique circumstances) are reviewed in editorial and may need the contributor's agreement to remove.
- Access to identity is limited to designated reviewers.
- Anonymity does not prevent claim verification against sources. It only means the contributor's identity is not part of the evidence.

## D9. Contributor eligibility — PROPOSED

Launch with **18+ only**, confirmed by checkbox. Guardian-consent flow for minors is deferred until the platform can support it.

## D10. Final publication authority — PROPOSED, needs Member 1

- `PERSONAL_ACCOUNT`, `OPINION`, `VISION_PROPOSAL`: Member 8 approves after moderation and editorial review.
- Anything with a factual claim: also needs the relevant lead's verification result before approval.
- `sensitive` flag: also needs sign-off from Member 1 (or a designated senior reviewer).

## D11. Escalation routing — PROPOSED, needs confirmation from Members 4 and 7

| Subject | Route to |
|---|---|
| History, governance, institutions, education, health, agriculture, statistics | Member 4 — Research & History |
| Culture, tradition, festivals, tourism, heritage | Member 7 — Culture, Tourism & Content |
| Geography, LGA boundaries, headquarters, landmarks | Member 5 — Geospatial & LGA |
| Sensitive allegations | Member 1 — Project Founder |

The v1.0 draft named an "Education" lead. There is none in the current 8-member structure, so education claims route to Member 4 unless a lead is designated.

## D12. Corrections, clarifications and removal — PROPOSED

- A correction request (from contributor, reviewer or reader) creates a linked correction record.
- Published content stays live during review unless there is a privacy or harm concern, in which case it becomes `UNPUBLISHED` immediately.
- Editors never silently change a contributor's meaning. Uncertain factual statements are held, qualified, attributed or removed depending on the result.
- A contributor may request removal of their contribution. Response timeline: to be set.

## D13. Language — OPEN

Should submissions be accepted in Yoruba as well as English? If yes, reviewers who can read Yoruba are needed. Decide before launch.

## D14. Data protection and retention — OPEN, needs Member 1

Names, contacts and photos are personal data. Needed before launch: a privacy notice, consent wording, retention period, and a removal process. Nigeria's data protection law applies (to be verified, not legal advice).

## D15. Where the documents live — PROPOSED

- Shared workflow: `11_Citizen_Stories/workflow/`
- Ekiti 2056 specifics: `12_Ekiti_2056/`
- Nothing in other members' folders. Any link from `18_Project_Documentation/` is added after review.
- Format: Markdown in the repo, PDF exported at the end.

---

## Confirmation needed

| Decision | Who confirms |
|---|---|
| D9 (18+ only), D10 (publication authority), D14 (privacy/retention) | Member 1 |
| D6 (fields, contact field), D2 (status model, transitions) | Member 2 (Engineering) |
| D11 (routing) | Members 4, 5, 7 |
| D13 (language) | Member 1 + Member 8 |
