"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import { AnimatePresence, LayoutGroup, motion } from "motion/react";
import {
  GITHUB_REPO,
  LIVE_API_FALLBACK,
  fetchAssets,
  fetchMethodologySummary,
  resolveApiBase,
  verificationTier,
  type MethodologyResponse,
  type ScoredAsset,
} from "@/lib/api";
import { AssetPanel } from "@/components/asset-panel";
import { FINDINGS } from "@/content/findings";

type SortKey =
  | "asset_id"
  | "risk_score"
  | "liquidity_score"
  | "data_confidence_score";
type TierFilter = "all" | "proof" | "unverified";

function scoreValue(asset: ScoredAsset, key: SortKey): number {
  if (key === "asset_id") return 0;
  const s = asset[key];
  if (!s || s.insufficient_data || s.value === null || s.value === undefined) {
    return -1;
  }
  return s.value;
}

function tierBucket(asset: ScoredAsset): "proof" | "unverified" | "other" {
  const t = verificationTier(asset);
  if (
    t === "cryptographic-onchain-proof" ||
    t === "independent-third-party-audit"
  ) {
    return "proof";
  }
  if (t === "self-reported-unverified") return "unverified";
  return "other";
}

function githubBlob(path: string) {
  return `${GITHUB_REPO}/blob/main/${path}`;
}

function apiUrl(base: string, path: string): string {
  if (!base) return path.startsWith("http") ? path : `${LIVE_API_FALLBACK}${path}`;
  return `${base}${path}`;
}

