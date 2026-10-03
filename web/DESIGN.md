# Tokn Investments — design direction

## Product

**Tokn Investments** is an investment-intelligence and verification UI for
tokenized infrastructure / DePIN / RWA assets.

Flow: **Browse assets → select → reusable asset intelligence page**.

Central idea: *don’t just show what an asset says about itself — show what
the available evidence supports.*

## Visual reference

Attached liquid-glass mock (neutral frosted panels, fine borders, soft
depth, technical mono). Language to preserve — not pixel-perfect layout.

| Token | Choice | Why |
| --- | --- | --- |
| Type | **VCR OSD Mono** (+ system mono fallback) | Technical / research feel per brief |
| Ground | Soft gray studio gradient + faint grid | Not flat white; not purple SaaS |
| Surface | Frosted glass (`backdrop-filter`, white/60–80, 1px border) | Reference panels |
| Accent | Zinc ink + functional green / amber / red for status only | No neon Web3 |
| Motion | Short fade / layout transitions (`motion`) | Presence, not noise |

## Data honesty

| Kind | Examples in this system | UI label |
| --- | --- | --- |
| **Live (scored now)** | Four scores recomputed on each API request (`scored_at`) | Scored |
| **Snapshot / refreshed** | `data_pulled_at`, claims, identity, yield inputs | Snapshot |
| **Derived snapshot** | Emission token `current_price` inside risk components (Glow) | Snapshot (registry) |
| **Not available** | Spot market price, 24h change, market cap, volume, FDV | Not available |

No fabricated market tickers or verification events.

## Score scale

Engine scores are **0–100** (higher is better on each axis). UI displays
that scale. Liquidity axis is labeled for **contractual exit / transfer
conditions**, not order-book depth.

## Architecture

- `/` — discovery grid from `GET /v1/assets`
- `/assets/[assetId]/` — one reusable `AssetDetailPage`
- Static export + `generateStaticParams` from `storage/` (+ live API when reachable)
