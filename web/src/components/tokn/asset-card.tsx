"use client";

import Link from "next/link";
import { motion } from "motion/react";
import type { ScoredAsset } from "@/lib/api";
import {
  assetClassLabel,
  categoryShort,
  formatScore,
  monogram,
  overallVerificationState,
  scoreTone,
  snapshotFreshness,
  tokenSymbol,
  verificationStateLabel,
} from "@/lib/asset-helpers";
import { AssetSeriesChart } from "@/components/tokn/asset-series-chart";

function MiniScore({
  label,
  score,
}: {
  label: string;
  score: { value: number | null; insufficient_data?: boolean };
}) {
  const tone = scoreTone(score.value, score.insufficient_data);
  const pct =
    score.insufficient_data || score.value === null
      ? 0
      : Math.max(0, Math.min(100, score.value));
  return (
    <div className="min-w-0">
      <div className="flex items-baseline justify-between gap-2 text-[10px] text-[var(--tokn-muted)]">
        <span>{label}</span>
        <span className="text-[var(--tokn-ink)]">
          {score.insufficient_data ? "—" : formatScore(score.value)}
        </span>
      </div>
      <div className="score-bar mt-1" data-tone={tone}>
        <span style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function AssetCard({ asset, index = 0 }: { asset: ScoredAsset; index?: number }) {
  const symbol = tokenSymbol(asset);
  const state = overallVerificationState(asset);
  const fresh = snapshotFreshness(asset);
  const pillClass =
    state === "discrepancy"
      ? "pill-bad"
      : state === "proof"
        ? "pill-ok"
        : state === "self-reported"
          ? "pill-warn"
          : "pill-muted";

  return (
    <motion.article
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.35 }}
      className="glass group flex h-full flex-col p-5"
    >
      <div className="flex items-start gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-full border border-white/70 bg-white/55 text-xs shadow-[inset_0_1px_0_rgba(255,255,255,0.9)]">
          {monogram(asset.name)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="truncate text-base font-semibold">{asset.name}</h2>
            {symbol ? <span className="pill pill-muted">{symbol}</span> : null}
          </div>
          <p className="mt-1 text-[11px] text-[var(--tokn-muted)]">
            {categoryShort(asset.asset_class)}
          </p>
          <p className="mt-0.5 text-[10px] text-[var(--tokn-muted)]">
            {assetClassLabel(asset.asset_class)}
          </p>
        </div>
      </div>

      <div className="glass-inset mt-4">
        <AssetSeriesChart asset={asset} compact />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <MiniScore label="Risk" score={asset.risk_score} />
        <MiniScore label="Yield" score={asset.yield_score} />
        <MiniScore label="Exit" score={asset.liquidity_score} />
        <MiniScore label="Confidence" score={asset.data_confidence_score} />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className={`pill ${pillClass}`}>
          Verification · {verificationStateLabel(state)}
        </span>
        <span className="pill pill-muted">
          {fresh.label} · {fresh.detail}
        </span>
      </div>

      <div className="mt-5 flex items-center justify-between gap-3 border-t border-white/40 pt-4">
        <span className="text-[10px] text-[var(--tokn-muted)]">
          {asset.source_platform}
        </span>
        <Link
          href={`/assets/${encodeURIComponent(asset.asset_id)}/`}
          className="rounded-full border border-white/50 bg-[rgba(26,28,31,0.9)] px-3 py-1.5 text-[11px] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.18)] transition group-hover:bg-black"
        >
          View asset →
        </Link>
      </div>
    </motion.article>
  );
}
