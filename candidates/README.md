# Candidates — discovery research log

This directory is a **public, honest research log** for evaluating **physical
real-world asset / infrastructure** tokenization projects as possible future
yield-opportunity sources. Tokn prioritizes tokens with economic exposure to
identifiable physical assets — not generic DePIN network/utility tokens. It is
**not** a product surface: nothing here is live on the platform, scored by the
engine, or exposed by the API.

## Hard rules

1. **Investigation only.** Work under `candidates/` produces FINDINGS documents
   (and, when classified `candidate-for-adapter`, an additive `ADAPTER_SPEC.md`)
   for human review. It does **not** add adapters, schema fields, storage
   snapshots, scoring weights, or API routes.
2. **No adapter code in this phase** — even if the classification is
   `candidate-for-adapter` and an `ADAPTER_SPEC.md` exists. Building an adapter
   is a separate, human-initiated task after an explicit greenlight of the spec.
3. **Same evidence standard as `adapters/FINDINGS.md`:** cite real URLs,
   contract addresses, and reachable endpoints; state what was checked; use an
   explicit “what’s actually reachable right now” table; never fabricate or
   round up past the evidence.
4. **One of four classifications, stated at the top** of every
   `candidates/<name>/FINDINGS.md` (see below).

## Adapter-spec research (additive)

For candidates already classified **`candidate-for-adapter`**,
`scheduler/run_research_agent.py` runs a deeper research pass and writes
`candidates/<slug>/ADAPTER_SPEC.md` without modifying FINDINGS.md.

- Triggered automatically at the end of `run_discovery.py` when the verdict is
  `candidate-for-adapter` (disable with `--skip-research`).
- Can also be run alone: `python3 scheduler/run_research_agent.py --candidate-name AgriFi`
- Output is a document only — **nothing is auto-approved**; a human still
  decides whether to greenlight bespoke adapter work.
## The four classifications

| Classification | Meaning |
| --- | --- |
| **`candidate-for-adapter`** | Passive capital-provision model (same family as Glow / Elmnts / RealT): a real, reachable data source was found. Ready for a human to decide whether to greenlight adapter work. **Still no adapter in this phase.** |
| **`not-yet-investable`** | Legitimate-seeming project, but nothing is actually live yet (e.g. regulatory engagement with zero issued tokens / no live participation path). |
| **`wrong-model`** | Active-operator / contribute-your-own-hardware (or equivalent node-operation) model — Helium / Render / Filecoin / Bittensor / Internet Computer style. Explain specifically why, citing the real mechanism found. |
| **`insufficient-information`** | Could not reach a confident classification. State exactly what is still unknown and what to check next. |

## How to run this process for a new candidate

1. **Create a branch** (do not edit live adapters/schema/scoring/storage/api).
2. **Create** `candidates/<slug>/` (lowercase slug, e.g. `aethir`).
3. **Investigate** using the checklist below. Prefer official docs, official
   portals, and direct RPC / public HTTP probes over aggregators or secondary
   blogs. Record dates and verbatim evidence.
4. **Write** `candidates/<slug>/FINDINGS.md` with:
   - Classification banner at the **top**
   - What was checked (with URLs / addresses)
   - Reachability table
   - Mechanism analysis vs this platform’s capital-provision bar
   - Explicit unknowns / next checks if any
5. **Add a row** to the index table in this README.
6. **Open a PR that only touches `candidates/`.** Confirm the diff file list
   contains nothing outside this directory.
7. **Stop.** Do not open adapter PRs from this process.

### Investigation checklist (minimum)

- [ ] Official site + docs: what participation tiers exist?
- [ ] For each tier: must the participant **operate hardware / run a node
      client**, or is there a genuine **capital-only** path (stake/license that
      finances an asset without operating infrastructure)?
- [ ] Payout shape: direct claim on external revenue vs protocol-token emission
      for network work?
- [ ] Public API / portal / on-chain contracts: what is reachable *without*
      partner keys?
- [ ] Secondary markets / transferability only as supporting context — not as
      proof of investability alone.
- [ ] Classification chosen and justified against the four options above.

## Index

| Candidate | Classification | Date investigated | FINDINGS |
| --- | --- | --- | --- |
| xU3O8 | `insufficient-information` | 2026-10-06 | [`xu3o8/FINDINGS.md`](./xu3o8/FINDINGS.md) |
| WTIC | `candidate-for-adapter` | 2026-10-06 | [`wtic/FINDINGS.md`](./wtic/FINDINGS.md) |
| RealX | `candidate-for-adapter` | 2026-10-06 | [`realx/FINDINGS.md`](./realx/FINDINGS.md) |
| Parcl | `insufficient-information` | 2026-10-05 | [`parcl/FINDINGS.md`](./parcl/FINDINGS.md) |
| Agro Digital Token | `insufficient-information` | 2026-10-04 | [`agro-digital-token/FINDINGS.md`](./agro-digital-token/FINDINGS.md) |
| Toucan Protocol | `insufficient-information` | 2026-10-04 | [`toucan-protocol/FINDINGS.md`](./toucan-protocol/FINDINGS.md) |
| Mineralized | `insufficient-information` | 2026-10-04 | [`mineralized/FINDINGS.md`](./mineralized/FINDINGS.md) |
| Blocksquare | `candidate-for-adapter` | 2026-10-04 | [`blocksquare/FINDINGS.md`](./blocksquare/FINDINGS.md) |
| Tangible | `candidate-for-adapter` | 2026-10-04 | [`tangible/FINDINGS.md`](./tangible/FINDINGS.md) |
| Landshare | `insufficient-information` | 2026-10-04 | [`landshare/FINDINGS.md`](./landshare/FINDINGS.md) |
| Energy Web | `insufficient-information` | 2026-10-04 | [`energy-web/FINDINGS.md`](./energy-web/FINDINGS.md) |
| Lofty | `insufficient-information` | 2026-10-04 | [`lofty/FINDINGS.md`](./lofty/FINDINGS.md) |
| AgriFi | `candidate-for-adapter` | 2026-10-03 | [`agrifi/FINDINGS.md`](./agrifi/FINDINGS.md) · [`ADAPTER_SPEC.md`](./agrifi/ADAPTER_SPEC.md) |
| PTX | `candidate-for-adapter` | 2026-09-11 | [`ptx/FINDINGS.md`](./ptx/FINDINGS.md) |
| Mining royalty tokenization (category) | `insufficient-information` | 2026-08-21 | [`mining-royalty-tokenization/FINDINGS.md`](./mining-royalty-tokenization/FINDINGS.md) |
| Tokenized farmland (category) | `insufficient-information` | 2026-08-21 | [`tokenized-farmland/FINDINGS.md`](./tokenized-farmland/FINDINGS.md) |
| Decentralized Space / Decen Space | `not-yet-investable` | 2026-08-21 | [`decentralized-space/FINDINGS.md`](./decentralized-space/FINDINGS.md) |
| Spacecoin | `wrong-model` | 2026-08-21 | [`spacecoin/FINDINGS.md`](./spacecoin/FINDINGS.md) |
| Aethir | `wrong-model` | 2026-08-19 | [`aethir/FINDINGS.md`](./aethir/FINDINGS.md) |
