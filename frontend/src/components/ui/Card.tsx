import type { HTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

export function Card({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={clsx("glass-panel rounded-2xl p-5", className)} {...rest}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={clsx("text-sm font-medium text-ink-secondary", className)}>{children}</h3>;
}

interface StatCardProps {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: ReactNode;
  tone?: "brand" | "good" | "warning" | "serious" | "critical" | "neutral";
  trend?: { value: string; positive?: boolean };
}

const toneRing: Record<NonNullable<StatCardProps["tone"]>, string> = {
  brand: "text-brand-2",
  good: "text-good",
  warning: "text-warning",
  serious: "text-serious",
  critical: "text-critical",
  neutral: "text-ink-secondary",
};

export function StatCard({ label, value, hint, icon, tone = "neutral", trend }: StatCardProps) {
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-muted">{label}</span>
        {icon && <span className={clsx("opacity-90", toneRing[tone])}>{icon}</span>}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-semibold tabular-nums text-ink">{value}</span>
        {trend && (
          <span
            className={clsx(
              "text-xs font-medium",
              trend.positive === false ? "text-critical" : "text-good",
            )}
          >
            {trend.value}
          </span>
        )}
      </div>
      {hint && <span className="text-xs text-ink-muted">{hint}</span>}
    </Card>
  );
}
