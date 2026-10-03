"use client";

import { useEffect, useState } from "react";
import {
  readWatchlist,
  writeWatchlist,
} from "@/lib/asset-helpers";

export function WatchlistButton({ assetId }: { assetId: string }) {
  const [on, setOn] = useState(false);

  useEffect(() => {
    setOn(readWatchlist().includes(assetId));
  }, [assetId]);

  return (
    <button
      type="button"
      onClick={() => {
        const cur = readWatchlist();
        const next = on
          ? cur.filter((id) => id !== assetId)
          : [...cur, assetId];
        writeWatchlist(next);
        setOn(!on);
      }}
      className="rounded-full border border-[rgba(26,28,31,0.14)] bg-white/55 px-3 py-1.5 text-[11px] transition hover:bg-white/80"
    >
      {on ? "★ ON WATCHLIST" : "☆ ADD TO WATCHLIST"}
    </button>
  );
}

export function FreshnessIndicator({
  label,
  detail,
  kind,
}: {
  label: string;
  detail: string;
  kind: "scored" | "snapshot" | "unavailable";
}) {
  const cls =
    kind === "scored"
      ? "pill-ok"
      : kind === "snapshot"
        ? "pill-warn"
        : "pill-muted";
  return (
    <div className="text-[10px] leading-relaxed text-[var(--tokn-muted)]">
      <span className={`pill ${cls}`}>{label}</span>
      <p className="mt-1 break-all">{detail}</p>
    </div>
  );
}
