# Integration Notes — Agriculture Content

Built to match the conventions established in `06_Education/` (which itself matched
Member 4's own merged PR #29 pattern and the PR #11/PR #20 KB ingestion schema). It
is **not** auto-merge-ready.

## 1. Ownership is genuinely unresolved — read this first
`06_Education/` had a clear owner (Member 4, Issue #4) and a clear reviewer chain
(Member 3 for KB structure, Member 8 for verification sign-off, Member 1 for Yoruba).
For this Agriculture content, none of that is known. Before this goes anywhere near
a PR, someone needs to confirm: which Issue this maps to, who owns it, who reviews
it, and what folder number `06_Education/`'s sibling actually is (this pass guessed
`07_Agriculture` from a folder list of exactly one entry — treat that number as a
placeholder, not a decision).

## 2. Everything here is `ingestible: no`
Same two blockers as Education:
- **No Yoruba review.** Unconfirmed whether the same launch-language requirement
  and reviewer (Member 1) apply to this content — flagged as an assumption, not
  verified.
- **Tier assignments (A/B/C/D) are a first-pass proposal**, following the same
  pattern as Education's tiers but not read from the merged spec. The C-tier
  entries lean on single sources or self-reported corporate/government figures
  (Ikun Dairy Farm's current scale, the CBN-ABP jobs target, YCAD's founding) and
  deserve the most scrutiny before any upgrade to VERIFIED.

## 3. Genuinely disputed, not just under-sourced
Two items are live disagreements between sources, not just gaps:
- **EK-AGR-007**: Ikun Dairy Farm's 2019 initial cattle count (227 vs. 400) —
  two different government-adjacent sources give different numbers.
- **EK-AGR-009 / institutions/agro-allied-cargo-airport/**: a December 2025
  Tribune opinion piece directly disputes whether the airport actually functions
  as "agro-allied" (no warehouse/cold-storage/quarantine facilities observed
  despite 20+ landings), against the government's own framing of the airport as
  its flagship agriculture-export project. This is the closest analogue to
  Education's EK-EDU-011 (the Africa Check dispute) — it contradicts an
  administration's own stated narrative and probably deserves the same kind of
  second-reviewer sign-off before ingestion, whoever that reviewer turns out to be
  here.

## 4. What's genuinely ready to build on
- 17 timeline entries (EK-AGR-001 to 017), each single-fact, each sourced, each
  cross-referenced to an institution or programme file.
- 3 institution folders (Ekiti ADP, Ikun Dairy Farm, Agro-Allied Cargo Airport)
  each with `metadata.md` / `sources.md` / `permission.md`.
- 6 programme write-ups (cocoa revival, YCAD, CBN Anchor Borrowers rice, the
  tractorisation subsidy, L-PRES livestock, the poultry/broiler scheme) — a
  structure not present in Education, added because Agriculture's 30-year history
  is dominated by schemes and PPPs rather than standalone institutions.
- One sector-snapshot data file, explicitly flagged as a loose collection of
  sourced figures, not a systematic dataset (unlike Education's single-document
  Annual School Census summary — no equivalent official agriculture census was
  found this pass).
- A `kb_manifest_agriculture_rows.csv` fragment in the same column order as
  Education's (`doc_id, source_title, source_url, class, tier, last_verified,
  ingestible`), 30 rows, verified to parse cleanly.
- An `Agriculture_Gaps_and_Follow-ups.md` listing 11 concrete open items, including
  the ownership question itself as item #11.

## 5. Mechanics
- No suggested branch name this pass — depends entirely on who picks this up and
  which Issue it's filed against (see §1).
- No "Add files via upload" commits, same standard as Education.
- Check for other open PRs/branches touching this path before pushing — same
  caveat as Education, and I have no write/list access to check it myself.
