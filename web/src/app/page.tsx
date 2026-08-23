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
  if (!base) {
    return path.startsWith("http") ? path : `${LIVE_API_FALLBACK}${path}`;
  }
  return `${base}${path}`;
}

const selectClass =
  "h-9 rounded-lg border border-[var(--border)] bg-white px-3 font-mono text-[11px] text-[var(--foreground)] outline-none transition focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200";

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
    <div className="relative min-h-screen overflow-x-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_#ffffff_0%,_#f4f4f5_55%,_#fafafa_100%)]"
      />

      <div className="mx-auto max-w-5xl px-4 pb-24 pt-10 sm:px-6 sm:pt-14">
        <motion.header
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="pb-10"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-white/80 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.16em] text-[var(--muted)] shadow-sm backdrop-blur">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Live API · read-only
          </div>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight text-[var(--foreground)] sm:text-5xl">
            Scored Assets
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-relaxed text-zinc-600 sm:text-[17px]">
            Agent-native verification and four-axis scoring for tokenized DePIN
            and RWA assets — same numbers as the public API.
          </p>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--muted)]">
            Descriptive and comparative only. Not investment advice. Scores are
            never blended into a single ranking number.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            <a
              href={displayBase}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-zinc-900 px-3 py-1.5 font-mono text-[11px] text-white transition hover:bg-zinc-800"
            >
              {displayBase.replace(/^https?:\/\//, "")}
            </a>
            <a
              href={apiUrl(apiBase, "/v1/assets")}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-1.5 font-mono text-[11px] text-zinc-700 transition hover:border-zinc-400"
            >
              /v1/assets
            </a>
            <a
              href={apiUrl(apiBase, "/docs")}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-1.5 font-mono text-[11px] text-zinc-700 transition hover:border-zinc-400"
            >
              OpenAPI
            </a>
            <a
              href={apiUrl(apiBase, "/mcp")}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-1.5 font-mono text-[11px] text-zinc-700 transition hover:border-zinc-400"
            >
              MCP
            </a>
            <a
              href={GITHUB_REPO}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-1.5 font-mono text-[11px] text-zinc-700 transition hover:border-zinc-400"
            >
              GitHub
            </a>
          </div>
        </motion.header>

        <section aria-labelledby="assets-heading" className="py-4">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2
                id="assets-heading"
                className="text-2xl font-semibold tracking-tight"
              >
                Live assets
              </h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Every scored asset from{" "}
                <span className="font-mono text-[12px]">GET /v1/assets</span>
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
                className={selectClass}
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
                className={selectClass}
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
            <p className="surface-card mb-6 px-4 py-3 text-sm text-[var(--danger)]">
              Could not load live API: {error}
            </p>
          ) : null}

          {loading ? (
            <p className="font-mono text-xs text-[var(--muted)]">
              Fetching /v1/assets…
            </p>
          ) : (
            <LayoutGroup>
              <motion.div
                layout
                className={`space-y-4 ${isPending ? "opacity-80" : ""}`}
              >
                <AnimatePresence mode="popLayout">
                  {visible.map((asset) => (
                    <motion.div
                      key={asset.asset_id}
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -6 }}
                      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
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
            <ul className="mt-6 space-y-1 font-mono text-[10px] text-[var(--muted)]">
              {notes.map((n) => (
                <li key={n}>{n}</li>
              ))}
            </ul>
          ) : null}
        </section>

        <section aria-labelledby="findings-heading" className="py-12">
          <h2
            id="findings-heading"
            className="text-2xl font-semibold tracking-tight"
          >
            Recent findings
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-[var(--muted)]">
            Investigation log excerpts from the repository — classification and
            structural facts, not live scores.
          </p>
          <ol className="mt-6 space-y-3">
            {FINDINGS.map((f, i) => (
              <motion.li
                key={f.id}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ delay: i * 0.05 }}
                className="surface-card px-4 py-5"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <time
                    dateTime={f.date}
                    className="font-mono text-[11px] text-[var(--muted)]"
                  >
                    {f.date}
                  </time>
                  <span className="rounded-full border border-[var(--border)] bg-zinc-50 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-zinc-700">
                    {f.classification}
                  </span>
                </div>
                <h3 className="mt-2 text-lg font-semibold tracking-tight">
                  {f.title}
                </h3>
                <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600">
                  {f.summary}
                </p>
                <a
                  className="mt-3 inline-flex font-mono text-[11px] text-zinc-900 underline-offset-4 hover:underline"
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
              </motion.li>
            ))}
          </ol>
        </section>

        <section aria-labelledby="methodology-heading" className="py-4">
          <h2
            id="methodology-heading"
            className="text-2xl font-semibold tracking-tight"
          >
            Methodology
          </h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Pulled from{" "}
            <span className="font-mono text-[12px]">
              GET /v1/methodology?format=summary
            </span>{" "}
            — not rewritten here.
          </p>

          {!methodology && !error ? (
            <p className="mt-6 font-mono text-xs text-[var(--muted)]">
              Fetching methodology…
            </p>
          ) : null}

          {fourScores ? (
            <div className="mt-6 space-y-4">
              <ul className="grid gap-3 sm:grid-cols-2">
                {fourScores.four_scores.map((s) => (
                  <li key={s.name} className="surface-card px-4 py-4">
                    <div className="font-mono text-[12px] font-medium">
                      {s.name}
                    </div>
                    <div className="mt-1 font-mono text-[10px] uppercase tracking-wider text-[var(--muted)]">
                      {s.direction.replace(/_/g, " ")}
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-zinc-600">
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
                <p key={n} className="font-mono text-[10px] text-[var(--muted)]">
                  {n}
                </p>
              ))}
              <div className="flex flex-wrap gap-3 font-mono text-[11px]">
                <a
                  className="rounded-lg bg-zinc-900 px-3 py-1.5 text-white hover:bg-zinc-800"
                  href={apiUrl(apiBase, "/v1/methodology?format=markdown")}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Full methodology →
                </a>
                {methodology?.methodology_path ? (
                  <a
                    className="rounded-lg border border-[var(--border)] bg-white px-3 py-1.5 hover:border-zinc-400"
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

        <footer className="mt-12 border-t border-[var(--border)] pt-8 font-mono text-[11px] text-[var(--muted)]">
          <p>
            Source of truth:{" "}
            <a
              className="text-[var(--foreground)] underline-offset-4 hover:underline"
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
