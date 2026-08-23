# Public scores page — design direction (v2)

## What “bklit” actually is

**Confirmed product: [Bklit UI](https://bklit.com)** (registry/docs also at
[ui.bklit.com](https://ui.bklit.com), source
[github.com/bklit/bklit-ui](https://github.com/bklit/bklit-ui)).

It is an **open-source charts & data-visualization component library** for
React / shadcn — line, area, bar, sparklines, KPI “stat cards” with
animated averages, Studio playground, etc. An older **Bklit Analytics**
hosted SaaS was discontinued; the live product people mean by “bklit” in
a UI context is this chart/UI library, not a guess at a similarly spelled
name.

## Kokonut UI (confirmed)

**[KokonutUI](https://kokonutui.com)** — 100+ open-source React components
built on **Tailwind + shadcn/ui + Motion** (`motion` / Framer Motion).
Registry install via `@kokonutui`. Aesthetic from live demos/docs:

- Neutral zinc/black surfaces, `rounded-xl` cards
- Soft `border-neutral-200/50` + light gradient fills
  (`from-neutral-50/80 → neutral-50`), dark variants
- Hover border + soft shadow lift
- `tracking-tight` sans typography (product UI, not editorial serif)
- Stagger / fade / layout motion as first-class UX

## Design direction for this page

Leave the paper/ink/oxide + Newsreader register behind. Match the
**product** feel of Kokonut cards + **Bklit** chart/KPI density.

| Token | Choice | Why |
| --- | --- | --- |
| Type | **Plus Jakarta Sans** + **JetBrains Mono** | Product UI sans (Kokonut-like tracking-tight), mono for IDs/scores — not Inter, not editorial serif |
| Ground | `#FAFAFA` → zinc-50 | Clean product canvas (Bklit/Kokonut light demos) |
| Surface | white cards, `rounded-xl`, `border-zinc-200` | Kokonut bento/card language |
| Accent | zinc-900 + a single emerald for proof tier | Serious tool; no purple SaaS glow |
| Charts | shadcn Chart + Recharts (Bklit-style sparklines/KPI strip) | Keep live API series; no fake trends |
| Motion | `motion` (motion.dev) | Count-up, chart draw-in, filter reorder — same purposeful rules as before |

### Hierarchy

1. Compact product masthead (name + one honest line + API links)
2. Filter/sort bar + live asset cards (score grid + history)
3. Findings timeline as equal-weight section
4. Methodology pulled from API

### Non-negotiables (unchanged from PR #13)

- Data only from live `/v1/assets`, `/v1/assets/{id}`, `/v1/methodology`
- No fabricated trend lines when &lt; 2 snapshots
- No investment-advice language
