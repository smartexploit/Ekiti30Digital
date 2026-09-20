# Citizen Contribution Workflow — Decisions Log

Issue: #8 · Owner: Member 8 · Status: **DRAFT — proposals awaiting confirmation**

## Purpose

This log records design decisions for the My Ekiti Story and Ekiti 2056 contribution workflow, so engineering and the research/content leads work from one agreed set of rules.

## Sources and precedence

1. **Issue #8** (authoritative for required tasks and fields)
2. **CONTRIBUTING.md** §4 (research contributions), §5 (citizen stories), §10 (content review)
3. Earlier internal draft workflow (v1.0), used as a base

Where sources conflict, Issue #8 takes precedence. Direction from Member 1 (see the Confirmation record at the end) takes precedence over PROPOSED items.

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

Each submission carries three status fields, plus a guardian consent field for contributors under 18.

**Lifecycle `status`:** `PENDING`, `IN_MODERATION`, `IN_CLASSIFICATION`, `IN_VERIFICATION`, `IN_EDITORIAL_REVIEW`, `NEEDS_REVISION`, `APPROVED`, `PUBLIC`, `REJECTED`, `WITHDRAWN`, `UNPUBLISHED`

**`verification_status`:** `NOT_STARTED`, `NOT_REQUIRED`, plus the outcomes in D4.

**`editorial_status`:** `NOT_REVIEWED`, `REVIEWED`, `REVISION_REQUESTED`.

**`guardian_consent_status`** (contributors under 18 only): `NOT_REQUIRED`, `PENDING`, `GRANTED`, `DECLINED`. See D9.

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

## D6. Submission fields — PROPOSED (updated after Member 1's reply)

**My Ekiti Story**

