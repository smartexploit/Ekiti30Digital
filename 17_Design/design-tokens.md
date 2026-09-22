# EKITI@30 DIGITAL — Design Tokens
**Owner:** Member 6 — UI/UX & Design Lead
**Status:** v4 — submitted as PR #14, design handoff to Engineering
**Last updated:** 22 September 2026

> **This file is the implementation source of truth.** Engineering (Member 2) should build
> components from the token values and layout principles below — not by eyeballing
> `homepage-preview.html`. The preview is a reference for look/feel and behavior; this
> document is what defines exact values.

---

## Color Palette

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#FFFFFF` | Primary background |
| `--bg-warm` | `#FFF8EA` | Warm section background (hero, landmarks) |
| `--bg-raised` | `#FCEFD2` | Card backgrounds |
| `--ink` | `#221B12` | Primary text |
| `--ink-soft` | `#6B5F49` | Secondary/muted text |
| `--forest` | `#0B6B41` | Primary brand green |
| `--forest-2` | `#1FA35F` | Accent green |
| `--gold` | `#F2A400` | Primary brand gold |
| `--gold-soft` | `#FFD866` | Light gold accent |
| `--rust` | `#E8451F` | CTA / primary action color |
| `--teal` | `#0E8C8C` | Secondary accent (photo placeholders, leader frames) |
| `--teal-deep` | `#095F5F` | Teal gradient pair |
| `--line` | `rgba(34,27,18,0.12)` | Borders, dividers |

**Note on v1–v3 → v4:** Original palette (`#14442F` forest, `#C08A1C` gold, `#AB4B29` rust) was
tested with the team and felt "matte"/flat. v4 pushes saturation up across the board —
this is the palette to build from.

**No dark mode.** Light theme only, by explicit team decision.

## Typography

- **Display / headings:** [Fraunces](https://fonts.google.com/specimen/Fraunces) (variable, italic used for emphasis)
- **Body / UI:** [Work Sans](https://fonts.google.com/specimen/Work+Sans)
- Both load via Google Fonts — see `<head>` of `homepage-preview.html` for exact import.

## Layout Principles

1. **Hero leads with nostalgia** — a "memory board" of tilted photo placeholders (polaroid style), not a stock banner.
2. **Leaders strip** — horizontally scrollable, one entry per administrator/governor since 1996. Expected to stay a fixed, known list (7 entries).
3. **Landmarks strip** — horizontally scrollable, open-ended (currently 4 placeholder entries + "more coming" card). Content owned jointly with Member 7 (Culture & Tourism).
4. **Moments/milestones strip** — horizontally scrollable, open-ended, rendered on a solid forest-green color band for contrast. Content pending more entries from Member 4 (Research & History).
5. **Feature grid** — asymmetric "bento" layout, not identical SaaS-style cards. Timeline & Ask Ekiti get larger tiles as flagship features.
6. **Photo placeholders** — every real photo slot (leaders, landmarks, hero) is a styled placeholder, not a real image. **Placeholders are acceptable for initial launch.** Real photography should not block technical implementation — swap in as photos are sourced and cleared.

## Homepage & Mobile Behavior

These are implementation-relevant behaviors, not just visual notes:

- **Header:** sticky to the top of the viewport (`position: sticky`), respects safe-area insets on notched devices. Nav links (Timeline, Explore Ekiti, etc.) collapse and hide below 820px width — mobile should rely on the primary CTA button only, or a hamburger menu if Engineering wants to add one (not specified in this pass).
- **Hero:** two-column layout (text + photo collage) above ~940px; stacks to a single column below that, text first, collage second.
- **Leaders / Landmarks / Moments sections:** all three are horizontal scroll strips (`overflow-x: auto`) at every screen size — this is deliberate, not a mobile fallback. It's how new entries get added without breaking layout.
- **Feature grid:** 6-column bento grid above 900px, collapses to 2 columns below that. Card spans are defined in the CSS (`c-timeline`, `c-ask` etc. span 3 columns of 6; `c-kb` spans all 6).
- **Safe-area handling:** page uses `env(safe-area-inset-top/bottom)` padding throughout — required for iOS devices with notches/dynamic island.
- **No dark mode.** Confirmed team decision — do not implement a `prefers-color-scheme` branch.

## Open items / dependencies

- [ ] Real, rights-cleared photos for all 7 leaders (Member 8 — verification process). **Not a launch blocker** — placeholders ship as-is if not ready in time.
- [ ] Real, rights-cleared photos for landmarks (Member 7 — sourcing). **Not a launch blocker.**
- [ ] Additional landmark entries beyond the initial 4 (Member 7 + Member 6)
- [ ] Additional milestone entries for "Moments that shaped us" (Member 4)
- [ ] Final logo/wordmark treatment beyond text lockup — non-blocking, can follow launch
- [ ] Any implementation questions → coordinate directly with Member 6 rather than guessing
