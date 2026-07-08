import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listMyActivityEvents } from "@/lib/api/activity";
import type { ActivityEventType } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { SelectField } from "@/components/ui/Form";
import { DataTable } from "@/components/ui/DataTable";
import { Badge } from "@/components/ui/Badge";
import { activityEventLabels } from "@/lib/utils/labels";
import { formatDateTime, formatDuration } from "@/lib/utils/format";
import type { BadgeTone } from "@/components/ui/Badge";

const EVENT_TONE: Record<ActivityEventType, BadgeTone> = {
  PAGE_VIEW: "brand",
  HEARTBEAT: "good",
  IDLE: "warning",
  RESUME: "neutral",
};

export function MyActivityPage() {
  const [eventType, setEventType] = useState<ActivityEventType | "">("");

  const query = useQuery({
    queryKey: ["activity", "me", eventType],
    queryFn: () => listMyActivityEvents({ event_type: eventType || undefined, limit: 150 }),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Mi actividad" subtitle="Trazabilidad de tu actividad reciente sobre dominios permitidos." />

      <Card className="flex flex-wrap items-end gap-3">
        <div className="w-48">
          <SelectField
            label="Tipo de evento"
            value={eventType}
            onChange={(e) => setEventType(e.target.value as ActivityEventType | "")}
          >
            <option value="">Todos</option>
            {(Object.keys(activityEventLabels) as ActivityEventType[]).map((type) => (
              <option key={type} value={type}>
                {activityEventLabels[type]}
              </option>
            ))}
          </SelectField>
        </div>
      </Card>

      {query.isLoading ? (
        <Card>
          <LoadingState label="Cargando actividad…" />
        </Card>
      ) : query.isError ? (
        <ErrorState message="No se pudo cargar tu actividad." onRetry={() => query.refetch()} />
      ) : (
        <DataTable
          rows={query.data ?? []}
          rowKey={(row) => row.id}
          emptyTitle="Sin eventos para este filtro"
          columns={[
            {
              key: "type",
              header: "Tipo",
              render: (row) => <Badge tone={EVENT_TONE[row.event_type]}>{activityEventLabels[row.event_type]}</Badge>,
            },
            { key: "domain", header: "Dominio", render: (row) => row.source_domain },
            {
              key: "page",
              header: "Página",
              render: (row) => (
                <span className="block max-w-xs truncate" title={row.source_url}>
                  {row.page_title || row.source_url}
                </span>
              ),
            },
            {
              key: "duration",
              header: "Duración",
              render: (row) => (row.duration_seconds != null ? formatDuration(row.duration_seconds) : "—"),
              align: "right",
            },
            {
              key: "occurred_at",
              header: "Ocurrió",
              render: (row) => formatDateTime(row.occurred_at),
              align: "right",
            },
          ]}
        />
      )}
    </div>
  );
}
