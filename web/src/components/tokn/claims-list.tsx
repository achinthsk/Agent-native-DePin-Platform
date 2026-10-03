"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import type { AssetClaim, ScoredAsset } from "@/lib/api";
import {
  claimStatus,
  claimTitle,
  formatClaimValue,
} from "@/lib/asset-helpers";

function statusPill(status: ReturnType<typeof claimStatus>) {
  if (status === "discrepancy") return "pill-warn";
  if (status === "verified") return "pill-ok";
  return "pill-muted";
}

function statusLabel(status: ReturnType<typeof claimStatus>) {
  if (status === "discrepancy") return "Discrepancy";
  if (status === "verified") return "Verified tier";
  return "Self-reported";
}

export function ClaimsList({ asset }: { asset: ScoredAsset }) {
  const claims = useMemo(() => asset.claims || [], [asset.claims]);
  const [openId, setOpenId] = useState<string | null>(
    claims.find((c) => c.conflicts_with)?.claim ?? claims[0]?.claim ?? null,
  );
  const byId = useMemo(
    () => new Map(claims.map((c) => [c.claim, c])),
    [claims],
  );

  return (
    <section id="verification" className="glass p-5 sm:p-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="eyebrow">Verification</p>
          <h2 className="mt-1 text-xl tracking-wide">Key claims and evidence</h2>
        </div>
        <p className="text-[11px] text-[var(--tokn-muted)]">
          {claims.length} claim{claims.length === 1 ? "" : "s"} on this snapshot
        </p>
      </div>

      {claims.length === 0 ? (
        <p className="mt-4 text-[12px] text-[var(--tokn-muted)]">
          No claim-level rows yet. Asset-root verification tier still applies to
          scoring.
        </p>
      ) : (
        <div className="mt-4 space-y-2">
          {claims.map((claim) => {
            const status = claimStatus(claim, claims);
            const open = openId === claim.claim;
            const other = claim.conflicts_with
              ? byId.get(claim.conflicts_with)
              : null;
            return (
              <div key={claim.claim} className="glass-row overflow-hidden">
                <button
                  type="button"
                  onClick={() =>
                    setOpenId((id) => (id === claim.claim ? null : claim.claim))
                  }
                  className="flex w-full items-start gap-3 px-4 py-3 text-left"
                >
                  <span className="mt-0.5 text-sm" aria-hidden>
                    {status === "discrepancy"
                      ? "⚠"
                      : status === "verified"
                        ? "✓"
                        : "◌"}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-sm tracking-wide">
                        {claimTitle(claim.claim)}
                      </p>
                      <span className={`pill ${statusPill(status)}`}>
                        {statusLabel(status)}
                      </span>
                    </div>
                    <p className="mt-1 text-[11px] text-[var(--tokn-muted)]">
                      Value: {formatClaimValue(claim.value)} · {claim.fact_domain}
                    </p>
                  </div>
                  <span className="text-[10px] tracking-[0.12em] text-[var(--tokn-muted)]">
                    {open ? "HIDE" : "DETAILS →"}
                  </span>
                </button>
                <AnimatePresence>
                  {open ? (
                    <ClaimDetail claim={claim} other={other ?? null} />
                  ) : null}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function ClaimDetail({
  claim,
  other,
}: {
  claim: AssetClaim;
  other: AssetClaim | null;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      className="overflow-hidden border-t border-[rgba(26,28,31,0.08)]"
    >
      <div className="grid gap-3 bg-white/35 p-4 text-[11px] leading-relaxed sm:grid-cols-2">
        <div>
          <p className="eyebrow">This claim</p>
          <p className="mt-1 text-sm text-[var(--tokn-ink)]">
            {formatClaimValue(claim.value)}
          </p>
          <p className="mt-2 text-[var(--tokn-muted)]">
            Tier: {claim.verification_tier}
          </p>
          <p className="text-[var(--tokn-muted)]">Domain: {claim.fact_domain}</p>
          <p className="text-[var(--tokn-muted)]">
            Verified: {claim.verified_at}
          </p>
        </div>
        <div>
          <p className="eyebrow">Evidence source</p>
          <p className="mt-1 text-[var(--tokn-muted)]">{claim.evidence_source}</p>
          {other ? (
            <div className="mt-3 rounded-lg border border-[rgba(161,98,7,0.25)] bg-[rgba(161,98,7,0.08)] p-3">
              <p className="eyebrow text-[var(--tokn-warn)]">Conflicts with</p>
              <p className="mt-1 text-[var(--tokn-ink)]">
                {claimTitle(other.claim)}: {formatClaimValue(other.value)}
              </p>
              <p className="mt-1 text-[var(--tokn-muted)]">
                {other.fact_domain} · {other.verification_tier}
              </p>
            </div>
          ) : (
            <p className="mt-3 text-[var(--tokn-muted)]">
              conflicts_with: null
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
