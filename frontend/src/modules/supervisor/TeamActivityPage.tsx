import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listActivityEvents } from "@/lib/api/activity";
import { listUsers } from "@/lib/api/users";
import type { ActivityEventType } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { SelectField } from "@/components/ui/Form";
import { DataTable } from "@/components/ui/DataTable";
import { Badge } from "@/components/ui/Badge";
import type { BadgeTone } from "@/components/ui/Badge";
import { activityEventLabels } from "@/lib/utils/labels";
import { formatDateTime, formatDuration } from "@/lib/utils/format";

const EVENT_TONE: Record<ActivityEventType, BadgeTone> = {
  PAGE_VIEW: "brand",
  HEARTBEAT: "good",
  IDLE: "warning",
  RESUME: "neutral",
};

export function TeamActivityPage() {
  const [userId, setUserId] = useState<string>("");
  const [eventType, setEventType] = useState<ActivityEventType | "">("");

  const usersQuery = useQuery({ queryKey: ["users", "all"], queryFn: () => listUsers() });
  const activityQuery = useQuery({
    queryKey: ["activity", "team", userId, eventType],
    queryFn: () =>
      listActivityEvents({
        user_id: userId ? Number(userId) : undefined,
        event_type: eventType || undefined,
        limit: 150,
      }),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Actividad del equipo" subtitle="Traza la actividad reciente por empleado y dominio." />

      <Card className="flex flex-wrap items-end gap-3">
        <div className="w-56">
          <SelectField label="Empleado" value={userId} onChange={(e) => setUserId(e.target.value)}>
            <option value="">Todos</option>
            {usersQuery.data?.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </SelectField>
        </div>
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

      {activityQuery.isLoading ? (
        <Card>
          <LoadingState label="Cargando actividad del equipo…" />
        </Card>
      ) : activityQuery.isError ? (
        <ErrorState message="No se pudo cargar la actividad." onRetry={() => activityQuery.refetch()} />
      ) : (
        <DataTable
          rows={activityQuery.data ?? []}
          rowKey={(row) => row.id}
          emptyTitle="Sin eventos para este filtro"
          columns={[
            {
              key: "user",
              header: "Empleado",
              render: (row) => usersQuery.data?.find((u) => u.id === row.user_id)?.name ?? `#${row.user_id}`,
            },
            {
              key: "type",
              header: "Tipo",
              render: (row) => <Badge tone={EVENT_TONE[row.event_type]}>{activityEventLabels[row.event_type]}</Badge>,
            },
            { key: "domain", header: "Dominio", render: (row) => row.source_domain },
            {
              key: "duration",
              header: "Duración",
              render: (row) => (row.duration_seconds != null ? formatDuration(row.duration_seconds) : "—"),
              align: "right",
            },
            { key: "occurred_at", header: "Ocurrió", render: (row) => formatDateTime(row.occurred_at), align: "right" },
          ]}
        />
      )}
    </div>
  );
}
