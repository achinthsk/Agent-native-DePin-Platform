import { cn } from "@/lib/utils";

const TIER_META: Record<
  string,
  { label: string; tone: "proof" | "unverified" | "neutral" }
> = {
  "cryptographic-onchain-proof": {
    label: "On-chain proof",
    tone: "proof",
  },
  "independent-third-party-audit": {
    label: "Third-party audit",
    tone: "proof",
  },
  "self-reported-unverified": {
    label: "Self-reported",
    tone: "unverified",
  },
};

export function VerificationBadge({ tier }: { tier: string | null }) {
  if (!tier) {
    return (
      <span className="inline-flex items-center rounded-full border border-[var(--border)] px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-[var(--muted)]">
        Tier unknown
      </span>
    );
  }
  const meta = TIER_META[tier] ?? {
    label: tier.replace(/-/g, " "),
    tone: "neutral" as const,
  };
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[10px] font-medium uppercase tracking-wider",
        meta.tone === "proof" &&
          "border-emerald-200 bg-emerald-50 text-emerald-800",
        meta.tone === "unverified" &&
          "border-amber-200 bg-amber-50 text-amber-800",
        meta.tone === "neutral" &&
          "border-[var(--border)] text-[var(--muted)]",
      )}
      title={tier}
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          meta.tone === "proof" && "bg-emerald-500",
          meta.tone === "unverified" && "bg-amber-500",
          meta.tone === "neutral" && "bg-zinc-400",
        )}
        aria-hidden
      />
      {meta.label}
    </span>
  );
}
