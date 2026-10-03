"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import type { ScoredAsset } from "@/lib/api";
import {
  conflictingClaimPairs,
  formatClaimValue,
  formatScore,
  claimTitle,
  scoreTone,
  snapshotHeadline,
} from "@/lib/asset-helpers";

function Dimension({
  label,
  hint,
  score,
}: {
  label: string;
  hint: string;
  score: { value: number | null; insufficient_data?: boolean };
}) {
  const tone = scoreTone(score.value, score.insufficient_data);
  const pct =
    score.insufficient_data || score.value === null
      ? 0
      : Math.max(0, Math.min(100, score.value));
  const status =
    score.insufficient_data || score.value === null
      ? "Insufficient data"
      : tone === "high"
        ? "Higher"
        : tone === "mid"
          ? "Moderate"
          : "Lower";
  return (
    <div className="glass-row p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="eyebrow">{label}</p>
          <p className="mt-1 text-xl">
            {score.insufficient_data ? "—" : formatScore(score.value)}
            <span className="text-xs text-[var(--tokn-muted)]"> / 100</span>
          </p>
        </div>
        <span
          className={`pill ${
            tone === "high"
              ? "pill-ok"
              : tone === "mid"
                ? "pill-warn"
                : tone === "low"
                  ? "pill-bad"
                  : "pill-muted"
          }`}
        >
          {status}
        </span>
      </div>
      <p className="mt-2 text-[11px] leading-relaxed text-[var(--tokn-muted)]">
        {hint}
      </p>
      <div className="score-bar mt-3" data-tone={tone}>
        <span style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function InvestmentSnapshot({ asset }: { asset: ScoredAsset }) {
  const [open, setOpen] = useState(false);
  const headline = snapshotHeadline(asset);
  const pairs = conflictingClaimPairs(asset.claims || []);
  const top = pairs[0];

  return (
    <section id="overview" className="grid gap-4 lg:grid-cols-[1.35fr_0.95fr]">
      <div className="glass p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="eyebrow">Investment snapshot</p>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="text-[11px] text-[var(--tokn-muted)] underline-offset-4 hover:text-[var(--tokn-ink)] hover:underline"
          >
            How this snapshot works →
          </button>
        </div>
        <h2 className="mt-3 max-w-xl text-2xl font-semibold leading-tight sm:text-3xl">
          {headline.primary}
          <span className="mt-1 block text-[var(--tokn-warn)]">
            {headline.secondary}
          </span>
        </h2>
        <p className="mt-3 max-w-2xl text-[12px] leading-relaxed text-[var(--tokn-muted)]">
          {headline.body}
        </p>

        <AnimatePresence>
          {open ? (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="glass-row mt-4 space-y-2 p-4 text-[11px] leading-relaxed text-[var(--tokn-muted)]">
                <p>
                  <strong className="text-[var(--tokn-ink)]">Risk</strong> —
                  risk quality (safer ↑) from verification tier, ages, exposure,
                  payout mechanism, and emission drawdown when present.
                </p>
                <p>
                  <strong className="text-[var(--tokn-ink)]">Yield</strong> —
                  maps advertised/realized yield; both null → insufficient_data.
                </p>
                <p>
                  <strong className="text-[var(--tokn-ink)]">Exit conditions</strong>{" "}
                  — contractual exit type / lockup / time-to-exit (not market
                  depth).
                </p>
                <p>
                  <strong className="text-[var(--tokn-ink)]">Data confidence</strong>{" "}
                  — verification tier, retrieval method, completeness, freshness.
                </p>
                <p>
                  Scores are never blended into one master number. Descriptive /
                  comparative only — not investment advice. Weights version:{" "}
                  {asset.weights_version || "—"}.
                </p>
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          <Dimension
            label="Risk quality"
            hint="Higher means structurally safer on this axis."
            score={asset.risk_score}
          />
          <Dimension
            label="Yield"
            hint="Higher is better when yield inputs exist."
            score={asset.yield_score}
          />
          <Dimension
            label="Exit conditions"
            hint="Transferability / lockup structure — not order-book liquidity."
            score={asset.liquidity_score}
          />
          <Dimension
            label="Data confidence"
            hint="How complete and checkable the observed fields are."
            score={asset.data_confidence_score}
          />
        </div>
      </div>

      <div className="glass flex flex-col p-5 sm:p-6">
        <p className="eyebrow">Key verification finding</p>
        {top ? (
          <>
            <div className="mt-3 rounded-xl border border-[rgba(180,35,24,0.28)] bg-[rgba(180,35,24,0.08)] p-4">
              <p className="text-[11px] font-semibold text-[var(--tokn-bad)]">
                Conflicting claims
              </p>
              <h3 className="mt-2 text-lg">
                {claimTitle(top.a.claim).replace(/ \(.*/, "")}
              </h3>
              <p className="mt-2 text-[11px] text-[var(--tokn-muted)]">
                Tokn surfaces both sides. It does not silently pick one.
              </p>
            </div>
            <div className="mt-4 space-y-3">
              <div className="glass-row p-3">
                <p className="eyebrow">
                  {top.a.fact_domain} · {top.a.verification_tier}
                </p>
                <p className="mt-1 text-sm">{formatClaimValue(top.a.value)}</p>
                <p className="mt-2 text-[10px] leading-relaxed text-[var(--tokn-muted)]">
                  {top.a.evidence_source}
                </p>
              </div>
              <div className="glass-row p-3">
                <p className="eyebrow">
                  {top.b.fact_domain} · {top.b.verification_tier}
                </p>
                <p className="mt-1 text-sm">{formatClaimValue(top.b.value)}</p>
                <p className="mt-2 text-[10px] leading-relaxed text-[var(--tokn-muted)]">
                  {top.b.evidence_source}
                </p>
              </div>
            </div>
            <a
              href="#verification"
              className="mt-auto pt-4 text-[11px] text-[var(--tokn-muted)] hover:text-[var(--tokn-ink)]"
            >
              View evidence →
            </a>
          </>
        ) : (
          <div className="mt-4 flex flex-1 flex-col justify-center rounded-xl border border-dashed border-[rgba(26,28,31,0.12)] p-4 text-[12px] leading-relaxed text-[var(--tokn-muted)]">
            <p className="text-[var(--tokn-ink)]">No conflicting claims on this snapshot.</p>
            <p className="mt-2">
              {(asset.claims || []).length === 0
                ? "No claim-level rows yet for this asset."
                : "Claim rows are present without conflicts_with links."}
            </p>
            <a
              href="#verification"
              className="mt-4 text-[11px] hover:text-[var(--tokn-ink)]"
            >
              View claims →
            </a>
          </div>
        )}
      </div>
    </section>
  );
}
