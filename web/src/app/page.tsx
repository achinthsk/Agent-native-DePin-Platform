"use client";

import { useEffect, useMemo, useState } from "react";
import { AssetCard } from "@/components/tokn/asset-card";
import { SiteNav } from "@/components/tokn/site-nav";
import {
  fetchAssets,
  GITHUB_REPO,
  LIVE_API_FALLBACK,
  resolveApiBase,
  type ScoredAsset,
} from "@/lib/api";
import { readWatchlist } from "@/lib/asset-helpers";

export default function HomePage() {
  const [apiBase] = useState(() => resolveApiBase());
  const [assets, setAssets] = useState<ScoredAsset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [watch, setWatch] = useState<string[]>([]);

  useEffect(() => {
    setWatch(readWatchlist());
    const onStorage = () => setWatch(readWatchlist());
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchAssets(apiBase)
      .then((res) => {
        if (cancelled) return;
        setAssets(res.assets);
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
  }, [apiBase]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return assets;
    return assets.filter((a) => {
      const blob = [
        a.name,
        a.asset_id,
        a.asset_class,
        a.source_platform,
        a.description_text || "",
      ]
        .join(" ")
        .toLowerCase();
      return blob.includes(q);
    });
  }, [assets, search]);

  const watched = filtered.filter((a) => watch.includes(a.asset_id));
  const displayBase = apiBase || LIVE_API_FALLBACK;

  return (
    <div className="tokn-shell">
      <SiteNav search={search} onSearch={setSearch} />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <section className="glass p-6 sm:p-8">
          <p className="eyebrow">Tokn Investments</p>
          <h1 className="mt-3 max-w-3xl text-3xl leading-tight tracking-wide sm:text-5xl">
            Investment intelligence for tokenized infrastructure.
          </h1>
          <p className="mt-4 max-w-2xl text-[13px] leading-relaxed text-[var(--tokn-muted)]">
            Discover assets, evaluate the four-axis snapshot, verify claims
            against evidence, and investigate conflicts — without treating
            marketing copy as proof.
          </p>
          <div className="mt-5 flex flex-wrap gap-2 text-[10px]">
            <a
              href={displayBase}
              target="_blank"
              rel="noopener noreferrer"
              className="pill pill-muted"
            >
              API {displayBase.replace(/^https?:\/\//, "")}
            </a>
            <a
              href={GITHUB_REPO}
              target="_blank"
              rel="noopener noreferrer"
              className="pill pill-muted"
            >
              GitHub
            </a>
            <span className="pill pill-muted">
              Descriptive only — not investment advice
            </span>
          </div>
        </section>

        <section id="research" className="mt-8">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="eyebrow">Assets</p>
              <h2 className="mt-1 text-xl tracking-wide">Browse</h2>
            </div>
            <p className="text-[11px] text-[var(--tokn-muted)]">
              {loading
                ? "Loading…"
                : `${filtered.length} of ${assets.length} shown`}
            </p>
          </div>

          {error ? (
            <div className="glass p-5 text-[12px] text-[var(--tokn-bad)]">
              Failed to load assets: {error}
            </div>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map((asset, i) => (
              <AssetCard key={asset.asset_id} asset={asset} index={i} />
            ))}
          </div>
          {!loading && !error && filtered.length === 0 ? (
            <p className="mt-4 text-[12px] text-[var(--tokn-muted)]">
              No assets match this search.
            </p>
          ) : null}
        </section>

        <section id="watchlist" className="mt-10">
          <p className="eyebrow">Watchlist</p>
          <h2 className="mt-1 text-xl tracking-wide">Saved locally</h2>
          <p className="mt-2 text-[11px] text-[var(--tokn-muted)]">
            Stored in this browser only — not synced to a server.
          </p>
          {watched.length === 0 ? (
            <p className="mt-4 text-[12px] text-[var(--tokn-muted)]">
              No watched assets yet.
            </p>
          ) : (
            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {watched.map((asset, i) => (
                <AssetCard key={asset.asset_id} asset={asset} index={i} />
              ))}
            </div>
          )}
        </section>

        <section id="about" className="glass mt-10 p-6">
          <p className="eyebrow">About</p>
          <h2 className="mt-1 text-xl tracking-wide">What Tokn shows</h2>
          <p className="mt-3 max-w-3xl text-[12px] leading-relaxed text-[var(--tokn-muted)]">
            Tokn Investments is a read-only front end over the Agent-native DePIN
            scored-assets API. Scores come from scoring.engine; claims come from
            schema claims[] when present. Spot market fields that the API does
            not provide are labeled Not available.
          </p>
        </section>
      </main>
    </div>
  );
}
