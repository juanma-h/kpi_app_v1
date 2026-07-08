import type { ScheduleResolutionResponse } from "@/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconCalendar } from "@/components/ui/Icon";
import { formatTime } from "@/lib/utils/format";
import { weekdayLabels } from "@/lib/utils/labels";

export function ScheduleResolutionCard({ resolution }: { resolution: ScheduleResolutionResponse }) {
  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-ink-muted">
          <IconCalendar className="text-brand-2" />
          Horario de hoy
        </span>
        <Badge tone={resolution.is_scheduled ? "brand" : "neutral"}>
          {weekdayLabels[resolution.weekday]}
        </Badge>
      </div>

      {resolution.is_scheduled ? (
        <div className="mt-1 flex flex-col gap-1">
          <span className="text-3xl font-semibold tabular-nums text-ink">
            {formatTime(resolution.expected_start_at)} – {formatTime(resolution.expected_end_at)}
          </span>
          <span className="text-xs text-ink-muted">
            {resolution.schedule_template_name}
            {resolution.grace_minutes ? ` · ${resolution.grace_minutes} min de tolerancia` : ""}
          </span>
        </div>
      ) : (
        <div className="mt-1 flex flex-col gap-1">
          <span className="text-lg font-medium text-ink-secondary">Sin horario asignado</span>
          <span className="text-xs text-ink-muted">{resolution.resolution_reason ?? "—"}</span>
        </div>
      )}
    </Card>
  );
}
