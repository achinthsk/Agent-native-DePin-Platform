"use client";

import type { ScoredAsset } from "@/lib/api";
import type { HistoryEvent } from "@/lib/asset-helpers";

export function EvidenceSources({ asset }: { asset: ScoredAsset }) {
  const sources: { label: string; value: string }[] = [];
  if (asset.source_url) {
    sources.push({ label: "Project / pull source", value: asset.source_url });
  }
  for (const c of asset.claims || []) {
    sources.push({
      label: `Claim · ${c.claim}`,
      value: c.evidence_source,
    });
  }
  if (asset.verification?.verification_notes) {
    sources.push({
      label: "Verification notes",
      value: asset.verification.verification_notes,
    });
  }

  return (
    <section id="evidence" className="glass p-5 sm:p-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="eyebrow">Evidence & sources</p>
          <h2 className="mt-1 text-xl">Where claims came from</h2>
        </div>
      </div>
      {sources.length === 0 ? (
        <p className="mt-4 text-[12px] text-[var(--tokn-muted)]">
          No source strings on this snapshot.
        </p>
      ) : (
        <ul className="mt-4 space-y-2">
          {sources.map((s, i) => (
            <li key={`${s.label}-${i}`} className="glass-row px-4 py-3 text-[11px]">
              <p className="eyebrow">{s.label}</p>
              <p className="mt-1 break-words leading-relaxed text-[var(--tokn-muted)]">
                {s.value.startsWith("http") ? (
                  <a
                    href={s.value}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline-offset-2 hover:underline"
                  >
                    {s.value}
                  </a>
                ) : (
                  s.value
                )}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function VerificationHistory({ events }: { events: HistoryEvent[] }) {
  return (
    <section id="history" className="glass p-5 sm:p-6">
      <p className="eyebrow">Verification history</p>
      <h2 className="mt-1 text-xl">Meaningful snapshot changes</h2>
      {events.length === 0 ? (
        <p className="mt-4 text-[12px] text-[var(--tokn-muted)]">
          No historical snapshots available to derive events from.
        </p>
      ) : (
        <ol className="mt-4 space-y-3">
          {events.map((e, i) => (
            <li key={`${e.at}-${i}`} className="glass-row px-4 py-3">
              <p className="text-[10px] text-[var(--tokn-muted)]">
                {e.at}
              </p>
              <p className="mt-1 text-sm">{e.title}</p>
              <p className="mt-1 text-[11px] leading-relaxed text-[var(--tokn-muted)]">
                {e.detail}
              </p>
            </li>
          ))}
        </ol>
      )}
      <p className="mt-3 text-[10px] text-[var(--tokn-muted)]">
        Events are derived only from stored snapshot history — not fabricated
        activity.
      </p>
    </section>
  );
}
