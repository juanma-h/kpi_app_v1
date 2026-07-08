import type { ScheduleTemplateResponse } from "@/types";
import { DataTable } from "@/components/ui/DataTable";
import { ActiveBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { weekdayShort } from "@/lib/utils/labels";
import { WEEKDAY_ORDER } from "@/lib/utils/labels";

export function TemplateList({
  templates,
  onToggleStatus,
}: {
  templates: ScheduleTemplateResponse[];
  onToggleStatus?: (template: ScheduleTemplateResponse) => void;
}) {
  return (
    <DataTable
      rows={templates}
      rowKey={(row) => row.id}
      emptyTitle="Sin plantillas de horario"
      columns={[
        { key: "name", header: "Plantilla", render: (t) => <span className="font-medium text-ink">{t.name}</span> },
        {
          key: "slots",
          header: "Franjas",
          render: (t) => (
            <div className="flex flex-wrap gap-1">
              {WEEKDAY_ORDER.filter((day) => t.slots.some((s) => s.weekday === day)).map((day) => (
                <span key={day} className="rounded bg-white/5 px-1.5 py-0.5 text-[11px] text-ink-secondary">
                  {weekdayShort[day]}
                </span>
              ))}
              {t.slots.length === 0 && <span className="text-ink-muted">Sin franjas</span>}
            </div>
          ),
        },
        { key: "tz", header: "Zona horaria", render: (t) => t.timezone_name },
        { key: "grace", header: "Tolerancia", render: (t) => `${t.grace_minutes} min`, align: "right" },
        { key: "status", header: "Estado", render: (t) => <ActiveBadge active={t.is_active} /> },
        ...(onToggleStatus
          ? [
              {
                key: "actions",
                header: "",
                align: "right" as const,
                render: (t: ScheduleTemplateResponse) => (
                  <Button variant="ghost" size="sm" onClick={() => onToggleStatus(t)}>
                    {t.is_active ? "Desactivar" : "Activar"}
                  </Button>
                ),
              },
            ]
          : []),
      ]}
    />
  );
}
