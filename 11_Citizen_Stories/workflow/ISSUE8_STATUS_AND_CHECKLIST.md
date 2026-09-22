# Issue #8 — Status, Acceptance Checklist and Follow-ups

Owner: Member 8 · Updated: 2026-09-22 · Target: final integration review, Wed 23 Sep 2026

## 1. Acceptance checklist (Issue #8's 13 tasks)

| # | Task | Drafted | Confirmed by team | Notes |
|---|---|---|---|---|
| 1 | My Ekiti Story submission process | Yes | Partial | Fields await Member 2 (D6, D16) |
| 2 | Ekiti 2056 submission process | Yes | Partial | Same as above |
| 3 | Information required from contributors | Yes | Partial | D6/D16 |
| 4 | Content review process | Yes | Yes | D1, D10 confirmed |
| 5 | Moderation process | Yes | Yes | |
| 6 | Approval/rejection process | Yes | Yes | D10 confirmed |
| 7 | Corrections/clarifications | Yes | Yes | Retention timing open (D14) |
| 8 | Contributor credit | Yes | Yes | D7 |
| 9 | Anonymous submissions | Yes | Yes | D8 |
| 10 | Inappropriate/misleading content | Yes | Yes | |
| 11 | Personal story vs verified fact | Yes | Yes | Core rule, confirmed |
| 12 | Community engagement plan | Yes | Partial | Launch date, wording await Member 1 |
| 13 | Verification workflow with leads | Yes | Partial | Routing (D11) awaits Members 4, 5, 7 |
| — | Implementable by Engineering | Yes | No | Awaiting Member 2 (section 2 below) |

**12 of 13 tasks drafted and internally consistent. Remaining gaps are external confirmations, not missing design work.**

## 2. Member 2 (Engineering) — outstanding items

Tracked from `ENGINEERING_HANDOFF.md` section 14 and `DECISIONS.md` D2, D6, D16.

| Item | Asked | Status | Due |
|---|---|---|---|
| D2: status model (3 fields, per-claim verification) | Yes | No reply | Chasing, see message below |
| D6/D16: form fields and limits | Yes | No reply | Chasing |
| Q1–Q15 in ENGINEERING_HANDOFF.md §14 (stack, verifier access, corrections model, estimate, etc.) | Yes | No reply | Chasing |

**If no reply by Wed:** these stay PROPOSED and go into PR #9 as accepted follow-up work, per Member 1's instruction not to merge until resolved or explicitly accepted as follow-up.

## 3. Privacy and retention — proposed for Member 1's decision

D14 left the retention period open pending a privacy policy. Given the deadline, here is a concrete proposal to approve or amend, rather than leaving it open indefinitely.

| Data | Proposed period | Action after |
|---|---|---|
| Contact details, item public | While published | Deleted when unpublished/removed |
| Contact details, item rejected/withdrawn | 90 days | Deleted |
| Rejected/withdrawn content + reason code | 12 months | Deleted |
| Correction records + reporter contact | 12 months | Deleted |
| Message log | 12 months | Deleted |
| Media files (unapproved) | 90 days | Deleted |
| Audit trail (no contact details) | Indefinite | Reviewed annually |

**Privacy notice**: short-form text already drafted in `MY_EKITI_STORY_SPEC.md` section 7, pending Member 1's approval of exact wording.

**Recommendation:** approve these as launch defaults, adjustable later. They are the same numbers used as the working example in `DECISIONS.md` D14 before Member 1 asked to leave the period open.

## 4. Yoruba-capable reviewer role

No one is currently assigned (D13). Options:
- A team member who reads Yoruba fluently is named as reviewer (part-time, reviewing only Yoruba submissions).
- If no one is available internally, a trusted community volunteer is vetted and given the role before launch.
- **Fallback if unresolved by Wed:** Yoruba submissions are accepted but held in `NEEDS_REVISION`-equivalent status until a reviewer is named, rather than blocking the whole feature. This is explicitly a follow-up, not a blocker to closing Issue #8's design phase.

## 5. Consistency

Last consistency sweep: 2026-09-22, `check_consistency.py`, 0 failures (after removing a false-positive check for "guardian_consent", which is legitimately referenced as *not existing* at launch).

All 12 documents are marked **READY FOR REVIEW (v1.0)**. Confirmed decisions (D1, D7–D10, D13 principle) are consistently reflected across `CONTRIBUTION_WORKFLOW.md`, `MODERATION_GUIDE.md`, `VERIFICATION_WORKFLOW.md`, `CREDIT_AND_ANONYMITY.md`, and `ENGINEERING_HANDOFF.md`.

## 6. Summary for Member 1

- PR #9 is open, not draft, not merged, per your instruction.
- 12 of 13 tasks are drafted and internally consistent.
- Three items need your direct decision before Wednesday: privacy/retention numbers (section 3), Yoruba reviewer (section 4), and whether Member 2's silence becomes an accepted follow-up.
- Everything else is external confirmation (Members 2, 4, 5, 7), tracked here and chased below.
