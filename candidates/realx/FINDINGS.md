# RealX — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-06
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Coverage test: RealX Investment Token (Thailand SEC-approved) — tokenized luxury Bangkok real-estate (Park Origin properties)

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | RealX (`realx`) |
| Category | `real_estate` |
| Official website | `https://realxtoken.finance/en` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Official/seed language indicates a physical real-world asset or identifiable asset pool (see excerpts). |
| Why it qualifies as physical RWA | Physical + ownership/economic-exposure markers present in notes/seeds/reachable text. |
| Why it is NOT generic DePIN | Not classified as generic DePIN: evidence points to asset claim / financing exposure rather than network-work utility alone. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `backlog_match` |
| Physical-asset gate | `physical-rwa` |
| Classification | `candidate-for-adapter` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://realxtoken.finance/en` | HTTP 200 — live (text/html) |
| `https://realxtoken.finance/en/assets` | HTTP 200 — live (text/html) |
| `https://realxtoken.finance/en/investor` | HTTP 200 — live (text/html) |
| `https://static.tokenx.finance/projects/realx/RealX_Whitepaper_Revised_230731_2.pdf` | HTTP 200 — live (application/pdf) |
| `https://market.sec.or.th/public/ipos/IPOSTD01.aspx?TransID=494728&lang=en` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://realxtoken.finance/en`

> RealX Home Assets Investor HHR Whitepaper FAQ Contact us ไทย EN REALX INVESTMENT TOKEN THE REAL ESTATE BACKED TOKEN Whitepaper Introducing RealX Investment Token is the First Asset-Backed Token in Thailand under the approval of the Security Exchange and Commissions of Thailand (SEC) and fully complies with the relevant regulations surrounding this nascent industry. RealX has raised over $60+ million during its fundraising period for the purpose of asset acquisition and tokenization, of which a t

### `https://realxtoken.finance/en/assets`

> Assets - RealX Home Assets Investor HHR Whitepaper FAQ Contact us ไทย EN Underlying Assets Totaling 244 rooms The underlying assets, namely Park Origin Promphong, Park Origin Thonglor, and Park Origin Phayathai, are assets located in the prime areas of Bangkok with a proven track record and are sought after by the market. Investment Proportion 27.46% Calculate as 67 Rooms Investment Proportion 38.11% Calculate as 93 Rooms Investment Proportion 27.46% Calculate as 84 Rooms The last, most distingu

### `https://realxtoken.finance/en/investor`

> RealX Home Assets Investor HHR Whitepaper FAQ Contact us ไทย EN Real Estate Exponential Co., Ltd. @RealXToken [email protected] 989 Siam Piwat Tower Floor 12A Rama I Rd. Pathumwan, Bangkok, 10330 Home Investor Whitepaper Contact us Assets HHR FAQ Privacy Policy Copyright © 2026 Real Estate Exponential Co., Ltd.

### `https://static.tokenx.finance/projects/realx/RealX_Whitepaper_Revised_230731_2.pdf`

> %PDF-1.6 %���� 48434 0 obj <</Filter/FlateDecode/First 179/Length 1548/N 17/Type/ObjStm>>stream h�Ԙ�NI�_�/���� EHA� M������`��� �����������"Z����ǚ��� l4� ),d*p% �����5+�PZ)�*T����:�����j��:�]\����� tP��Q�dk+6S�4��5�&�*a�� {Jt�x� ޓzPR����hx�������鸝u���y󱽜,��ݳ�x��}� oon��5���9���`O� � ێ�YҢ����U;���DP�9j��=/bs< ].�m����`�O��>p� *^�p���z2�{�~1���צɴռ��}����m^ � ���ؽ��t�}�n�vW����z4��^/�}ڍ�����r� � �����7gw7-�%���n�h>��cc���Ѳ�!�v��[b������7�TN���'�GoF7��I7G�_,7�� �f o�t�f�RNU�9�&

### `https://market.sec.or.th/public/ipos/IPOSTD01.aspx?TransID=494728&lang=en`

> Digital Token Prospectus {1} ##LOC[OK]## {1} ##LOC[OK]## ##LOC[Cancel]## {1} ##LOC[OK]## ##LOC[Cancel]## Digital Token Detail Digital Token Name : RealX Investment Token Digital Token Issuer : REAL ESTATE EXPONENTIAL COMPANY LIMITED Filing Acknowledge Date : 04/01/2023 Filing First Date : 20/03/2023 Effective Date : 19/06/2023 Sell Begin Date : 01/07/2023 Sell End Date : 31/08/2023 Digital Token Type : Token Digital for investment Offering Type : Initial Coin Offering ICO Portal : TOKEN X COMPAN


## Classification rationale

**`candidate-for-adapter`**

Reachable seeds describe a capital / ownership / royalty-style path tied to a physical-RWA thesis without clear operator-hardware requirements. This is a **first-pass** signal only — a human must greenlight any adapter work separately. No adapter is created by this cycle.

## Can the four scores be computed?

**No.** Discovery does not invent scores. An adapter + real `storage/`
snapshot would be required first, and only after a human greenlights
adapter work for a `candidate-for-adapter` disposition.

## What would need to change for this to become scoreable

1. Human review of this FINDINGS.md.
2. If promoted: a dedicated adapter under `adapters/` (SourceError
   discipline; no fabrication).
3. At least one real snapshot under `storage/<asset-id>/`.
4. Confirmation that payout / claim mechanics fit this project's
   capital-provision bar — or keep `wrong-model` / `not-yet-investable`
   / `insufficient-information` as the honest outcome.

## Scheduler notes

- One candidate per cycle (this file).
- Already-investigated slugs (existing FINDINGS.md / candidate state) are
  skipped on future discovery runs even if `next_index` is stale.
- Output is intended to land as a PR for human merge — nothing auto-merges.
