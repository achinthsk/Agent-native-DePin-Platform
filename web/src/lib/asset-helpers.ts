import type { AssetClaim, ScoredAsset } from "@/lib/api";
import { verificationTier } from "@/lib/api";

export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toFixed(1);
}

export function scoreTone(
  value: number | null | undefined,
  insufficient?: boolean,
): "missing" | "low" | "mid" | "high" {
  if (insufficient || value === null || value === undefined) return "missing";
  if (value >= 70) return "high";
  if (value >= 40) return "mid";
  return "low";
}

export function assetClassLabel(assetClass: string): string {
  switch (assetClass) {
    case "solar-depin":
      return "DePIN / Solar Infrastructure";
    case "real-estate-rental":
      return "RWA / Real Estate Rental";
    case "oil-gas-royalty":
      return "RWA / Oil & Gas Royalty";
    case "regulated-fund":
      return "Regulated Fund";
    case "regulated-credit":
      return "Regulated Credit";
    default:
      return assetClass;
  }
}

export function categoryShort(assetClass: string): string {
  switch (assetClass) {
    case "solar-depin":
      return "Solar Infrastructure";
    case "real-estate-rental":
      return "Real Estate Rental";
    case "oil-gas-royalty":
      return "Oil & Gas Royalty";
    default:
      return assetClass;
  }
}

/** Known protocol tickers only — never invent spot symbols. */
export function tokenSymbol(asset: ScoredAsset): string | null {
  if (asset.source_platform === "glow") return "GLW";
  return null;
}

