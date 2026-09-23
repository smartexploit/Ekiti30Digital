---
id: lga-example                 # required, unique: lowercase letters, digits, hyphens
title: Example title            # required
category: lgas                  # history | government | lgas | tourism | culture | education | agriculture | health | statistics
doc_type: entity                # entity | event | dataset | background
source_ids: [SRC-000]           # required; every ID must exist in the Source Inventory
source_name: Copy the exact title from the Source Inventory
source_url: Copy the exact URL/location from the Source Inventory
publication_date: YYYY-MM-DD    # when the SOURCE was published (YYYY, YYYY-MM, YYYY-MM-DD or Not stated)
source_tier: A                  # A | B | C | D (Tier D is not used at launch)
status: draft                   # draft | needs_review | conflict | verified | retired
verified_by:                    # leave blank until verified; never the author
last_verified:                  # leave blank; the reviewer enters the real completion date (YYYY-MM-DD), never a future date
verification_note:              # required for a Tier C exception or a resolved conflict
tier_c_exception: false         # true only with a recorded reason in verification_note
period_covered: 1996-2026       # a year, a range, or pre-1996 (pre-1996 documents live in 01_History/pre-1996/)
language: en                    # en | yo
translation_of:                 # Yoruba translations only: id of the English original
translation_reviewed_by:        # Yoruba reviewer, once reviewed
lgas: []
tags: []
---

## Summary
Two to three self-contained sentences.

## Facts
- One fact per line, each traceable to a source. [S1]

## Sources
- [S1] SRC-000: title, publisher, URL, date of the source.
