import { useQuery } from "@tanstack/react-query";
import { getCurrentShift } from "@/lib/api/shifts";
import { getMyKpiOverview } from "@/lib/api/kpis";
import { PageHeader } from "@/components/ui/PageHeader";
import { ShiftPanel } from "./ShiftPanel";
import { Card, StatCard } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EmptyState, LoadingState } from "@/components/ui/States";
import { formatDuration, formatPercent } from "@/lib/utils/format";
import { hasPunctualityData } from "@/lib/utils/kpi";

export function ShiftPage() {
  const currentShiftQuery = useQuery({ queryKey: ["shift", "current"], queryFn: getCurrentShift });
  const shiftStartAt = currentShiftQuery.data?.start_at;

  const shiftKpiQuery = useQuery({
    queryKey: ["kpis", "me", "overview", "since-shift", shiftStartAt],
    queryFn: () => getMyKpiOverview({ started_from: shiftStartAt }),
    enabled: !!shiftStartAt,
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Mi turno" subtitle="Inicia y cierra tu turno, y consulta su avance en vivo." />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <ShiftPanel />
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink-secondary">Detalle del turno abierto</h2>
        {!shiftStartAt ? (
          <EmptyState
            title="No hay un turno abierto"
            description="Inicia tu turno para ver el detalle de actividad y puntualidad en vivo."
          />
        ) : shiftKpiQuery.isLoading ? (
          <Card>
            <LoadingState label="Cargando detalle del turno…" />
          </Card>
        ) : shiftKpiQuery.data ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Tiempo activo"
              value={formatDuration(shiftKpiQuery.data.total_active_seconds)}
              tone="good"
            />
            <StatCard
              label="Tiempo inactivo"
              value={formatDuration(shiftKpiQuery.data.total_idle_seconds)}
              tone="warning"
            />
            <StatCard label="Cobertura" value={formatPercent(shiftKpiQuery.data.activity_coverage_rate)} />
            <Card className="flex flex-col gap-2">
              <span className="text-xs font-medium uppercase tracking-wide text-ink-muted">Puntualidad</span>
              {hasPunctualityData(shiftKpiQuery.data) ? (
                <Badge tone={shiftKpiQuery.data.late_shift_count === 0 ? "good" : "critical"}>
                  {shiftKpiQuery.data.late_shift_count === 0
                    ? "Puntual"
                    : `Tarde ${shiftKpiQuery.data.average_late_by_minutes.toFixed(0)} min`}
                </Badge>
              ) : (
                <span className="text-xs text-ink-muted">Sin horario asignado para este turno.</span>
              )}
            </Card>
          </div>
        ) : null}
      </div>
    </div>
  );
}
