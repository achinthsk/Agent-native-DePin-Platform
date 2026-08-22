/** Live scored-assets API client — sole source for scores and methodology. */

export const LIVE_API_FALLBACK = "https://agent-native-depin-platform.onrender.com";

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
  inputs?: Record<string, unknown>;
  components?: Record<string, unknown>;
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
  regulatory?: Record<string, unknown>;
  jurisdiction_note?: Record<string, unknown>;
  yield_score: ScoreObject;
  risk_score: ScoreObject;
  liquidity_score: ScoreObject;
  data_confidence_score: ScoreObject;
  weights_version?: string;
  scored_at?: string;
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
  const fromRisk =
    asset.risk_score?.inputs?.["verification.verification_tier"];
  const fromConf =
    asset.data_confidence_score?.inputs?.[
      "verification.verification_tier"
    ];
  const tier = (fromRisk ?? fromConf) as string | undefined;
  return tier || null;
}

export function realizedYieldPct(asset: ScoredAsset): number | null {
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
