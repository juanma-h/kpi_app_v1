import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getGlobalKpiOverview } from "@/lib/api/kpis";
import { useTeamOverview } from "./useTeamOverview";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, StatCard } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { DataTable } from "@/components/ui/DataTable";
import { Badge, RoleBadge } from "@/components/ui/Badge";
import { Tabs } from "@/components/ui/Tabs";
import { formatPercent, formatRelative, startOfTodayIso } from "@/lib/utils/format";
import { hasPunctualityData } from "@/lib/utils/kpi";

type Filter = "all" | "active" | "late" | "low_coverage";

export function TeamOverviewPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<Filter>("all");
  const todayParams = useMemo(() => ({ started_from: startOfTodayIso() }), []);

  const globalKpiQuery = useQuery({
    queryKey: ["kpis", "overview", "today"],
    queryFn: () => getGlobalKpiOverview(todayParams),
  });

  const { rows, isLoading, isError, refetch } = useTeamOverview(todayParams);

  const filteredRows = rows.filter(({ kpi }) => {
    if (!kpi) return filter === "all";
    if (filter === "active") return kpi.open_shift_count > 0;
    if (filter === "late") return kpi.late_shift_count > 0;
    if (filter === "low_coverage") return kpi.shift_count > 0 && kpi.activity_coverage_rate < 0.5;
    return true;
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Equipo hoy" subtitle="Estado operativo del equipo en la jornada actual." />

      {globalKpiQuery.data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Turnos activos" value={globalKpiQuery.data.open_shift_count} tone="good" />
          <StatCard
            label="Retrasos hoy"
            value={globalKpiQuery.data.late_shift_count}
            tone={globalKpiQuery.data.late_shift_count > 0 ? "warning" : "good"}
          />
          <StatCard label="Sin turno" value={rows.filter((r) => !r.kpi || r.kpi.shift_count === 0).length} />
          <StatCard
            label="Cobertura promedio"
            value={formatPercent(globalKpiQuery.data.activity_coverage_rate)}
          />
        </div>
      )}

      <Tabs
        items={[
          { key: "all", label: "Todos", count: rows.length },
          { key: "active", label: "Con turno activo", count: rows.filter((r) => r.kpi && r.kpi.open_shift_count > 0).length },
          { key: "late", label: "Con retraso", count: rows.filter((r) => r.kpi && r.kpi.late_shift_count > 0).length },
          {
            key: "low_coverage",
            label: "Baja cobertura",
            count: rows.filter((r) => r.kpi && r.kpi.shift_count > 0 && r.kpi.activity_coverage_rate < 0.5).length,
          },
        ]}
        active={filter}
        onChange={(k) => setFilter(k as Filter)}
      />

      {isLoading ? (
        <Card>
          <LoadingState label="Cargando estado del equipo…" />
        </Card>
      ) : isError ? (
        <ErrorState message="No se pudo cargar el equipo." onRetry={() => refetch()} />
      ) : (
        <DataTable
          rows={filteredRows}
          rowKey={(row) => row.user.id}
          onRowClick={(row) => navigate(`/app/team/users/${row.user.id}`)}
          emptyTitle="Sin empleados para este filtro"
          columns={[
            {
              key: "name",
              header: "Empleado",
              render: (r) => (
                <div className="flex flex-col">
                  <span className="font-medium text-ink">{r.user.name}</span>
                  <span className="text-xs text-ink-muted">{r.user.email}</span>
                </div>
              ),
            },
            { key: "role", header: "Rol", render: (r) => <RoleBadge role={r.user.role} /> },
            {
              key: "shift",
              header: "Turno",
              render: (r) =>
                r.isLoading ? (
                  "…"
                ) : r.kpi && r.kpi.open_shift_count > 0 ? (
                  <Badge tone="good">Activo</Badge>
                ) : r.kpi && r.kpi.shift_count > 0 ? (
                  <Badge tone="neutral">Cerrado</Badge>
                ) : (
                  <Badge tone="neutral">Sin turno</Badge>
                ),
            },
            {
              key: "punctuality",
              header: "Puntualidad",
              render: (r) =>
                !r.kpi || !hasPunctualityData(r.kpi) ? (
                  <span className="text-ink-muted">N/D</span>
                ) : r.kpi.late_shift_count > 0 ? (
                  <Badge tone="warning">Tarde</Badge>
                ) : (
                  <Badge tone="good">Puntual</Badge>
                ),
            },
            {
              key: "coverage",
              header: "Cobertura",
              render: (r) => (r.kpi ? formatPercent(r.kpi.activity_coverage_rate) : "—"),
              align: "right",
            },
            {
              key: "last_activity",
              header: "Último evento",
              render: (r) => (r.kpi ? formatRelative(r.kpi.last_activity_at) : "—"),
              align: "right",
            },
          ]}
        />
      )}
    </div>
  );
}
