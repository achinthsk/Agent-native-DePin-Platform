"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "motion/react";
import type { ScoreObject } from "@/lib/api";

function AnimatedNumber({
  value,
  insufficient,
}: {
  value: number | null | undefined;
  insufficient?: boolean;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.2 });
  const [ready, setReady] = useState(false);
  const [display, setDisplay] = useState("—");

  useEffect(() => {
    const t = window.setTimeout(() => setReady(true), 120);
    return () => window.clearTimeout(t);
  }, []);

  useEffect(() => {
    if (!inView && !ready) return;
    if (
      insufficient ||
      value === null ||
      value === undefined ||
      Number.isNaN(value)
    ) {
      setDisplay("—");
      return;
    }
    const target = value;
    const start = performance.now();
    const duration = 700;
    let frame = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay((target * eased).toFixed(1));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, ready, value, insufficient]);

  return (
    <span
      ref={ref}
      className="font-mono text-2xl tabular-nums tracking-tight text-[var(--ink)]"
    >
      {display}
    </span>
  );
}

type Scores = {
  yield_score: ScoreObject;
  risk_score: ScoreObject;
  liquidity_score: ScoreObject;
  data_confidence_score: ScoreObject;
};

const AXES: { key: keyof Scores; label: string; hint: string }[] = [
  { key: "yield_score", label: "Yield", hint: "higher is better" },
  {
    key: "risk_score",
    label: "Risk quality",
    hint: "higher is better (safer ↑)",
  },
  { key: "liquidity_score", label: "Liquidity", hint: "higher is better" },
  {
    key: "data_confidence_score",
    label: "Data confidence",
    hint: "higher is better",
  },
];

export function ScoreStrip({ scores }: { scores: Scores }) {
  return (
    <div className="grid grid-cols-2 gap-px bg-[var(--rule)] sm:grid-cols-4">
      {AXES.map((axis) => {
        const score = scores[axis.key];
        return (
          <motion.div
            key={axis.key}
            layout
            className="bg-[var(--panel)] px-3 py-3"
          >
            <div className="text-[10px] font-medium uppercase tracking-[0.14em] text-[var(--muted)]">
              {axis.label}
            </div>
            <div className="mt-1 flex items-baseline gap-2">
              <AnimatedNumber
                value={score?.value}
                insufficient={score?.insufficient_data}
              />
              <span className="font-mono text-[10px] text-[var(--muted)]">
                / 100
              </span>
            </div>
            <div className="mt-1 text-[10px] text-[var(--muted)]">
              {axis.hint}
            </div>
            {score?.direction ? (
              <div className="mt-1 font-mono text-[9px] uppercase tracking-wider text-[var(--muted)]">
                {score.direction.replace(/_/g, " ")}
              </div>
            ) : null}
          </motion.div>
        );
      })}
    </div>
  );
}
