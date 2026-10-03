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
      <div className="flex items-baseline justify-between gap-2 text-[10px] tracking-[0.12em] text-[var(--tokn-muted)]">
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
        <div className="grid h-11 w-11 place-items-center rounded-full border border-[rgba(26,28,31,0.1)] bg-white/70 text-xs tracking-[0.08em]">
          {monogram(asset.name)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="truncate text-base tracking-wide">{asset.name}</h2>
            {symbol ? <span className="pill pill-muted">{symbol}</span> : null}
          </div>
          <p className="mt-1 text-[11px] tracking-[0.08em] text-[var(--tokn-muted)]">
            {categoryShort(asset.asset_class)}
          </p>
          <p className="mt-0.5 text-[10px] text-[var(--tokn-muted)]">
            {assetClassLabel(asset.asset_class)}
          </p>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-dashed border-[rgba(26,28,31,0.12)] bg-white/35 px-3 py-2 text-[11px] text-[var(--tokn-muted)]">
        <div className="flex items-center justify-between gap-2">
          <span className="tracking-[0.12em]">TOKEN PRICE</span>
          <span className="pill pill-muted">Not available</span>
        </div>
        <p className="mt-1 text-[10px]">
          No live spot ticker in the API. Market fields are omitted rather than invented.
        </p>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <MiniScore label="RISK" score={asset.risk_score} />
        <MiniScore label="YIELD" score={asset.yield_score} />
        <MiniScore label="EXIT" score={asset.liquidity_score} />
        <MiniScore label="CONFIDENCE" score={asset.data_confidence_score} />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className={`pill ${pillClass}`}>
          Verification · {verificationStateLabel(state)}
        </span>
        <span className="pill pill-muted">
          {fresh.label} · {fresh.detail}
        </span>
      </div>

      <div className="mt-5 flex items-center justify-between gap-3 border-t border-[rgba(26,28,31,0.08)] pt-4">
        <span className="text-[10px] tracking-[0.1em] text-[var(--tokn-muted)]">
          {asset.source_platform.toUpperCase()}
        </span>
        <Link
          href={`/assets/${encodeURIComponent(asset.asset_id)}/`}
          className="rounded-full border border-[rgba(26,28,31,0.14)] bg-[rgba(26,28,31,0.92)] px-3 py-1.5 text-[11px] tracking-[0.12em] text-white transition group-hover:bg-black"
        >
          VIEW ASSET →
        </Link>
      </div>
    </motion.article>
  );
}