| Field | Required | Public |
|---|---|---|
| Name (contributors under 18: first name only) | Yes | Per credit choice |
| Contact: email or phone/WhatsApp (contributors under 18: the parent/guardian's contact instead) | Yes | **Never** |
| Age group: "18 or over" / "Under 18" | Yes | **Never** |
| Location / LGA (16-LGA list) | Yes | Yes |
| Story title | Yes | Yes |
| Story | Yes | Yes |
| Year / period (with "not sure" option) | Yes | Yes |
| Photo / media | Optional | Only if approved and consent is on record |
| Permission to publish | Yes | No |
| Contributor credit choice (D7) | Yes | Applied |
| Confirmation: I have the right to share this content and any media | Yes | No |
| Parent/guardian consent (under 18 only, obtained after submission, see D9) | If under 18 | No |
| Review status | System | No |

**Ekiti 2056**

| Field | Required | Public |
|---|---|---|
| Name (contributors under 18: first name only) | Yes | Per credit choice |
| Contact (contributors under 18: the parent/guardian's contact instead) | Yes | **Never** |
| Age group: "18 or over" / "Under 18" | Yes | **Never** |
| Location / LGA | Yes | Yes |
| Vision / idea | Yes | Yes |
| Category | Yes | Yes |
| Why it matters | Yes | Yes |
| Photo / media | Optional | Only if approved and consent is on record |
| Permission to publish | Yes | No |
| Contributor credit choice (D7) | Yes | Applied |
| Confirmation: I have the right to share this content and any media | Yes | No |
| Parent/guardian consent (under 18 only, obtained after submission, see D9) | If under 18 | No |
| Review status | System | No |

**Not collected:** date of birth, exact age, home address, school name, ID numbers, precise location, or a child's own contact details. If a field is not needed for review, follow-up, consent or credit, we do not ask for it.

Changes from the v1.0 draft:
- Added Why It Matters, Permission, Credit and Review Status to Ekiti 2056 (required by Issue #8).
- Added Contact, needed for revision requests, follow-up, consent and anonymous handling.
- Replaced the optional age range with a two-option age group, used only for safeguards and never public.
- Replaced the 18+ confirmation with the under-18 safeguards in D9.

System-generated on submission: Submission ID, timestamp, type, statuses, assigned reviewer.

## D7. Contributor credit — PROPOSED

The contributor chooses one option at submission, stored on the record:
1. Full name + LGA (not available to contributors under 18)
2. First name + LGA
3. Anonymous (see D8)

For contributors under 18, the parent/guardian confirms the credit choice as part of consent (D9).

## D8. Anonymous submissions — PROPOSED

- Anonymous is an opt-in choice, never the default.
- Internal record keeps identity and contact for moderation, follow-up and verification.
- Public record shows "Anonymous contributor" + LGA (LGA may be withheld if it would identify the person).
- Identifying details inside the text (names, unique circumstances) are reviewed in editorial and may need the contributor's agreement to remove.
- Access to identity is limited to designated reviewers.
- Anonymity does not prevent claim verification against sources. It only means the contributor's identity is not part of the evidence.

## D9. Contributors under 18, safeguards and guardian consent — CONFIRMED (principle), details PROPOSED

**Direction from Member 1 (confirmed):** the platform does not launch as 18+ only. Younger contributors are allowed, with appropriate safeguards and, where necessary, parent/guardian consent. We avoid collecting unnecessary personal information from minors.

**Proposed way to apply it** (details awaiting Member 1):

1. **Age group, not age.** The form asks one question: "18 or over" or "Under 18". No date of birth or exact age is collected. The answer is never shown publicly.
2. **What is collected from under-18 contributors:** first name only, LGA, the content, and a parent/guardian's contact. Not collected: the child's own contact details, date of birth, home address, school name, ID numbers.
3. **Guardian consent (proposed default: required for every under-18 publication).** "Where necessary" is applied as "always before publication", because a moderator cannot reliably judge necessity case by case. After submission the guardian is contacted and asked to confirm permission to publish, the credit choice, and permission for any media. The result is tracked in `guardian_consent_status`: `PENDING`, then `GRANTED` or `DECLINED`.
4. **Gate.** A submission from someone under 18 cannot become `APPROVED` unless `guardian_consent_status = GRANTED`. Moderation and review may continue while consent is pending.
5. **No guardian reply in 30 days:** the submission is withdrawn and the guardian's contact is deleted per D14.
6. **Withdrawal of consent.** A guardian can withdraw consent at any time. The item becomes `UNPUBLISHED` immediately (D12).
7. **How under-18 content is shown.** Credit is first name + LGA, or anonymous. Full name is never shown. No school name, home address or other detail that could identify or locate a child. No identifiable photo of a child unless the guardian's consent specifically covers media.
8. **Safeguarding.** If a submission suggests a child is at risk or has been harmed, it is not published and goes to Member 1 the same day.
9. **Verification is unchanged.** Claims are still checked by the relevant lead. Verifiers never receive the contributor's or guardian's identity or contact details.

**Open for Member 1:**
- Is there a minimum age (for example 13)?
- Should guardian consent apply to all under-18 publications, or only some (for example under 16, or where media or identifying details are involved)?
- Nigeria's data protection law is likely to have specific rules on children's data (to be verified). Member 1 to confirm what the platform must do. This is not legal advice.

## D10. Final publication sign-off — CONFIRMED (principle), details PROPOSED

**Direction from Member 1 (confirmed):**
- Final publication approval sits with the **Project/Editorial Review function**.
- **Member 8 coordinates** the submission workflow.
- Any factual claim must be **verified by the relevant research/content lead before publication.**

**Who does what**

| Step | Owner |
|---|---|
| Intake, moderation, classification, routing claims, editorial preparation, contributor communication | Member 8 |
| Checking factual claims | Relevant research/content lead (D11) |
| **Final publication approval** | **Project/Editorial Review function** |
| Publishing an approved item | Member 8 |

Member 8 does not give final approval alone. Contributors are told that approval is by the project's editorial review.

**Sensitive submissions** (`sensitive = true`) go through the same final approval, with Member 1 involved (D11).

**Points to confirm with Member 1**
1. **Who is the Project/Editorial Review function?** A named person, or a small panel? Until named, Member 1 acts as the approving reviewer.
2. **How "verified before publication" applies to unverified claims.** Proposed reading: every factual claim must be reviewed by the relevant lead before publication, with a finding recorded. A `VERIFIED` claim may be published as fact with its source. A claim the lead cannot establish is either removed, or published only as the contributor's own account, clearly labelled and never as verified (`ATTRIBUTED`, and never for sensitive claims). If Member 1 wants a stricter rule (claims that cannot be verified are always removed), `ATTRIBUTED` is dropped from the workflow.

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

## D14. Privacy, data minimisation and retention — CONFIRMED (principles), details PROPOSED / OPEN

**Direction from Member 1 (confirmed):**
- Data minimisation: collect only what is necessary.
- Contributors' contact information is not publicly displayed by default.
- Photos and media are published only with appropriate consent.
- Personal information is not kept indefinitely without a legitimate reason.

**Proposed practice**
- Only the fields in D6 are collected.
- Contact details are used only for follow-up, revision requests, corrections and consent. They are never public and never given to verifiers, publishers or the wider team.
- Media: the contributor confirms the right to share it. Photos of identifiable people need those people's permission. Under-18 rules are in D9.
- Anonymous contributors: identity is held internally and access is limited to designated reviewers (D8).
- A short privacy notice is shown on each form: what is collected, why, who sees it, how long it is kept, and how to request removal.
- Removal: a contributor (or guardian) can request removal of a published item and of their personal data. Response time to be set.

**Proposed retention** (example values, for Member 1 to confirm)

| Data | Kept | Then |
|---|---|---|
| Published content and its credit line | While published | Removed on request or when unpublished |
| Contact details, item is public | While the item is public, for corrections and removal requests | Deleted when the item is unpublished or removed |
| Contact details, item rejected or withdrawn | 90 days after the final decision | Deleted |
| Rejected or withdrawn content and reason code | 12 months (duplicate checks, audit) | Deleted |
| Guardian consent record | While the item is public | Deleted with the item |
| Audit trail of status changes | Kept, without contact details | Reviewed annually |

**For engineering (Phase 5)**
- Contact fields are visible only to designated reviewers.
- Contact details are excluded from exports and public pages.
- A scheduled deletion job applies the retention table.

**Open**
- Retention periods above.
- Wording of the privacy notice.
- Legal check: Nigeria's data protection law is likely to apply (to be verified). Member 1 to confirm the platform's obligations. This is not legal advice.

## D15. Where the documents live — PROPOSED

- Shared workflow: `11_Citizen_Stories/workflow/`
- Ekiti 2056 specifics: `12_Ekiti_2056/`
- Nothing in other members' folders. Any link from `18_Project_Documentation/` is added after review.
- Format: Markdown in the repo, PDF exported at the end.

---

## Confirmation needed

| Decision | Who confirms |
|---|---|
| D9 open points: minimum age, scope of guardian consent | Member 1 |
| D10 open points: who is the Project/Editorial Review function, how "verified before publication" applies to unverified claims | Member 1 |
| D14 open points: retention periods, privacy notice, legal check | Member 1 |
| D6 (fields, age group, guardian consent field), D2 (status model including guardian consent) | Member 2 (Engineering) |
| D11 (routing) | Members 4, 5, 7 |
| D13 (language) | Member 1 + Member 8 |

## Confirmation record

| Date | From | Decisions | Summary |
|---|---|---|---|
| 2026-09-20 | Member 1 | D9, D10, D14 | Not 18+ only: younger contributors allowed with safeguards and guardian consent where necessary, minimal data from minors. Final publication approval by the Project/Editorial Review function, coordinated by Member 8, with factual claims verified by the relevant lead before publication. Data minimisation, contact details not public by default, media only with consent, no indefinite retention. |
