import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useTeamOverview } from "./useTeamOverview";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { DataTable } from "@/components/ui/DataTable";
import { Badge, ShiftStatusBadge } from "@/components/ui/Badge";
import { formatDuration, startOfTodayIso } from "@/lib/utils/format";
import { hasPunctualityData } from "@/lib/utils/kpi";

export function TeamShiftsPage() {
  const navigate = useNavigate();
  const todayParams = useMemo(() => ({ started_from: startOfTodayIso() }), []);
  const { rows, isLoading, isError, refetch } = useTeamOverview(todayParams);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Turnos de hoy" subtitle="Estado de turno y puntualidad de cada empleado en la jornada actual." />

      {isLoading ? (
        <Card>
          <LoadingState label="Cargando turnos de hoy…" />
        </Card>
      ) : isError ? (
        <ErrorState message="No se pudieron cargar los turnos." onRetry={() => refetch()} />
      ) : (
        <DataTable
          rows={rows}
          rowKey={(row) => row.user.id}
          onRowClick={(row) => navigate(`/app/team/users/${row.user.id}`)}
          emptyTitle="Sin empleados con turnos hoy"
          columns={[
            { key: "name", header: "Empleado", render: (r) => <span className="font-medium text-ink">{r.user.name}</span> },
            {
              key: "status",
              header: "Estado",
              render: (r) =>
                r.kpi && r.kpi.shift_count > 0 ? (
                  <ShiftStatusBadge status={r.kpi.open_shift_count > 0 ? "OPEN" : "CLOSED"} />
                ) : (
                  <Badge tone="neutral">Sin turno</Badge>
                ),
            },
            {
              key: "worked",
              header: "Tiempo de turno",
              render: (r) => (r.kpi ? formatDuration(r.kpi.total_shift_seconds) : "—"),
              align: "right",
            },
            {
              key: "punctuality",
              header: "Puntualidad",
              render: (r) =>
                !r.kpi || !hasPunctualityData(r.kpi) ? (
                  <span className="text-ink-muted">N/D</span>
                ) : r.kpi.late_shift_count > 0 ? (
                  <Badge tone="warning">Tarde ({r.kpi.average_late_by_minutes.toFixed(0)} min)</Badge>
                ) : (
                  <Badge tone="good">Puntual</Badge>
                ),
            },
            {
              key: "sessions",
              header: "Sesiones",
              render: (r) => `${r.kpi?.open_session_count ?? 0} / ${r.kpi?.session_count ?? 0}`,
              align: "right",
            },
          ]}
        />
      )}
    </div>
  );
}
