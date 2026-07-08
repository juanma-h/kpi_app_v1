import type { ReactNode } from "react";
import clsx from "clsx";
import type { NoveltyPriority, NoveltyStatus, ShiftStatus, UserRole } from "@/types";
import {
  noveltyPriorityLabels,
  noveltyStatusLabels,
  roleLabels,
  shiftStatusLabels,
} from "@/lib/utils/labels";

export type BadgeTone = "neutral" | "good" | "warning" | "serious" | "critical" | "brand";

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-white/6 text-ink-secondary border-white/10",
  good: "bg-good/15 text-good border-good/35",
  warning: "bg-warning/15 text-warning border-warning/35",
  serious: "bg-serious/15 text-serious border-serious/35",
  critical: "bg-critical/15 text-critical border-critical/40",
  brand: "bg-(--color-brand-soft) text-[#c9c1ff] border-brand/40",
};

export function Badge({
  tone = "neutral",
  icon,
  children,
  className,
}: {
  tone?: BadgeTone;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium leading-none",
        toneClasses[tone],
        className,
      )}
    >
      {icon}
      {children}
    </span>
  );
}

export function Dot({ tone = "neutral", pulse = false }: { tone?: BadgeTone; pulse?: boolean }) {
  const dotColor: Record<BadgeTone, string> = {
    neutral: "bg-ink-muted",
    good: "bg-good",
    warning: "bg-warning",
    serious: "bg-serious",
    critical: "bg-critical",
    brand: "bg-brand-2",
  };
  return (
    <span className={clsx("relative inline-flex h-2 w-2 rounded-full", dotColor[tone], pulse && "pulse-dot")} />
  );
}

export function ShiftStatusBadge({ status }: { status: ShiftStatus }) {
  return (
    <Badge tone={status === "OPEN" ? "good" : "neutral"} icon={<Dot tone={status === "OPEN" ? "good" : "neutral"} pulse={status === "OPEN"} />}>
      {shiftStatusLabels[status]}
    </Badge>
  );
}

export function RoleBadge({ role }: { role: UserRole }) {
  const tone: BadgeTone = role === "ADMIN" ? "brand" : role === "SUPERVISOR" ? "serious" : "neutral";
  return <Badge tone={tone}>{roleLabels[role]}</Badge>;
}

export function NoveltyPriorityBadge({ priority }: { priority: NoveltyPriority }) {
  const tone: Record<NoveltyPriority, BadgeTone> = {
    LOW: "neutral",
    MEDIUM: "warning",
    HIGH: "serious",
    CRITICAL: "critical",
  };
  return <Badge tone={tone[priority]}>{noveltyPriorityLabels[priority]}</Badge>;
}

export function NoveltyStatusBadge({ status }: { status: NoveltyStatus }) {
  const tone: Record<NoveltyStatus, BadgeTone> = {
    OPEN: "warning",
    IN_PROGRESS: "brand",
    BLOCKED: "critical",
    RESOLVED: "good",
    CLOSED: "neutral",
  };
  return <Badge tone={tone[status]}>{noveltyStatusLabels[status]}</Badge>;
}

export function ActiveBadge({ active }: { active: boolean }) {
  return (
    <Badge tone={active ? "good" : "neutral"} icon={<Dot tone={active ? "good" : "neutral"} />}>
      {active ? "Activo" : "Inactivo"}
    </Badge>
  );
}