export default function HomePage() {
  const [apiBase] = useState(() => resolveApiBase());
  const [assets, setAssets] = useState<ScoredAsset[]>([]);
  const [notes, setNotes] = useState<string[]>([]);
  const [methodology, setMethodology] = useState<MethodologyResponse | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("asset_id");
  const [tierFilter, setTierFilter] = useState<TierFilter>("all");
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([fetchAssets(apiBase), fetchMethodologySummary(apiBase)])
      .then(([assetsRes, meth]) => {
        if (cancelled) return;
        setAssets(assetsRes.assets);
        setNotes(assetsRes.notes ?? []);
        setMethodology(meth);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  const visible = useMemo(() => {
    let rows = [...assets];
    if (tierFilter !== "all") {
      rows = rows.filter((a) => tierBucket(a) === tierFilter);
    }
    rows.sort((a, b) => {
      if (sortKey === "asset_id") return a.asset_id.localeCompare(b.asset_id);
      const diff = scoreValue(b, sortKey) - scoreValue(a, sortKey);
      if (diff !== 0) return diff;
      return a.asset_id.localeCompare(b.asset_id);
    });
    return rows;
  }, [assets, sortKey, tierFilter]);

  const fourScores =
    methodology?.content &&
    typeof methodology.content === "object" &&
    methodology.content !== null &&
    "four_scores" in methodology.content
      ? (methodology.content as {
          four_scores: Array<{
            name: string;
            direction: string;
            summary: string;
          }>;
          null_handling?: string;
          no_master_score?: string;
        })
      : null;

  const displayBase = apiBase || LIVE_API_FALLBACK;

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[960px] px-4 pb-20 pt-10 sm:px-6 sm:pt-14">
        <header className="border-b border-[var(--rule)] pb-10">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
            Agent-native DePIN Platform
          </p>
          <h1 className="mt-3 font-serif text-4xl leading-[1.1] tracking-tight text-[var(--ink)] sm:text-5xl">
            Scored Assets
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-[var(--ink)] sm:text-lg">
            Agent-native verification and four-axis scoring for tokenized
            DePIN and RWA assets — read-only view of the live public API.
          </p>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--muted)]">
            Descriptive and comparative only. Not investment advice. Scores
            are never blended into a single ranking number.
          </p>
          <div className="mt-6 flex flex-wrap gap-x-5 gap-y-2 font-mono text-[11px] text-[var(--muted)]">
            <a
              className="text-[var(--oxide)] underline-offset-4 hover:underline"
              href={displayBase}
              target="_blank"
              rel="noopener noreferrer"
            >
              {displayBase.replace(/^https?:\/\//, "")}
            </a>
            <a
              className="underline-offset-4 hover:underline"
              href={apiUrl(apiBase, "/v1/assets")}
              target="_blank"
              rel="noopener noreferrer"
            >
              /v1/assets
            </a>
            <a
              className="underline-offset-4 hover:underline"
              href={apiUrl(apiBase, "/docs")}
              target="_blank"
              rel="noopener noreferrer"
            >
              OpenAPI
            </a>
            <a
              className="underline-offset-4 hover:underline"
              href={apiUrl(apiBase, "/mcp")}
              target="_blank"
              rel="noopener noreferrer"
            >
              MCP
            </a>
            <a
              className="underline-offset-4 hover:underline"
              href={GITHUB_REPO}
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </header>

        <section
          className="border-b border-[var(--rule)] py-12"
          aria-labelledby="assets-heading"
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2
                id="assets-heading"
                className="font-serif text-2xl tracking-tight text-[var(--ink)]"
              >
                Live assets
              </h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Every scored asset from{" "}
                <span className="font-mono">GET /v1/assets</span>
                {loading ? "" : ` · ${assets.length} matched`}.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <label className="sr-only" htmlFor="tier-filter">
                Verification tier filter
              </label>
              <select
                id="tier-filter"
                value={tierFilter}
                onChange={(e) =>
                  startTransition(() =>
                    setTierFilter(e.target.value as TierFilter),
                  )
                }
                className="border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 font-mono text-[11px] text-[var(--ink)] outline-none focus:border-[var(--oxide)]"
              >
                <option value="all">All tiers</option>
                <option value="proof">On-chain / audited proof</option>
                <option value="unverified">Self-reported unverified</option>
              </select>
              <label className="sr-only" htmlFor="sort-key">
                Sort assets
              </label>
              <select
                id="sort-key"
                value={sortKey}
                onChange={(e) =>
                  startTransition(() => setSortKey(e.target.value as SortKey))
                }
                className="border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 font-mono text-[11px] text-[var(--ink)] outline-none focus:border-[var(--oxide)]"
              >
                <option value="asset_id">Sort: asset id</option>
                <option value="risk_score">Sort: risk quality ↓</option>
                <option value="liquidity_score">Sort: liquidity ↓</option>
                <option value="data_confidence_score">
                  Sort: data confidence ↓
                </option>
              </select>
            </div>
          </div>

          {error ? (
            <p className="mt-8 border border-[var(--oxide)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--oxide)]">
              Could not load live API: {error}
            </p>
          ) : null}

          {loading ? (
            <p className="mt-8 font-mono text-xs text-[var(--muted)]">
              Fetching /v1/assets…
            </p>
          ) : (
            <LayoutGroup>
              <motion.div
                layout
                className={`mt-8 space-y-5 ${isPending ? "opacity-80" : ""}`}
              >
                <AnimatePresence mode="popLayout">
                  {visible.map((asset) => (
                    <motion.div
                      key={asset.asset_id}
                      layout
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -6 }}
                      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
                    >
                      <AssetPanel asset={asset} apiBase={apiBase} />
                    </motion.div>
                  ))}
                </AnimatePresence>
                {visible.length === 0 ? (
                  <p className="text-sm text-[var(--muted)]">
                    No assets match this filter.
                  </p>
                ) : null}
              </motion.div>
            </LayoutGroup>
          )}

          {notes.length > 0 ? (
            <ul className="mt-6 space-y-1 border-t border-[var(--rule)] pt-4 font-mono text-[10px] text-[var(--muted)]">
              {notes.map((n) => (
                <li key={n}>{n}</li>
              ))}
            </ul>
          ) : null}
        </section>

        <section
          className="border-b border-[var(--rule)] py-12"
          aria-labelledby="findings-heading"
        >
          <h2
            id="findings-heading"
            className="font-serif text-2xl tracking-tight text-[var(--ink)]"
          >
            Recent findings
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-[var(--muted)]">
            Investigation log excerpts from the repository — classification
            and structural facts, not live scores. Scores above come only
            from the API.
          </p>
          <ol className="mt-8 space-y-0 divide-y divide-[var(--rule)] border-y border-[var(--rule)]">
            {FINDINGS.map((f) => (
              <li key={f.id} className="py-6">
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  <time
                    dateTime={f.date}
                    className="font-mono text-[11px] text-[var(--muted)]"
                  >
                    {f.date}
                  </time>
                  <span className="border border-[var(--rule)] px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-[var(--ink)]">
                    {f.classification}
                  </span>
                </div>
                <h3 className="mt-2 font-serif text-xl text-[var(--ink)]">
                  {f.title}
                </h3>
                <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--ink)]">
                  {f.summary}
                </p>
                <a
                  className="mt-3 inline-block font-mono text-[11px] text-[var(--oxide)] underline-offset-4 hover:underline"
                  href={
                    f.id === "spacecoin-wrong-model"
                      ? `${GITHUB_REPO}/blob/cursor/scheduler-refresh-discovery-c7dd/${f.source_path}`
                      : githubBlob(f.source_path)
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {f.source_label} →
                </a>
              </li>
            ))}
          </ol>
        </section>

        <section className="py-12" aria-labelledby="methodology-heading">
          <h2
            id="methodology-heading"
            className="font-serif text-2xl tracking-tight text-[var(--ink)]"
          >
            Methodology
          </h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Pulled from{" "}
            <span className="font-mono">
              GET /v1/methodology?format=summary
            </span>
            — not rewritten here.
          </p>

          {!methodology && !error ? (
            <p className="mt-6 font-mono text-xs text-[var(--muted)]">
              Fetching methodology…
            </p>
          ) : null}

          {fourScores ? (
            <div className="mt-8 space-y-6">
              <ul className="space-y-4">
                {fourScores.four_scores.map((s) => (
                  <li
                    key={s.name}
                    className="border-l-2 border-[var(--oxide)] pl-4"
                  >
                    <div className="font-mono text-[12px] text-[var(--ink)]">
                      {s.name}
                    </div>
                    <div className="mt-0.5 font-mono text-[10px] uppercase tracking-wider text-[var(--muted)]">
                      {s.direction.replace(/_/g, " ")}
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-[var(--ink)]">
                      {s.summary}
                    </p>
                  </li>
                ))}
              </ul>
              {fourScores.null_handling ? (
                <p className="text-sm leading-relaxed text-[var(--muted)]">
                  {fourScores.null_handling}
                </p>
              ) : null}
              {fourScores.no_master_score ? (
                <p className="text-sm leading-relaxed text-[var(--muted)]">
                  {fourScores.no_master_score}
                </p>
              ) : null}
              {methodology?.notes?.map((n) => (
                <p
                  key={n}
                  className="font-mono text-[10px] text-[var(--muted)]"
                >
                  {n}
                </p>
              ))}
              <div className="flex flex-wrap gap-4 font-mono text-[11px]">
                <a
                  className="text-[var(--oxide)] underline-offset-4 hover:underline"
                  href={apiUrl(apiBase, "/v1/methodology?format=markdown")}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Full methodology (markdown) →
                </a>
                {methodology?.methodology_path ? (
                  <a
                    className="underline-offset-4 hover:underline"
                    href={githubBlob(methodology.methodology_path)}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {methodology.methodology_path}
                  </a>
                ) : null}
              </div>
            </div>
          ) : null}
        </section>

        <footer className="border-t border-[var(--rule)] pt-8 font-mono text-[11px] text-[var(--muted)]">
          <p>
            Source of truth:{" "}
            <a
              className="text-[var(--oxide)] underline-offset-4 hover:underline"
              href={apiUrl(apiBase, "/v1/assets")}
              target="_blank"
              rel="noopener noreferrer"
            >
              live API
            </a>
            . If this page and the API disagree, that is a bug.
          </p>
          <p className="mt-2">
            <a
              className="underline-offset-4 hover:underline"
              href={GITHUB_REPO}
              target="_blank"
              rel="noopener noreferrer"
            >
              {GITHUB_REPO.replace(/^https?:\/\//, "")}
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
}
