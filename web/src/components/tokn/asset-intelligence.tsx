"use client";

import type { ReactNode } from "react";
import type { ScoredAsset } from "@/lib/api";
import {
  emissionRegistryPrice,
  realizedYieldPct,
  verificationTier,
} from "@/lib/api";
import { assetClassLabel } from "@/lib/asset-helpers";

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-[rgba(26,28,31,0.06)] py-2 text-[11px] last:border-b-0">
      <span className="text-[var(--tokn-muted)]">{label}</span>
      <span className="max-w-[60%] text-right text-[var(--tokn-ink)]">
        {value ?? "Not available"}
      </span>
    </div>
  );
}

function na(v: unknown): string {
  if (v === null || v === undefined || v === "") return "Not available";
  return String(v);
}

export function AssetIntelligence({ asset }: { asset: ScoredAsset }) {
  const exposure = asset.exposure || {};
  const maturity = asset.maturity || {};
  const payout = asset.payout_mechanism || {};
  const liq = asset.liquidity || {};
  const yieldPct = realizedYieldPct(asset);
  const registry = emissionRegistryPrice(asset);

  return (
    <section id="intelligence" className="glass p-5 sm:p-6">
      <p className="eyebrow">Asset intelligence</p>
      <h2 className="mt-1 text-xl tracking-wide">Fundamentals & economics</h2>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="glass-row p-4">
          <p className="eyebrow">Asset fundamentals</p>
          <div className="mt-2">
            <Row label="Asset type" value={assetClassLabel(asset.asset_class)} />
            <Row label="Platform" value={asset.source_platform} />
            <Row
              label="Underlying"
              value={na(exposure.underlying_reference)}
            />
            <Row label="Operator" value={na(exposure.operator_name)} />
            <Row label="Exposure" value={na(exposure.exposure_type)} />
            <Row
              label="Protocol age (months)"
              value={na(maturity.protocol_age_months)}
            />
            <Row
              label="Asset age (months)"
              value={na(maturity.asset_age_months)}
            />
            <Row
              label="Completed payout cycles"
              value={na(maturity.completed_payout_cycles)}
            />
            <Row
              label="Payout mechanism"
              value={na(payout.payout_mechanism_type)}
            />
            <Row label="Payout currency" value={na(payout.payout_currency)} />
            <Row label="Payout frequency" value={na(payout.payout_frequency)} />
            <Row
              label="Root verification tier"
              value={verificationTier(asset) || "Not available"}
            />
            <Row label="Retrieval method" value={na(asset.retrieval_method)} />
          </div>
        </div>

        <div className="glass-row p-4">
          <p className="eyebrow">Market / economics</p>
          <div className="mt-2">
            <Row
              label="Live spot price"
              value={<span className="pill pill-muted">Not available</span>}
            />
            <Row
              label="24h change"
              value={<span className="pill pill-muted">Not available</span>}
            />
            <Row label="Market cap" value="Not available" />
            <Row label="Volume / FDV / supply" value="Not available" />
            <Row
              label="Realized yield %"
              value={
                yieldPct === null ? (
                  "Not available"
                ) : (
                  <span>
                    {yieldPct}%{" "}
                    <span className="pill pill-muted ml-1">Snapshot</span>
                  </span>
                )
              }
            />
            <Row
              label="Exit type"
              value={na(liq.exit_type)}
            />
            <Row
              label="Lockup (weeks)"
              value={na(liq.lockup_period_weeks)}
            />
            <Row
              label="Exit-conditions score"
              value={
                asset.liquidity_score.insufficient_data
                  ? "Insufficient data"
                  : `${asset.liquidity_score.value ?? "—"} / 100 (not market depth)`
              }
            />
            {registry ? (
              <Row
                label="Emission token price (registry)"
                value={
                  <span>
                    {registry.current.toFixed(4)} USDG/GLW{" "}
                    <span className="pill pill-muted ml-1">
                      Snapshot{registry.asOf ? ` · ${registry.asOf}` : ""}
                    </span>
                  </span>
                }
              />
            ) : null}
          </div>
          <p className="mt-3 text-[10px] leading-relaxed text-[var(--tokn-muted)]">
            Location, capacity, token standard, network, and exchange market data
            are not fields on the current asset schema/API — shown as Not
            available rather than guessed.
          </p>
        </div>
      </div>
    </section>
  );
}
