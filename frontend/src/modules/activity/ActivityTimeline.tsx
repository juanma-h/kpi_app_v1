import type { ActivityEventResponse } from "@/types";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/States";
import { activityEventLabels } from "@/lib/utils/labels";
import { formatDuration, formatRelative } from "@/lib/utils/format";
import type { BadgeTone } from "@/components/ui/Badge";

const EVENT_TONE: Record<ActivityEventResponse["event_type"], BadgeTone> = {
  PAGE_VIEW: "brand",
  HEARTBEAT: "good",
  IDLE: "warning",
  RESUME: "neutral",
};

export function ActivityTimeline({ events }: { events: ActivityEventResponse[] }) {
  if (events.length === 0) {
    return <EmptyState title="Sin actividad registrada" description="Aún no hay eventos de actividad en este rango." />;
  }

  return (
    <ol className="flex flex-col gap-0">
      {events.map((event, idx) => (
        <li key={event.id} className="relative flex gap-3 pb-5 last:pb-0">
          {idx !== events.length - 1 && (
            <span className="absolute left-[7px] top-4 h-full w-px bg-(--color-border)" />
          )}
          <span className="relative z-10 mt-1 h-3.5 w-3.5 shrink-0 rounded-full border-2 border-(--color-surface) bg-brand-2" />
          <div className="flex flex-1 flex-col gap-0.5">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={EVENT_TONE[event.event_type]}>{activityEventLabels[event.event_type]}</Badge>
              <span className="text-xs text-ink-muted">{formatRelative(event.occurred_at)}</span>
              {event.duration_seconds != null && (
                <span className="text-xs text-ink-muted">· {formatDuration(event.duration_seconds)}</span>
              )}
            </div>
            <span className="truncate text-sm text-ink-secondary">
              {event.page_title || event.source_url}
            </span>
            <span className="truncate text-xs text-ink-muted">{event.source_domain}</span>
          </div>
        </li>
      ))}
    </ol>
  );
}
