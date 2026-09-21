# Citizen Contribution Workflow — Decisions Log

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0), some decisions still PROPOSED or OPEN**

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

## D6. Submission fields — PROPOSED (language field added after Member 1's reply)

**My Ekiti Story**

| Field | Required | Public |
|---|---|---|
| Name | Yes | Per credit choice |
| Contact (email or phone/WhatsApp) | Yes | **Never** |
| Location / LGA (16-LGA list) | Yes | Yes |
| Language of submission (English / Yoruba) | Yes | Yes (shown as a label) |
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
| Language of submission (English / Yoruba) | Yes | Yes (shown as a label) |
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

Data minimisation (D14): only the fields above are collected. Contact details are never public by default. Not collected: date of birth, home address, ID numbers, precise location.

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

## D9. Contributor eligibility — CONFIRMED (18+ only for the initial launch)

**Direction from Member 1 (confirmed):**
- The platform is not to be permanently restricted to 18+.
- For the initial launch it is **18+ only**, until there is a proper guardian/consent workflow and appropriate safeguards for minors.

**How this applies at launch (proposed):**
1. Both forms include a required confirmation: "I am 18 or over."
2. Nothing else about age is collected. No date of birth, school, or guardian details at launch.
3. If a submission clearly shows the contributor is under 18 (for example, they say so), it is not published. The moderator declines it politely, explains that under-18 contributions are not yet accepted, and uses reason code `UNDER_AGE`.
4. Adults may submit content that mentions children. Identifiable photos of children are not published without the permission of a parent or guardian (see D14).

**Before the 18+ restriction is lifted (future work, not part of the launch scope):** a separate decision from Member 1 on the guardian/consent workflow, safeguards, minimum age, and what data may be collected from minors.

## D10. Final publication authority and unverified claims — CONFIRMED

**Direction from Member 1 (confirmed):**
- Member 8 coordinates moderation and editorial review.
- Publication of submissions containing factual claims requires the relevant lead's verification before publication.
- Sensitive allegations require Member 1 or a designated senior reviewer. **For the initial launch, Member 1 is the designated senior reviewer**, unless Member 1 explicitly designates another.
- If a lead cannot verify a factual claim, it does not automatically have to be removed. Where appropriate, it may remain as part of the contributor's clearly labelled citizen or personal account, but it must never be presented as verified fact. If the claim is harmful, defamatory, seriously accusatory or otherwise unsuitable for publication, it is removed or sent back for revision.

**How this applies:**

| Submission | Approval path |
|---|---|
| No checkable claims | Member 8 approves after moderation and editorial review |
| Contains factual claims | The relevant lead records a finding for every claim. Then Member 8 approves. |
| Sensitive allegation (`sensitive = true`) | The designated senior reviewer (Member 1 at launch) also signs off |

Member 8 publishes approved items.

**A claim the lead cannot establish.** After the contributor has been asked for a source or clarification, the reviewer chooses one of:
1. **Keep it as `ATTRIBUTED`.** It stays in the contributor's clearly labelled citizen account, worded as the contributor's own account, never in the Verified facts box, never shown as verified. Allowed only when it is not harmful, defamatory, seriously accusatory or otherwise unsuitable, and is not a sensitive claim.
2. **Send the submission back for revision** (reword, narrow the claim, or add a source).
3. **Remove the claim,** with the contributor's agreement. If the claim is the core of the submission, reject it.

A claim that is harmful, defamatory, seriously accusatory or otherwise unsuitable is never `ATTRIBUTED`. It is removed or the submission goes back for revision.

**Stricter application, PROPOSED (Member 1 may relax it):** sensitive claims are never published as attributed-only. They are either `VERIFIED` or removed.

**Open:** whether Member 1 designates another senior reviewer later. Until then it is Member 1.

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

## D13. Language — CONFIRMED (English and Yoruba), details PROPOSED

**Direction from Member 1 (confirmed):**
- Accept submissions in both English and Yoruba.
- Yoruba submissions go through the same moderation and verification process.
- An appropriate reviewer is involved where language-specific review is required.

**How this applies (proposed):**
1. Both forms include "Language of submission" (English or Yoruba). It is stored and used to assign a reviewer.
2. Same stages, checks, reason codes and statuses for both languages. There are no shortcuts for either.
3. Moderation and editorial review of Yoruba submissions is done by a reviewer who reads Yoruba. Member 8 still coordinates.
4. Editorial edits to Yoruba text respect spelling, diacritics and tone marks, and never change meaning. Anything unclear goes back to the contributor.
5. Verification requests include the claim in its original wording plus an English working translation, clearly marked as such. Leads who read Yoruba can check the original.
6. Published in the language submitted. Any English translation shown is labelled as a translation, has been checked by a person, and does not replace the original.
7. Machine or AI translation is a working aid only. It is never the sole basis for moderation, verification or publication (consistent with CONTRIBUTING.md section 6).
8. For engineering (Phase 5): Yoruba characters and tone marks must be stored, displayed and searched correctly (UTF-8).

**Open:** who takes the Yoruba-capable reviewer role. Member 1 confirmed that no specific reviewer is hard-coded until this is agreed. In the workflow and in engineering it is an assignable role (`reviewer_role = YORUBA_REVIEWER`) filled from a configurable list. To be confirmed by Member 1 and Member 8.

