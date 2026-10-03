/** Live scored-assets API client — sole source for scores, claims, methodology. */

export const LIVE_API_FALLBACK =
  "https://agent-native-depin-platform.onrender.com";

export const GITHUB_REPO =
  "https://github.com/achinthsk/Agent-native-DePin-Platform";

export function resolveApiBase(): string {
  if (
    typeof process !== "undefined" &&
    process.env.NEXT_PUBLIC_API_BASE !== undefined
  ) {
    return process.env.NEXT_PUBLIC_API_BASE.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    if (window.location.hostname.endsWith(".onrender.com")) {
      return "";
    }
  }
  return LIVE_API_FALLBACK;
}

export type ScoreObject = {
  value: number | null;
  insufficient_data?: boolean;
  direction?: string;
  reason?: string;
  mode?: string;
  inputs?: Record<string, unknown>;
  components?: Record<string, unknown>;
  whitelist_haircut_applied?: boolean;
};

export type AssetClaim = {
  claim: string;
  value: unknown;
  verification_tier: string;
  fact_domain: string;
  evidence_source: string;
  verified_at: string;
  conflicts_with: string | null;
};

export type ScoredAsset = {
  asset_id: string;
  name: string;
  asset_class: string;
  source_platform: string;
  schema_version?: string;
  snapshot_file?: string;
  data_pulled_at?: string;
  snapshot_age_days?: number | null;
  description_text?: string | null;
  source_url?: string | null;
  retrieval_method?: string | null;
  payout_mechanism?: Record<string, unknown> | null;
  yield_profile?: Record<string, unknown> | null;
  verification?: {
    verification_tier?: string;
    verification_notes?: string;
  } | null;
  maturity?: Record<string, unknown> | null;
  liquidity?: Record<string, unknown> | null;
  exposure?: Record<string, unknown> | null;
  regulatory?: Record<string, unknown>;
  jurisdiction_note?: Record<string, unknown>;
  yield_score: ScoreObject;
  risk_score: ScoreObject;
  liquidity_score: ScoreObject;
  data_confidence_score: ScoreObject;
  weights_version?: string;
  scored_at?: string;
  claims?: AssetClaim[];
};

export type AssetsResponse = {
  query: Record<string, unknown>;
  total_matched: number;
  limit: number;
  offset: number;
  assets: ScoredAsset[];
  notes: string[];
};

export type AssetDetailResponse = {
  asset?: ScoredAsset | null;
  assets?: ScoredAsset[];
  notes?: string[];
  error?: string;
};

export type MethodologyResponse = {
  format: string;
  weights_path: string;
  methodology_path: string;
  content: unknown;
  notes: string[];
};

export function verificationTier(asset: ScoredAsset): string | null {
  const fromRoot = asset.verification?.verification_tier;
  const fromRisk =
    asset.risk_score?.inputs?.["verification.verification_tier"];
  const fromConf =
    asset.data_confidence_score?.inputs?.[
      "verification.verification_tier"
    ];
  const tier = (fromRoot ?? fromRisk ?? fromConf) as string | undefined;
  return tier || null;
}

export function realizedYieldPct(asset: ScoredAsset): number | null {
  const fromProfile = asset.yield_profile?.realized_yield_pct;
  if (typeof fromProfile === "number") return fromProfile;
  const v =
    asset.yield_score?.inputs?.["yield_profile.realized_yield_pct"];
  return typeof v === "number" ? v : null;
}

export function peakDeclinePct(asset: ScoredAsset): number | null {
  const v =
    asset.risk_score?.inputs?.["emission_token.peak_decline_pct"];
  if (typeof v === "number") return v;
  const comp =
    asset.risk_score?.components?.["emission_token_peak_decline"];
  if (comp && typeof comp === "object" && "decline_pct" in comp) {
    const d = (comp as { decline_pct?: unknown }).decline_pct;
    return typeof d === "number" ? d : null;
  }
  return null;
}

/** Snapshot registry price from risk components (Glow emissions), not a live ticker. */
export function emissionRegistryPrice(
  asset: ScoredAsset,
): { current: number; peak: number; asOf?: string } | null {
  const comp =
    asset.risk_score?.components?.["emission_token_peak_decline"];
  if (!comp || typeof comp !== "object") return null;
  const c = comp as {
    current_price?: unknown;
    peak_price?: unknown;
    current_as_of?: unknown;
  };
  if (typeof c.current_price !== "number" || typeof c.peak_price !== "number") {
    return null;
  }
  return {
    current: c.current_price,
    peak: c.peak_price,
    asOf: typeof c.current_as_of === "string" ? c.current_as_of : undefined,
  };
}

function joinUrl(base: string, path: string): string {
  if (!base) return path;
  return `${base.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API ${res.status} for ${url}`);
  return res.json() as Promise<T>;
}

export async function fetchAssets(
  base: string = resolveApiBase(),
): Promise<AssetsResponse> {
  return getJson<AssetsResponse>(
    joinUrl(base, "/v1/assets?latest_only=true&limit=50"),
  );
}

export async function fetchAsset(
  assetId: string,
  base: string = resolveApiBase(),
): Promise<ScoredAsset> {
  const data = await getJson<AssetDetailResponse>(
    joinUrl(
      base,
      `/v1/assets/${encodeURIComponent(assetId)}?latest_only=true`,
    ),
  );
  if (!data.asset) {
    throw new Error(data.error || `Asset not found: ${assetId}`);
  }
  return data.asset;
}

export async function fetchAssetHistory(
  assetId: string,
  base: string = resolveApiBase(),
): Promise<ScoredAsset[]> {
  const data = await getJson<AssetDetailResponse>(
    joinUrl(
      base,
      `/v1/assets/${encodeURIComponent(assetId)}?latest_only=false`,
    ),
  );
  if (Array.isArray(data.assets)) return data.assets;
  if (data.asset) return [data.asset];
  return [];
}

export async function fetchMethodologySummary(
  base: string = resolveApiBase(),
): Promise<MethodologyResponse> {
  return getJson<MethodologyResponse>(
    joinUrl(base, "/v1/methodology?format=summary"),
  );
}
