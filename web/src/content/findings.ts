export type Finding = {
  id: string;
  date: string;
  title: string;
  classification: string;
  summary: string;
  source_path: string;
  source_label: string;
};

/**
 * Excerpts from in-repo investigation logs. Not scores — those come only
 * from the live API. This feed is proof-of-process.
 */
export const FINDINGS: Finding[] = [
  {
    id: "glw-peak-decline",
    date: "2026-08-18",
    title: "GLW emission token — peak-to-spot decline",
    classification: "structural fact (payout mechanism)",
    summary:
      "On-chain Uniswap V2 GLW–USDG reserves investigation recorded a peak near 3.95 USDG/GLW versus a later spot near 0.23 — about −94% from peak. Documented as a property of token-emission payouts, not a misconduct claim. Used as an input to the risk_score emission-token peak-decline component.",
    source_path: "scoring/GLW_PRICE_EMISSIONS_FINDINGS.md",
    source_label: "GLW price & emissions findings",
  },
  {
    id: "aethir-wrong-model",
    date: "2026-08-19",
    title: "Aethir — Checker / host participation",
    classification: "wrong-model",
    summary:
      "Live GPU DePIN with docs and Checker License NFTs. Checked paths (Cloud Host, Checker Node including NaaS, ATH staking) require operating or delegating an active client earning protocol-token emissions for validation work — not a passive capital claim on financed capacity or external rental revenue.",
    source_path: "candidates/aethir/FINDINGS.md",
    source_label: "Aethir candidate findings",
  },
  {
    id: "spacecoin-wrong-model",
    date: "2026-08-21",
    title: "Spacecoin — SpaceRouter provider path",
    classification: "wrong-model",
    summary:
      "Official docs describe SpaceRouter Proxy providers who run a home/node app, stake SPACE, and earn for served bandwidth. Staking documentation states staking alone does not qualify for SpaceRouter rewards — node operation is required. Capital-only bar not met.",
    source_path: "candidates/spacecoin/FINDINGS.md",
    source_label: "Spacecoin candidate findings",
  },
];
