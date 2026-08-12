# Adapters — live / manual data pulls into `asset-v1.schema.json`

Investigation results (read first): [`FINDINGS.md`](./FINDINGS.md)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env if you have a preferred Ethereum RPC URL.
```

`.env` is gitignored. **Never commit API keys or RPC URLs that embed secrets.**

| Variable | Required? | Used by | Purpose |
| --- | --- | --- | --- |
| `ETH_RPC_URL` | Recommended | `glow_adapter.py` | Ethereum HTTPS RPC for `eth_call` |
| `GCA_API_BASE` | Optional | `glow_adapter.py` | Override GCA HTTP API base (default `http://95.217.194.59:35015`) |

Elmnts manual entry needs **no** secrets (there is no public API to call).

## Glow — `glow_adapter.py`

Pulls **real** farm registry data from the public GCA HTTP API and enriches
with on-chain MinerPoolAndGCA bucket state. See FINDINGS.md for why the
Control API was not used.

```bash
# One farm (GCA ShortID)
python3 adapters/glow_adapter.py --farm-id 1

# First N farms
python3 adapters/glow_adapter.py --all --limit 3

# Validate/print only
python3 adapters/glow_adapter.py --farm-id 1 --dry-run
```

### What it does on failure

- If the Ethereum RPC or GCA API is unreachable after retries: logs a clear
  `[FATAL]` / `[ERROR]` to **stderr** and exits **non-zero**.
- Writes **nothing** to `storage/` on source failure.
- If a built instance fails schema validation: logs errors and exits
  **non-zero** — **never** persists an invalid or partial file.
- Refuses to overwrite an existing `storage/{asset_id}/{timestamp}.json`.

### Yield honesty

`realized_yield_pct` is intentionally `null` today: farm→delegator GLW
attribution is not publicly recoverable (Control API DNS NXDOMAIN; on-chain
merkle leaves use payout wallets, not farm ShortIDs). The reason is stored in
`yield_calculation_basis`.

## Elmnts — `elmnts_manual_entry.py`

**Not a live adapter.** Built because FINDINGS.md found no public
programmatic source. Labels output as `retrieval_method: manual-entry` and
`verification_tier: self-reported-unverified`.

```bash
# Interactive prompts (TTY required)
python3 adapters/elmnts_manual_entry.py

# Non-interactive from an answers file
python3 adapters/elmnts_manual_entry.py \
  --from-file adapters/elmnts_manual_answers.example.json
```

Same validation + timestamped storage rules as Glow.

## Storage convention

```
storage/{asset_id}/{data_pulled_at}.json
```

The filename uses the instance's `data_pulled_at` ISO-8601 timestamp with `:`
→ `-` for filesystem safety; the JSON field keeps real ISO-8601.

## Validate everything in `storage/`

```bash
python3 schema/validate.py
```

`validate.py` checks the original examples **and** every `storage/**/*.json`
snapshot (all must PASS).
