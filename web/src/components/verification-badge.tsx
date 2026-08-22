import { cn } from "@/lib/utils";

const TIER_META: Record<
  string,
  { label: string; tone: "proof" | "unverified" | "neutral" }
> = {
  "cryptographic-onchain-proof": {
    label: "Cryptographic on-chain proof",
    tone: "proof",
  },
  "independent-third-party-audit": {
    label: "Independent third-party audit",
    tone: "proof",
  },
  "self-reported-unverified": {
    label: "Self-reported · unverified",
    tone: "unverified",
  },
};

export function VerificationBadge({ tier }: { tier: string | null }) {
  if (!tier) {
    return (
      <span className="inline-flex items-center border border-[var(--rule)] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-[var(--muted)]">
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
        "inline-flex items-center gap-1.5 border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider",
        meta.tone === "proof" &&
          "border-[var(--proof)] bg-[var(--proof)] text-[var(--paper)]",
        meta.tone === "unverified" &&
          "border-[var(--unverified)] text-[var(--unverified)]",
        meta.tone === "neutral" && "border-[var(--rule)] text-[var(--muted)]",
      )}
      title={tier}
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          meta.tone === "proof" && "bg-[var(--paper)]",
          meta.tone === "unverified" && "bg-[var(--unverified)]",
          meta.tone === "neutral" && "bg-[var(--muted)]",
        )}
        aria-hidden
      />
      {meta.label}
    </span>
  );
}
