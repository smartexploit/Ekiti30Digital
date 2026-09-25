---
doc_id: EK-AGR-000
source_title: "EKITI@30 Agriculture Sector — Section Overview"
source_url: ""
class: agriculture
tier: A
last_verified: 2026-09-25
ingestible: no
---

# 07_Agriculture — Section Overview

This section documents the Ekiti State agriculture sector, 1996–2026, built to the
same conventions as `06_Education/` (Issue #4 / PR #11 knowledge-base spec, PR #20
`kb_manifest.csv` schema). It was requested directly, outside the original Issue #4
scope — see the open ownership question below before merge.

## Open question: who owns this content on the repo side?
`06_Education/` was built for Member 4, whose own merged PRs (#29, #10) set the
conventions this section reuses. **No equivalent owner has been identified for
Agriculture in this conversation** — I don't have visibility into which Issue or
which team member's work this corresponds to. Two folder-placement/ownership items
need a human decision before merge:
1. **Which Issue this maps to**, and who the reviewing member is (parallel to
   Member 4 for Education, Member 8 for verification sign-off).
2. **The folder number.** `06_Education/` was the only sibling folder visible when
   this was built, so `07_Agriculture` is a guess at the next available number, not
   read from an authoritative folder list. Confirm against the real repo tree
   before merging — a numbering collision here is a trivial fix, but it needs a
   human to check.

## Contents
- `timeline/agriculture_timeline_1996-2026.md` — EK-AGR-0XX dated entries, one fact
  per ID, covering the sector from state creation to 2026
- `institutions/` — three flagship agriculture assets, each with `metadata.md`,
  `sources.md`, `permission.md`: the State Agricultural Development Programme (ADP),
  Ikun Dairy Farm, and the Agro-Allied International Cargo Airport
- `programmes/` — six policy/scheme write-ups (cocoa revival, YCAD, CBN Anchor
  Borrowers rice financing, tractorisation subsidy, L-PRES livestock project, the
  poultry/broiler scheme)
- `data/agriculture_sector_snapshot.md` — sourced sector-level figures (share of
  employment, cocoa producer-tier classification, etc.)
- `Agriculture_Gaps_and_Follow-ups.md` — open items, naming convention matches
  `06_Education/Education_Gaps_and_Follow-ups.md`

## Language requirement
Per the Education section's README (citing PR #11 Part C), launch requires English +
Yoruba review. **None of the content in this section has been translated or
Yoruba-reviewed.** Every file here should be treated as `ingestible: no` for the live
KB until that pass happens.

## Source tier note
Tier assignments (A/B/C/D) are a first-pass proposal following the same
official/primary=A, reputable secondary/press=B, lower-confidence/single-sourced=C,
oral/community=D pattern used in `06_Education/`. Not read directly from the merged
KB spec this pass — confirm before ingestion, same caveat as Education.

## What makes this pass different from Education's first pass
Agriculture is the state's largest economic sector (~75% of the population, per the
state government's own "About Ekiti" page) and has 30 years of continuous,
well-documented state investment — so this write-up leans harder on *programme*
history (schemes, funding rounds, PPPs) than *institutional* history, since most of
the durable agriculture assets are projects and parastatals rather than
standalone schools. Two threads run the full 30 years and are flagged where relevant:
the Ikun Dairy Farm's decades-long moribund-to-revival arc, and cocoa's
1970s-boom-to-multi-decade-decline-to-current-revival arc.
