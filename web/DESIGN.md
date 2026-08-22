# Public scores page — design direction

**Product register:** verification instrument, not a growth landing page.
Precision over excitement. Someone should be able to paste this URL into X
or Moltbook and have it read as a serious read-only window into the live
scoring API — the same numbers the API returns, nothing else.

## Typography

| Role | Face | Why |
| --- | --- | --- |
| Display / section titles | **Newsreader** | Editorial serif; authority without “fintech startup” gloss |
| Body / UI labels | **IBM Plex Sans** | Engineered, tabular-friendly, not Inter/system default |
| Scores, IDs, timestamps | **IBM Plex Mono** | Numerals and asset IDs as data, not decoration |

Scale stays tight: one display size for the page title, small caps-ish
labels for axes, mono for the four score values.

## Color

Restrained paper / ink / oxide — no purple, no neon glow, no dark-mode
default.

| Token | Hex | Use |
| --- | --- | --- |
| `--paper` | `#F4F0E8` | Page ground (warm paper, not cream-terracotta cliché) |
| `--ink` | `#161412` | Primary text |
| `--muted` | `#6B645A` | Secondary labels |
| `--rule` | `#C9C1B4` | Hairlines / section dividers |
| `--panel` | `#FBF8F2` | Slight lift for asset panels (border, not shadow card) |
| `--oxide` | `#7A3E2E` | Sole accent (links, focus, active sort) |
| `--proof` | `#1E4A3A` | `cryptographic-onchain-proof` badge |
| `--unverified` | `#8A5A1E` | `self-reported-unverified` badge |
| `--chart` | `#2A4560` | Single series stroke |

Badges are outlined or solid fills of `--proof` / `--unverified` — visually
distinct at a glance, never both the same gray pill.

## Layout / hierarchy

1. **Masthead** — product name as the hero signal (“Scored Assets”), then
   one honest sentence. No hero image, no CTA cluster, no stats strip.
2. **Assets** — primary band. Each asset is a bordered panel (interaction
   surface for expand/sort), not a floating shadow card. Four-axis score
   strip in mono. History chart only when ≥2 API snapshots; single-point
   state is labeled, not faked into a trend.
3. **Recent findings** — equal weight. Timeline of real investigations
   (GLW −94% peak decline, Aethir / Spacecoin `wrong-model`). Proof of
   work, not blog fluff.
4. **Methodology** — pulled from `GET /v1/methodology`, not rewritten.
5. **Footer** — live API base, MCP note, GitHub.

Max width ~960px, generous vertical rhythm, hairline rules between bands.
Desktop and mobile: one column; score strip wraps cleanly.

## Motion (purposeful only)

| Motion | Purpose |
| --- | --- |
| Score count-up (mono numerals) | Make newly loaded API values noticeable as *data arriving* |
| Chart line draw-in once | Reveal series formation; skipped when only one point |
| Filter/sort layout transition | Clarify reordering — not ornamental hover bounce |

No background particle fields, no looping logo spin, no stagger that
delays reading.

## Chart pairing (confirmed)

shadcn/ui **Chart** components are built on **Recharts** (current docs:
Recharts v3). Use `ChartContainer` + Recharts primitives so theming stays
on design tokens (`var(--chart)`), not a second visual language.

## Data rules

- Scores, tiers (via score `inputs`), history series, methodology: **only**
  `https://agent-native-depin-platform.onrender.com` (`/v1/assets`,
  `/v1/assets/{id}`, `/v1/methodology`).
- Findings feed: excerpts from repo investigation markdown (same evidence
  already published in-tree) — clearly labeled as investigation log, not
  live scores.
- Copy scan: no recommend / invest / buy / opportunity / alpha language.
