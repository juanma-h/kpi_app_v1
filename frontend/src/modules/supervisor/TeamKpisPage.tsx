import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { subDays } from "date-fns";
import { getGlobalKpiOverview } from "@/lib/api/kpis";
import { getGlobalNoveltyKpis } from "@/lib/api/novelties";
import { useTeamOverview } from "./useTeamOverview";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, StatCard } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { Tabs } from "@/components/ui/Tabs";
import { DataTable } from "@/components/ui/DataTable";
import { RoleBadge } from "@/components/ui/Badge";
import { BreakdownBarChart } from "@/components/charts/BreakdownBarChart";
import { formatDuration, formatPercent } from "@/lib/utils/format";
import { activityEventLabels, noveltyStatusLabels } from "@/lib/utils/labels";
import { hasPunctualityData } from "@/lib/utils/kpi";

const RANGE_OPTIONS = [
  { key: "1", label: "Hoy" },
  { key: "7", label: "7 días" },
  { key: "30", label: "30 días" },
  { key: "all", label: "Todo" },
];

export function TeamKpisPage() {
  const navigate = useNavigate();
  const [range, setRange] = useState("7");

  const startedFrom = useMemo(() => {
    if (range === "all") return undefined;
    return subDays(new Date(), Number(range)).toISOString();
  }, [range]);

  const rangeParams = useMemo(() => ({ started_from: startedFrom }), [startedFrom]);

  const kpiQuery = useQuery({
    queryKey: ["kpis", "overview", range],
    queryFn: () => getGlobalKpiOverview(rangeParams),
  });
  const noveltyKpiQuery = useQuery({
    queryKey: ["novelties", "kpis", "overview", range],
    queryFn: () => getGlobalNoveltyKpis({ reported_from: startedFrom }),
  });
  const { rows, isLoading: teamLoading } = useTeamOverview(rangeParams);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="KPIs del equipo"
        subtitle="Cobertura, actividad, puntualidad y novedades del equipo."
        actions={<Tabs items={RANGE_OPTIONS} active={range} onChange={setRange} />}
      />

      {kpiQuery.isLoading ? (
        <Card>
          <LoadingState label="Calculando indicadores…" />
        </Card>
      ) : kpiQuery.isError ? (
        <ErrorState message="No se pudieron cargar los KPIs del equipo." onRetry={() => kpiQuery.refetch()} />
      ) : kpiQuery.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Turnos" value={kpiQuery.data.shift_count} hint={`${kpiQuery.data.open_shift_count} abierto(s)`} />
            <StatCard label="Cobertura de actividad" value={formatPercent(kpiQuery.data.activity_coverage_rate)} />
            <StatCard label="Tiempo activo total" value={formatDuration(kpiQuery.data.total_active_seconds)} tone="good" />
            <StatCard
              label="Puntualidad"
              value={hasPunctualityData(kpiQuery.data) ? formatPercent(kpiQuery.data.punctuality_rate) : "N/D"}
              tone={kpiQuery.data.punctuality_rate >= 0.85 ? "good" : "warning"}
            />
          </div>

          <Card>
            <h3 className="mb-3 text-sm font-semibold text-ink">Actividad por tipo de evento</h3>
            <BreakdownBarChart
              data={kpiQuery.data.event_types.map((e) => ({
                label: activityEventLabels[e.event_type],
                value: e.tracked_seconds > 0 ? e.tracked_seconds : e.count,
              }))}
              valueFormatter={(v) => formatDuration(v)}
            />
          </Card>
        </>
      ) : null}

      {noveltyKpiQuery.data && (
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-ink">Novedades por estado</h3>
          <BreakdownBarChart
            data={noveltyKpiQuery.data.statuses.map((s) => ({
              label: noveltyStatusLabels[s.key as keyof typeof noveltyStatusLabels] ?? s.label,
              value: s.count,
            }))}
            valueFormatter={(v) => `${v}`}
          />
        </Card>
      )}

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink-secondary">Detalle por empleado</h2>
        {teamLoading ? (
          <Card>
            <LoadingState label="Cargando detalle por empleado…" />
          </Card>
        ) : (
          <DataTable
            rows={rows}
            rowKey={(row) => row.user.id}
            onRowClick={(row) => navigate(`/app/team/users/${row.user.id}`)}
            emptyTitle="Sin empleados en este rango"
            columns={[
              {
                key: "name",
                header: "Empleado",
                render: (r) => <span className="font-medium text-ink">{r.user.name}</span>,
              },
              { key: "role", header: "Rol", render: (r) => <RoleBadge role={r.user.role} /> },
              { key: "shifts", header: "Turnos", render: (r) => r.kpi?.shift_count ?? "—", align: "right" },
              {
                key: "coverage",
                header: "Cobertura",
                render: (r) => (r.kpi ? formatPercent(r.kpi.activity_coverage_rate) : "—"),
                align: "right",
              },
              {
                key: "active",
                header: "Tiempo activo",
                render: (r) => (r.kpi ? formatDuration(r.kpi.total_active_seconds) : "—"),
                align: "right",
              },
              {
                key: "punctuality",
                header: "Puntualidad",
                render: (r) => (r.kpi && hasPunctualityData(r.kpi) ? formatPercent(r.kpi.punctuality_rate) : "N/D"),
                align: "right",
              },
            ]}
          />
        )}
      </div>
    </div>
  );
}