## D14. Privacy, data minimisation and retention — CONFIRMED (principles), retention period OPEN

**Direction from Member 1 (confirmed):**
- Data minimisation: collect only information necessary for submission, review, follow-up and publication.
- Contact information is never publicly displayed by default.
- Contributor identity and contact details have restricted access.
- Photos and media require appropriate permission.
- The specific retention period is left open until the project's privacy notice and retention policy are established. No period is assumed in the meantime.

**Proposed practice:**
- Only the fields in D6 are collected.
- Contact details are used only for follow-up, revision requests, corrections and removal requests. They are never public, and never given to verifiers, publishers or the wider team.
- Identity and contact fields are visible to designated reviewers only (D8).
- Media: the contributor confirms the right to share it. Identifiable people in photos, especially children, need their permission or a parent's or guardian's (D9).
- Each form shows a short privacy notice: what is collected, why, who sees it, how long it is kept, and how to ask for removal. The text is drafted once the policy exists.
- A contributor can ask for their item and personal data to be removed. Response time is set with the policy.

**For engineering (Phase 5):**
- Identity and contact fields are restricted by role, and excluded from exports and public pages.
- Retention is a configurable setting for each data type, not a fixed number in the code, so the period can be set later.
- Deletion of a submission and its personal data must be possible.

**Open:**
- Retention periods for each data type.
- The privacy notice and who drafts it.
- Removal-request response time.
- Whether a legal check against Nigeria's data protection law is needed (to be verified, not legal advice).

## D15. Where the documents live — PROPOSED

- Shared workflow: `11_Citizen_Stories/workflow/`
- Ekiti 2056 specifics: `12_Ekiti_2056/`
- Nothing in other members' folders. Any link from `18_Project_Documentation/` is added after review.
- Format: Markdown in the repo, PDF exported at the end.

---

## D16. Additions to the D6 field lists, proposed in the Phase 3 specs — PROPOSED

The submission specs add these details to the D6 field lists. They contain no personal data beyond what D6 already collects.

| Addition | Applies to | Why |
|---|---|---|
| "Outside Ekiti State" as an LGA option | Both forms | Ekiti diaspora contributors |
| Contact method (email, phone or WhatsApp) | Both forms | Reach the contributor the way they prefer |
| `vision_headline`: "Vision in one line" | Ekiti 2056 | A heading for the public page, so editors do not invent one |
| `media_caption`, `media_credit`, `media_people_ok` | Both forms, if media | Every image is described and credited, and people in photos have agreed |
| `promote_on_social`: separate optional permission | Both forms | Publishing on the platform and sharing on social media are separate consents |
| `privacy_ack`: privacy notice acknowledged | Both forms | Data minimisation and transparency (D14) |
| Location metadata stripped from images | Both forms | Photos must not reveal where someone lives (D14) |

Full specifications: `MY_EKITI_STORY_SPEC.md` (in `11_Citizen_Stories/`) and `EKITI_2056_SPEC.md` (in `12_Ekiti_2056/`). Credit rules: `CREDIT_AND_ANONYMITY.md`. Corrections: `CORRECTIONS_AND_CLARIFICATIONS.md`.

## Confirmation needed

| Decision | Who confirms |
|---|---|
| D10: whether Member 1 designates another senior reviewer later (Member 1 is the senior reviewer for the initial launch) | Member 1 |
| D14: privacy notice and retention policy (period left open); who drafts | Member 1 |
| D13: who takes the Yoruba-capable reviewer role (assignable role, not hard-coded) | Member 1 + Member 8 |
| D9: conditions for lifting 18+ only (future, not for launch) | Member 1, later |
| D6 (fields, including the language field), D2 (status model, transitions) | Member 2 (Engineering) |
| D11 (routing) | Members 4, 5, 7 |
| D16 (additions to the D6 fields; LGA list source) | Member 2 (Engineering), Member 5 (LGA list) |

## Confirmation record

| Date | From | Decisions | Summary |
|---|---|---|---|
| 2026-09-20 | Member 1 | D9, D10, D13, D14 | D9: 18+ only for the initial launch, not permanently. Minors later, once a guardian/consent workflow and safeguards exist. D10: Member 8 coordinates moderation and editorial review. Factual claims need the relevant lead's verification before publication. Sensitive allegations need Member 1 or a designated senior reviewer. D13: English and Yoruba accepted, same moderation and verification, with a language-specific reviewer where required. D14: data minimisation, contact details never public by default, restricted access to identity and contacts, media needs permission, retention period left open until the privacy notice and retention policy exist. |
| 2026-09-20 | Member 1 | D10, D13 | Follow-up. D10: an unverified claim may stay as part of the contributor's clearly labelled citizen account, never as verified fact. Harmful, defamatory, seriously accusatory or otherwise unsuitable claims are removed or sent back for revision. Member 1 is the designated senior reviewer for sensitive submissions at initial launch, unless he designates another. D13: Yoruba submissions follow the same moderation, verification and editorial process, with a Yoruba-capable reviewer where language-specific review is required. No specific reviewer is hard-coded until the role is confirmed. |
