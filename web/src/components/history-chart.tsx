"use client";

import { useMemo } from "react";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { realizedYieldPct, type ScoredAsset } from "@/lib/api";

const chartConfig = {
  yield: { label: "Realized yield %", color: "var(--chart)" },
  risk: { label: "Risk quality", color: "var(--chart)" },
} satisfies ChartConfig;

function shortDate(iso?: string) {
  if (!iso) return "—";
  try {
    return new Date(iso).toISOString().slice(0, 10);
  } catch {
    return iso.slice(0, 10);
  }
}

/** Bklit-inspired history chart — never invents a trend from &lt;2 points. */
export function HistoryChart({ history }: { history: ScoredAsset[] }) {
  const points = useMemo(() => {
    return [...history]
      .sort((a, b) =>
        String(a.data_pulled_at || "").localeCompare(
          String(b.data_pulled_at || ""),
        ),
      )
      .map((a) => ({
        date: shortDate(a.data_pulled_at),
        yield: realizedYieldPct(a),
        risk: a.risk_score?.insufficient_data ? null : a.risk_score?.value,
      }));
  }, [history]);

  const hasYieldSeries = points.filter((p) => p.yield !== null).length >= 2;
  const seriesKey: "yield" | "risk" = hasYieldSeries ? "yield" : "risk";
  const seriesLabel = hasYieldSeries
    ? "Realized yield % (API inputs)"
    : "Risk quality score (API)";
  const numericCount = points.filter((p) =>
    seriesKey === "yield" ? p.yield !== null : p.risk !== null,
  ).length;

  if (points.length === 0) {
    return (
      <p className="text-sm text-[var(--muted)]">
        No snapshot history returned by the API for this asset.
      </p>
    );
  }

  if (points.length < 2 || numericCount < 2) {
    const only = points[0];
    const v = seriesKey === "yield" ? only.yield : only.risk;
    return (
      <div className="rounded-lg border border-dashed border-[var(--border)] bg-zinc-50/80 px-3 py-4">
        <div className="text-[10px] font-medium uppercase tracking-[0.12em] text-[var(--muted)]">
          Snapshot history
        </div>
        <p className="mt-2 text-sm leading-relaxed text-zinc-700">
          {points.length === 1 ? "Single" : "Insufficient distinct"} API
          snapshot{points.length === 1 ? "" : "s"} for a series
          {only?.date ? (
            <>
              {" "}
              (latest <span className="font-mono">{only.date}</span>
              {v !== null && v !== undefined ? (
                <>
                  ; {seriesLabel.toLowerCase()}{" "}
                  <span className="font-mono">{v}</span>
                </>
              ) : null}
              )
            </>
          ) : null}
          . No trend line is drawn from fewer than two points.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-2 flex items-baseline justify-between gap-3">
        <div className="text-[10px] font-medium uppercase tracking-[0.12em] text-[var(--muted)]">
          {seriesLabel}
        </div>
        <div className="font-mono text-[10px] text-[var(--muted)]">
          {points.length} snapshots · live API
        </div>
      </div>
      <ChartContainer config={chartConfig} className="h-44 min-h-44 w-full">
        <AreaChart
          accessibilityLayer
          data={points}
          margin={{ left: 4, right: 8, top: 8, bottom: 0 }}
        >
          <CartesianGrid
            vertical={false}
            stroke="var(--border)"
            strokeDasharray="3 3"
          />
          <XAxis
            dataKey="date"
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            tick={{ fill: "var(--muted)", fontSize: 10 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            width={36}
            tick={{ fill: "var(--muted)", fontSize: 10 }}
            domain={["auto", "auto"]}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Area
            dataKey={seriesKey}
            type="monotone"
            fill={`var(--color-${seriesKey})`}
            fillOpacity={0.1}
            stroke={`var(--color-${seriesKey})`}
            strokeWidth={2}
            dot={{ r: 3, fill: "var(--chart)", strokeWidth: 0 }}
            isAnimationActive
            animationDuration={900}
            connectNulls={false}
          />
        </AreaChart>
      </ChartContainer>
    </div>
  );
}
