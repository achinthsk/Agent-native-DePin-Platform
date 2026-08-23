"use client";

import * as React from "react";
import * as RechartsPrimitive from "recharts";
import { cn } from "@/lib/utils";

export type ChartConfig = Record<string, { label?: string; color?: string }>;

const ChartContext = React.createContext<{ config: ChartConfig } | null>(null);

function useChart() {
  const ctx = React.useContext(ChartContext);
  if (!ctx) throw new Error("useChart must be used within <ChartContainer />");
  return ctx;
}

export function ChartContainer({
  config,
  className,
  children,
}: {
  config: ChartConfig;
  className?: string;
  children: React.ReactNode;
}) {
  const style = Object.fromEntries(
    Object.entries(config).map(([key, val]) => [
      `--color-${key}`,
      val.color || "var(--chart)",
    ]),
  ) as React.CSSProperties;

  return (
    <ChartContext.Provider value={{ config }}>
      <div
        className={cn("flex w-full justify-center text-xs", className)}
        style={style}
      >
        <RechartsPrimitive.ResponsiveContainer width="100%" height="100%">
          {children as React.ReactElement}
        </RechartsPrimitive.ResponsiveContainer>
      </div>
    </ChartContext.Provider>
  );
}

export const ChartTooltip = RechartsPrimitive.Tooltip;

export function ChartTooltipContent({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{
    name?: string;
    value?: number | string;
    dataKey?: string;
  }>;
  label?: string;
}) {
  const { config } = useChart();
  if (!active || !payload?.length) return null;
  return (
    <div className="border border-[var(--rule)] bg-[var(--panel)] px-2.5 py-1.5 shadow-none">
      {label ? (
        <div className="mb-1 font-mono text-[10px] text-[var(--muted)]">
          {label}
        </div>
      ) : null}
      <div className="grid gap-0.5">
        {payload.map((item) => {
          const key = String(item.dataKey ?? item.name ?? "value");
          const cfg = config[key];
          return (
            <div
              key={key}
              className="flex items-center justify-between gap-4 font-mono text-[11px] text-[var(--ink)]"
            >
              <span className="text-[var(--muted)]">
                {cfg?.label ?? item.name ?? key}
              </span>
              <span>{item.value ?? "—"}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
