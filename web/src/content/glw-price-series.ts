/**
 * Documented GLW/USDG price samples from scoring/GLW_PRICE_EMISSIONS_FINDINGS.md
 * (Uniswap V2 Sync / getReserves — not invented). Used only for Glow charts.
 */
export type PricePoint = {
  date: string;
  price: number;
  note?: string;
};

export const GLW_PRICE_SERIES: PricePoint[] = [
  { date: "2023-12-18", price: 1.469, note: "launch-era weekly sample" },
  { date: "2024-05-21", price: 2.707 },
  { date: "2024-12-18", price: 3.718 },
  { date: "2025-01-08", price: 3.954, note: "sample peak" },
  { date: "2025-06-12", price: 0.666 },
  { date: "2025-12-19", price: 0.24 },
  { date: "2026-08-15", price: 0.231 },
  { date: "2026-08-18", price: 0.2305, note: "spot getReserves" },
];

export const GLW_PRICE_SOURCE =
  "scoring/GLW_PRICE_EMISSIONS_FINDINGS.md § Part 2 (Uniswap V2 Sync samples)";
