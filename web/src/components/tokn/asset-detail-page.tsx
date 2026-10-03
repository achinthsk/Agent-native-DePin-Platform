"use client";

import { useEffect, useMemo, useState } from "react";
import { AssetHeader } from "@/components/tokn/asset-header";
import { AssetIntelligence } from "@/components/tokn/asset-intelligence";
import { ClaimsList } from "@/components/tokn/claims-list";
import { EvidenceSources, VerificationHistory } from "@/components/tokn/evidence-history";
import { InvestmentSnapshot } from "@/components/tokn/investment-snapshot";
import { SiteNav } from "@/components/tokn/site-nav";
import {
  fetchAsset,
  fetchAssetHistory,
  resolveApiBase,
  type ScoredAsset,
} from "@/lib/api";
import { deriveHistoryEvents } from "@/lib/asset-helpers";

const SECTIONS = [
  { id: "overview", label: "Overview" },
  { id: "verification", label: "Verification" },
  { id: "intelligence", label: "Asset Intelligence" },
  { id: "evidence", label: "Evidence & Sources" },
  { id: "history", label: "Verification History" },
] as const;

export function AssetDetailPage({ assetId }: { assetId: string }) {
  const [apiBase] = useState(() => resolveApiBase());
  const [asset, setAsset] = useState<ScoredAsset | null>(null);
  const [history, setHistory] = useState<ScoredAsset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([
      fetchAsset(assetId, apiBase),
      fetchAssetHistory(assetId, apiBase),
    ])
      .then(([detail, hist]) => {
        if (cancelled) return;
        setAsset(detail);
        setHistory(hist);
        setError(null);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [apiBase, assetId]);

  const events = useMemo(() => deriveHistoryEvents(history), [history]);

  return (
    <div className="tokn-shell">
      <SiteNav />
      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[200px_1fr]">
        <aside className="hidden lg:block">
          <div className="glass sticky top-20 space-y-4 p-4">
            <p className="eyebrow">On this page</p>
            <nav className="space-y-2 text-[11px] tracking-[0.1em] text-[var(--tokn-muted)]">
              {SECTIONS.map((s) => (
                <a
                  key={s.id}
                  href={`#${s.id}`}
                  className="block hover:text-[var(--tokn-ink)]"
                >
                  {s.label}
                </a>
              ))}
            </nav>
            {asset ? (
              <div className="border-t border-[rgba(26,28,31,0.08)] pt-3 text-[10px] leading-relaxed text-[var(--tokn-muted)]">
                <p>Snapshot {asset.data_pulled_at || "—"}</p>
                <p className="mt-1">
                  Age{" "}
                  {typeof asset.snapshot_age_days === "number"
                    ? `${asset.snapshot_age_days.toFixed(1)}d`
                    : "—"}
                </p>
              </div>
            ) : null}
          </div>
        </aside>

        <main className="min-w-0 space-y-4 pb-16">
          {loading ? (
            <div className="glass p-6 text-[12px] text-[var(--tokn-muted)]">
              Loading asset intelligence…
            </div>
          ) : null}
          {error ? (
            <div className="glass p-6 text-[12px] text-[var(--tokn-bad)]">
              {error}
            </div>
          ) : null}
          {asset ? (
            <>
              <AssetHeader asset={asset} />
              <InvestmentSnapshot asset={asset} />
              <ClaimsList asset={asset} />
              <AssetIntelligence asset={asset} />
              <EvidenceSources asset={asset} />
              <VerificationHistory events={events} />
              <p className="px-1 text-[10px] leading-relaxed text-[var(--tokn-muted)]">
                Descriptive and comparative only — not investment advice. Scores
                from scoring.engine; claims from schema claims[] when present.
              </p>
            </>
          ) : null}
        </main>
      </div>
    </div>
  );
}