export function monogram(name: string): string {
  const parts = name.replace(/[^a-zA-Z0-9 ]/g, " ").trim().split(/\s+/);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

export type FreshnessKind = "scored" | "snapshot" | "unavailable";

export function snapshotFreshness(asset: ScoredAsset): {
  kind: FreshnessKind;
  label: string;
  detail: string;
} {
  if (!asset.data_pulled_at) {
    return {
      kind: "unavailable",
      label: "Not available",
      detail: "No data_pulled_at on this asset",
    };
  }
  const age =
    typeof asset.snapshot_age_days === "number"
      ? `${asset.snapshot_age_days.toFixed(1)}d age`
      : null;
  return {
    kind: "snapshot",
    label: "Snapshot",
    detail: age
      ? `${asset.data_pulled_at} · ${age}`
      : asset.data_pulled_at,
  };
}

export function scoredFreshness(asset: ScoredAsset): {
  kind: FreshnessKind;
  label: string;
  detail: string;
} {
  if (!asset.scored_at) {
    return {
      kind: "unavailable",
      label: "Not available",
      detail: "Scores not yet computed",
    };
  }
  return {
    kind: "scored",
    label: "Scored",
    detail: asset.scored_at,
  };
}

export type VerificationState =
  | "discrepancy"
  | "proof"
  | "self-reported"
  | "unknown";

export function overallVerificationState(
  asset: ScoredAsset,
): VerificationState {
  const claims = asset.claims || [];
  if (claims.some((c) => c.conflicts_with)) return "discrepancy";
  const tier = verificationTier(asset);
  if (
    tier === "cryptographic-onchain-proof" ||
    tier === "independent-third-party-audit" ||
    tier === "remote-sensing-verified"
  ) {
    return "proof";
  }
  if (tier === "self-reported-unverified") return "self-reported";
  return "unknown";
}

export function verificationStateLabel(state: VerificationState): string {
  switch (state) {
    case "discrepancy":
      return "Discrepancy";
    case "proof":
      return "On-chain / verified tier";
    case "self-reported":
      return "Self-reported";
    default:
      return "Unknown";
  }
}

export function claimStatus(
  claim: AssetClaim,
  all: AssetClaim[],
): "discrepancy" | "verified" | "self-reported" {
  if (claim.conflicts_with) return "discrepancy";
  if (
    claim.verification_tier === "cryptographic-onchain-proof" ||
    claim.verification_tier === "independent-third-party-audit" ||
    claim.verification_tier === "remote-sensing-verified"
  ) {
    return "verified";
  }
  void all;
  return "self-reported";
}

export function claimTitle(claimId: string): string {
  const map: Record<string, string> = {
    weekly_infrastructure_emissions_glw_documented:
      "Weekly infrastructure emissions (documented)",
    weekly_infrastructure_emissions_glw_onchain_median:
      "Weekly infrastructure emissions (on-chain median)",
    "yield_profile.realized_yield_pct": "Realized yield %",
    "yield_profile.advertised_yield_pct": "Advertised yield %",
  };
  return map[claimId] || claimId.replace(/_/g, " ");
}

export function formatClaimValue(value: unknown): string {
  if (value === null || value === undefined) return "Not available";
  if (typeof value === "number") {
    if (Number.isInteger(value) && Math.abs(value) >= 1000) {
      return value.toLocaleString("en-US");
    }
    return String(value);
  }
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

export function conflictingClaimPairs(
  claims: AssetClaim[],
): { a: AssetClaim; b: AssetClaim }[] {
  const byId = new Map(claims.map((c) => [c.claim, c]));
  const seen = new Set<string>();
  const pairs: { a: AssetClaim; b: AssetClaim }[] = [];
  for (const c of claims) {
    if (!c.conflicts_with) continue;
    const other = byId.get(c.conflicts_with);
    if (!other) continue;
    const key = [c.claim, other.claim].sort().join("|");
    if (seen.has(key)) continue;
    seen.add(key);
    pairs.push({ a: c, b: other });
  }
  return pairs;
}

export function snapshotHeadline(asset: ScoredAsset): {
  primary: string;
  secondary: string;
  body: string;
} {
  const y = asset.yield_score;
  const r = asset.risk_score;
  const conf = asset.data_confidence_score;
  const hasConflict = (asset.claims || []).some((c) => c.conflicts_with);

  if (y?.insufficient_data) {
    return {
      primary: "Yield inputs incomplete.",
      secondary: hasConflict
        ? "Verification gaps remain."
        : "Compare remaining axes with care.",
      body: "Advertised and realized yield are both unavailable for this snapshot, so yield_score is insufficient_data. Risk, exit conditions, and data confidence still reflect observable fields.",
    };
  }

  const riskV = r?.value;
  const confV = conf?.value;
  if (typeof riskV === "number" && riskV >= 60 && !hasConflict) {
    return {
      primary: "Risk quality mid-to-high on this axis.",
      secondary: "Read claims and evidence before comparing.",
      body: "Scores are descriptive and comparative only — not investment advice. Each axis is separate; they are never blended into a single ranking number.",
    };
  }

  return {
    primary: hasConflict
      ? "Evidence conflict on a yield-related claim."
      : "Four-axis snapshot from the live scoring API.",
    secondary:
      typeof confV === "number" && confV < 50
        ? "Data confidence is limited."
        : "Inspect claims and freshness.",
    body: "Scores are computed from storage snapshots via scoring.engine. Higher is better on each axis. Liquidity here means contractual exit / transfer conditions, not order-book depth.",
  };
}

export type HistoryEvent = {
  at: string;
  title: string;
  detail: string;
};

/** Derive verification/history events only from real snapshot history. */
export function deriveHistoryEvents(history: ScoredAsset[]): HistoryEvent[] {
  const sorted = [...history].sort((a, b) =>
    (a.snapshot_file || "").localeCompare(b.snapshot_file || ""),
  );
  const events: HistoryEvent[] = [];
  let prev: ScoredAsset | null = null;
  for (const snap of sorted) {
    const at = snap.data_pulled_at || snap.scored_at || snap.snapshot_file || "";
    if (!prev) {
      events.push({
        at,
        title: "First stored snapshot",
        detail: `Snapshot ${snap.snapshot_file || "unknown"} recorded.`,
      });
    } else {
      if (prev.data_pulled_at !== snap.data_pulled_at) {
        events.push({
          at,
          title: "Snapshot refreshed",
          detail: `data_pulled_at ${prev.data_pulled_at || "—"} → ${snap.data_pulled_at || "—"}.`,
        });
      }
      const prevClaims = prev.claims || [];
      const nextClaims = snap.claims || [];
      if (prevClaims.length === 0 && nextClaims.length > 0) {
        const conflict = nextClaims.some((c) => c.conflicts_with);
        events.push({
          at: nextClaims[0]?.verified_at || at,
          title: conflict
            ? "Claim-level conflict recorded"
            : "Claim-level provenance added",
          detail: conflict
            ? "Documentation and independent observation diverge on a yield-related claim."
            : `${nextClaims.length} yield claim(s) attached to the asset instance.`,
        });
      }
    }
    prev = snap;
  }
  return events.reverse();
}

export const WATCHLIST_KEY = "tokn.watchlist.v1";

export function readWatchlist(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(WATCHLIST_KEY);
    const parsed = raw ? (JSON.parse(raw) as unknown) : [];
    return Array.isArray(parsed)
      ? parsed.filter((x) => typeof x === "string")
      : [];
  } catch {
    return [];
  }
}

export function writeWatchlist(ids: string[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(WATCHLIST_KEY, JSON.stringify(ids));
}
