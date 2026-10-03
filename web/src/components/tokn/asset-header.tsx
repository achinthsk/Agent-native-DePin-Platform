"use client";

import Link from "next/link";
import type { ScoredAsset } from "@/lib/api";
import { emissionRegistryPrice } from "@/lib/api";
import {
  assetClassLabel,
  monogram,
  scoredFreshness,
  snapshotFreshness,
  tokenSymbol,
} from "@/lib/asset-helpers";
import { FreshnessIndicator, WatchlistButton } from "@/components/tokn/watchlist-freshness";

export function AssetHeader({ asset }: { asset: ScoredAsset }) {
  const symbol = tokenSymbol(asset);
  const snap = snapshotFreshness(asset);
  const scored = scoredFreshness(asset);
  const registry = emissionRegistryPrice(asset);

  return (
    <section className="glass p-5 sm:p-6">
      <Link
        href="/"
        className="text-[11px] text-[var(--tokn-muted)] hover:text-[var(--tokn-ink)]"
      >
        ← Back to assets
      </Link>
      <div className="mt-4 flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 items-start gap-4">
          <div className="grid h-14 w-14 shrink-0 place-items-center rounded-full border border-[rgba(26,28,31,0.1)] bg-white/70 text-sm">
            {monogram(asset.name)}
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl sm:text-3xl">{asset.name}</h1>
              {symbol ? <span className="pill pill-muted">{symbol}</span> : null}
            </div>
            <p className="mt-2 text-[11px] text-[var(--tokn-muted)]">
              {assetClassLabel(asset.asset_class)}
            </p>
            <p className="mt-3 max-w-2xl text-[12px] leading-relaxed text-[var(--tokn-muted)]">
              {asset.description_text || "No description on this snapshot."}
            </p>
          </div>
        </div>

        <div className="w-full shrink-0 lg:w-64">
          <p className="eyebrow">Token price</p>
          {registry ? (
            <>
              <p className="mt-1 text-3xl">
                {registry.current.toFixed(4)}
              </p>
              <p className="mt-1 text-[11px] text-[var(--tokn-muted)]">
                USDG per GLW · registry snapshot
                {registry.asOf ? ` · as of ${registry.asOf}` : ""}
              </p>
              <p className="mt-2 text-[10px] text-[var(--tokn-muted)]">
                Not a live exchange ticker. From emission price history used in
                risk scoring (peak {registry.peak.toFixed(4)}).
              </p>
            </>
          ) : (
            <>
              <p className="mt-1 text-2xl">Not available</p>
              <p className="mt-1 text-[11px] text-[var(--tokn-muted)]">
                No live spot price field in the API.
              </p>
            </>
          )}
          <p className="mt-3 text-[11px] text-[var(--tokn-muted)]">
            24h change:{" "}
            <span className="pill pill-muted">Not available</span>
          </p>
          <div className="mt-4 space-y-3">
            <FreshnessIndicator {...snap} />
            <FreshnessIndicator {...scored} />
            <WatchlistButton assetId={asset.asset_id} />
          </div>
        </div>
      </div>
    </section>
  );
}
