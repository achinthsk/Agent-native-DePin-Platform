"use client";

import { useMemo, type ReactNode } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { realizedYieldPct, type ScoredAsset } from "@/lib/api";
import {
  GLW_PRICE_SERIES,
  GLW_PRICE_SOURCE,
} from "@/content/glw-price-series";

const lineConfig = {
  value: { label: "Value", color: "var(--chart)" },
} satisfies ChartConfig;

const barConfig = {
  value: { label: "Score", color: "var(--chart)" },
} satisfies ChartConfig;

function shortDate(iso?: string) {
  if (!iso) return "—";
  try {
    return new Date(iso).toISOString().slice(0, 10);
  } catch {
    return iso.slice(0, 10);
  }
}

type Props = {
  asset: ScoredAsset;
  history?: ScoredAsset[];
  /** Compact sparkline for discovery cards */
  compact?: boolean;
};

/**
 * One real chart per asset:
 * - Glow: documented GLW/USDG Sync price path
 * - Others with ≥2 snapshots: risk (and yield when available) over snapshots
 * - Else: four-axis score bars for the current snapshot (never invents a series)
 */
export function AssetSeriesChart({ asset, history = [], compact = false }: Props) {
  const glowSeries = useMemo(() => {
    if (asset.source_platform !== "glow") return null;
    return GLW_PRICE_SERIES.map((p) => ({
      date: p.date,
      value: p.price,
    }));
  }, [asset.source_platform]);

  const historySeries = useMemo(() => {
    const points = [...history]
      .sort((a, b) =>
        String(a.data_pulled_at || a.snapshot_file || "").localeCompare(
          String(b.data_pulled_at || b.snapshot_file || ""),
        ),
      )
      .map((a) => {
        const y = realizedYieldPct(a);
        const risk =
          a.risk_score?.insufficient_data || a.risk_score?.value == null
            ? null
            : a.risk_score.value;
        return {
          date: shortDate(a.data_pulled_at),
          yield: y,
          risk,
        };
      });
    const yieldCount = points.filter((p) => p.yield != null).length;
    const riskCount = points.filter((p) => p.risk != null).length;
    if (yieldCount >= 2) {
      return {
        kind: "yield" as const,
        label: "Realized yield % (snapshot history)",
        data: points
          .filter((p) => p.yield != null)
          .map((p) => ({ date: p.date, value: p.yield as number })),
      };
    }
    if (riskCount >= 2) {
      return {
        kind: "risk" as const,
        label: "Risk quality score (snapshot history)",
        data: points
          .filter((p) => p.risk != null)
          .map((p) => ({ date: p.date, value: p.risk as number })),
      };
    }
    return null;
  }, [history]);

  const barData = useMemo(
    () => [
      {
        name: "Risk",
        value: asset.risk_score.insufficient_data
          ? 0
          : (asset.risk_score.value ?? 0),
      },
      {
        name: "Yield",
        value: asset.yield_score.insufficient_data
          ? 0
          : (asset.yield_score.value ?? 0),
      },
      {
        name: "Exit",
        value: asset.liquidity_score.insufficient_data
          ? 0
          : (asset.liquidity_score.value ?? 0),
      },
      {
        name: "Conf.",
        value: asset.data_confidence_score.insufficient_data
          ? 0
          : (asset.data_confidence_score.value ?? 0),
      },
    ],
    [asset],
  );

  const fillId = `fill-${asset.asset_id.replace(/[^a-zA-Z0-9_-]/g, "")}`;
  const chartClass = compact
    ? "h-[104px] min-h-[104px] w-full"
    : "h-[200px] min-h-[200px] w-full";

  if (glowSeries && glowSeries.length >= 2) {
    return (
      <ChartBlock
        title={compact ? "Token value" : "Token value over time"}
        subtitle={compact ? "Documented Sync samples" : GLW_PRICE_SOURCE}
        compact={compact}
      >
        <ChartContainer config={lineConfig} className={chartClass}>
          <AreaChart data={glowSeries} margin={{ left: 4, right: 4, top: 8, bottom: 0 }}>
            <defs>
              <linearGradient id={fillId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--chart)" stopOpacity={0.32} />
                <stop offset="100%" stopColor="var(--chart)" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            {!compact ? <CartesianGrid vertical={false} strokeOpacity={0.15} /> : null}
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={6}
              tick={{ fontSize: 10 }}
              hide={compact}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              width={compact ? 0 : 36}
              tick={{ fontSize: 10 }}
              hide={compact}
            />
            {!compact ? (
              <ChartTooltip content={<ChartTooltipContent />} />
            ) : null}
            <Area
              type="monotone"
              dataKey="value"
              stroke="var(--chart)"
              fill={`url(#${fillId})`}
              strokeWidth={1.75}
              dot={false}
            />
          </AreaChart>
        </ChartContainer>
      </ChartBlock>
    );
  }

  if (historySeries) {
    return (
      <ChartBlock
        title={compact ? historySeries.label.split(" (")[0] : historySeries.label}
        subtitle="From stored API snapshots — not a live exchange feed"
        compact={compact}
      >
        <ChartContainer config={lineConfig} className={chartClass}>
          <AreaChart
            data={historySeries.data}
            margin={{ left: 4, right: 4, top: 8, bottom: 0 }}
          >
            <defs>
              <linearGradient id={`${fillId}-h`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--chart)" stopOpacity={0.32} />
                <stop offset="100%" stopColor="var(--chart)" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            {!compact ? <CartesianGrid vertical={false} strokeOpacity={0.15} /> : null}
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 10 }}
              hide={compact}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              width={compact ? 0 : 36}
              tick={{ fontSize: 10 }}
              hide={compact}
            />
            {!compact ? (
              <ChartTooltip content={<ChartTooltipContent />} />
            ) : null}
            <Area
              type="monotone"
              dataKey="value"
              stroke="var(--chart)"
              fill={`url(#${fillId}-h)`}
              strokeWidth={1.75}
              dot={compact ? false : { r: 2.5 }}
            />
          </AreaChart>
        </ChartContainer>
      </ChartBlock>
    );
  }

  return (
    <ChartBlock
      title={compact ? "Score profile" : "Four-axis scores (current snapshot)"}
      subtitle="No multi-point price series in API — showing live scores instead of inventing a trend"
      compact={compact}
    >
      <ChartContainer config={barConfig} className={chartClass}>
        <BarChart data={barData} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
          {!compact ? <CartesianGrid vertical={false} strokeOpacity={0.12} /> : null}
          <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 10 }} />
          <YAxis
            domain={[0, 100]}
            tickLine={false}
            axisLine={false}
            width={compact ? 0 : 28}
            tick={{ fontSize: 10 }}
            hide={compact}
          />
          {!compact ? <ChartTooltip content={<ChartTooltipContent />} /> : null}
          <Bar dataKey="value" fill="var(--chart)" radius={[6, 6, 2, 2]} />
        </BarChart>
      </ChartContainer>
    </ChartBlock>
  );
}

function ChartBlock({
  title,
  subtitle,
  compact,
  children,
}: {
  title: string;
  subtitle: string;
  compact?: boolean;
  children: ReactNode;
}) {
  return (
    <div className={compact ? "" : "glass-row p-4"}>
      <div className="mb-2 flex items-baseline justify-between gap-2">
        <p className={compact ? "eyebrow" : "text-sm font-medium"}>{title}</p>
        {!compact ? <span className="pill pill-muted">Documented</span> : null}
      </div>
      {children}
      {!compact ? (
        <p className="mt-2 text-[10px] leading-relaxed text-[var(--tokn-muted)]">
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}
