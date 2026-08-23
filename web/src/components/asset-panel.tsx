"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  fetchAssetHistory,
  peakDeclinePct,
  verificationTier,
  type ScoredAsset,
} from "@/lib/api";
import { ScoreStrip } from "@/components/score-strip";
import { VerificationBadge } from "@/components/verification-badge";
import { HistoryChart } from "@/components/history-chart";

export function AssetPanel({
  asset,
  apiBase,
}: {
  asset: ScoredAsset;
  apiBase: string;
}) {
  const [history, setHistory] = useState<ScoredAsset[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const tier = verificationTier(asset);
  const peak = peakDeclinePct(asset);

  useEffect(() => {
    let cancelled = false;
    setHistory(null);
    setError(null);
    fetchAssetHistory(asset.asset_id, apiBase)
      .then((rows) => {
        if (!cancelled) setHistory(rows);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [asset.asset_id, apiBase]);

  return (
    <motion.article
      layout
      className="border border-[var(--rule)] bg-[var(--panel)]"
    >
      <header className="flex flex-col gap-3 border-b border-[var(--rule)] px-4 py-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h3 className="font-serif text-xl leading-snug text-[var(--ink)]">
            {asset.name}
          </h3>
          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11px] text-[var(--muted)]">
            <span>{asset.asset_id}</span>
            <span aria-hidden>·</span>
            <span>{asset.asset_class}</span>
            <span aria-hidden>·</span>
            <span>{asset.source_platform}</span>
          </div>
        </div>
        <VerificationBadge tier={tier} />
      </header>

      <ScoreStrip
        scores={{
          yield_score: asset.yield_score,
          risk_score: asset.risk_score,
          liquidity_score: asset.liquidity_score,
          data_confidence_score: asset.data_confidence_score,
        }}
      />

      <div className="space-y-3 px-4 py-4">
        {peak !== null ? (
          <p className="text-sm leading-relaxed text-[var(--ink)]">
            Emission-token peak decline from live{" "}
            <span className="font-mono">risk_score</span> inputs:{" "}
            <span className="font-mono">−{peak.toFixed(1)}%</span> from peak.
            Risk-quality axis remains higher-is-better; this input lowers that
            score.
          </p>
        ) : null}

        <AnimatePresence mode="wait">
          {error ? (
            <motion.p
              key="err"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-[var(--oxide)]"
            >
              History fetch failed: {error}
            </motion.p>
          ) : history === null ? (
            <motion.p
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-mono text-xs text-[var(--muted)]"
            >
              Loading snapshot history…
            </motion.p>
          ) : (
            <motion.div
              key="chart"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.25 }}
            >
              <HistoryChart history={history} />
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10px] text-[var(--muted)]">
          {asset.data_pulled_at ? (
            <span>data_pulled_at {asset.data_pulled_at}</span>
          ) : null}
          {asset.scored_at ? <span>scored_at {asset.scored_at}</span> : null}
          {asset.weights_version ? (
            <span>weights {asset.weights_version}</span>
          ) : null}
        </div>
      </div>
    </motion.article>
  );
}
