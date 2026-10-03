"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export function SiteNav({
  search,
  onSearch,
}: {
  search?: string;
  onSearch?: (value: string) => void;
}) {
  const [local, setLocal] = useState(search ?? "");
  const value = onSearch ? (search ?? "") : local;

  const links = useMemo(
    () => [
      { href: "/", label: "Explore" },
      { href: "/#research", label: "Research" },
      { href: "/#watchlist", label: "Watchlist" },
      { href: "/#about", label: "About" },
    ],
    [],
  );

  return (
    <header className="sticky top-0 z-40 border-b border-white/40 bg-[rgba(236,240,245,0.55)] backdrop-blur-2xl">
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="shrink-0 text-sm font-semibold">
          Tokn
        </Link>
        <nav className="hidden items-center gap-5 text-[12px] text-[var(--tokn-muted)] md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-[var(--tokn-ink)]">
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex min-w-0 flex-1 justify-end md:max-w-sm">
          <label className="glass flex w-full items-center gap-2 rounded-full px-3 py-1.5 text-[11px] text-[var(--tokn-muted)]">
            <span aria-hidden>⌕</span>
            <input
              value={value}
              onChange={(e) => {
                setLocal(e.target.value);
                onSearch?.(e.target.value);
              }}
              placeholder="Search assets, projects, or tokens…"
              className="w-full bg-transparent text-[var(--tokn-ink)] outline-none placeholder:text-[var(--tokn-muted)]"
            />
          </label>
        </div>
      </div>
    </header>
  );
}
