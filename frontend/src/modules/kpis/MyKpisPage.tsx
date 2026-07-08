import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { subDays } from "date-fns";
import { getMyKpiOverview } from "@/lib/api/kpis";
import { getMyNoveltyKpis } from "@/lib/api/novelties";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, StatCard } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { Tabs } from "@/components/ui/Tabs";
import { DataTable } from "@/components/ui/DataTable";
import { BreakdownBarChart } from "@/components/charts/BreakdownBarChart";
import { formatDuration, formatPercent } from "@/lib/utils/format";
import { activityEventLabels } from "@/lib/utils/labels";
import { hasPunctualityData } from "@/lib/utils/kpi";

const RANGE_OPTIONS = [
  { key: "7", label: "7 días" },
  { key: "30", label: "30 días" },
  { key: "90", label: "90 días" },
  { key: "all", label: "Todo" },
];

export function MyKpisPage() {
  const [range, setRange] = useState("30");

  const startedFrom = useMemo(() => {
    if (range === "all") return undefined;
    return subDays(new Date(), Number(range)).toISOString();
  }, [range]);

  const kpiQuery = useQuery({
    queryKey: ["kpis", "me", "overview", range],
    queryFn: () => getMyKpiOverview({ started_from: startedFrom }),
  });
  const noveltyKpiQuery = useQuery({
    queryKey: ["novelties", "kpis", "me", range],
    queryFn: () => getMyNoveltyKpis({ reported_from: startedFrom }),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Mis KPIs"
        subtitle="Indicadores personales de cobertura, actividad y puntualidad."
        actions={<Tabs items={RANGE_OPTIONS} active={range} onChange={setRange} />}
      />

      {kpiQuery.isLoading ? (
        <Card>
          <LoadingState label="Calculando tus indicadores…" />
        </Card>
      ) : kpiQuery.isError ? (
        <ErrorState message="No se pudieron cargar tus KPIs." onRetry={() => kpiQuery.refetch()} />
      ) : kpiQuery.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Turnos" value={kpiQuery.data.shift_count} hint={`${kpiQuery.data.open_shift_count} abierto(s)`} />
            <StatCard
              label="Cobertura de actividad"
              value={formatPercent(kpiQuery.data.activity_coverage_rate)}
            />
            <StatCard
              label="Tiempo activo"
              value={formatDuration(kpiQuery.data.total_active_seconds)}
              tone="good"
            />
            <StatCard
              label="Puntualidad"
              value={hasPunctualityData(kpiQuery.data) ? formatPercent(kpiQuery.data.punctuality_rate) : "N/D"}
              tone={!hasPunctualityData(kpiQuery.data) ? "neutral" : kpiQuery.data.punctuality_rate >= 0.85 ? "good" : "warning"}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
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

            <Card className="flex flex-col">
              <h3 className="mb-3 text-sm font-semibold text-ink">Dominios visitados</h3>
              <DataTable
                rows={kpiQuery.data.domains}
                rowKey={(row) => row.source_domain}
                emptyTitle="Sin dominios registrados"
                columns={[
                  { key: "domain", header: "Dominio", render: (r) => r.source_domain },
                  { key: "active", header: "Activo", render: (r) => formatDuration(r.active_seconds), align: "right" },
                  { key: "idle", header: "Inactivo", render: (r) => formatDuration(r.idle_seconds), align: "right" },
                  { key: "events", header: "Eventos", render: (r) => r.event_count, align: "right" },
                ]}
              />
            </Card>
          </div>
        </>
      ) : null}

      {noveltyKpiQuery.data && noveltyKpiQuery.data.total_novelties > 0 && (
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-ink">Mis novedades</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Total" value={noveltyKpiQuery.data.total_novelties} />
            <StatCard label="Backlog" value={noveltyKpiQuery.data.backlog_count} tone="warning" />
            <StatCard label="Resueltas" value={noveltyKpiQuery.data.resolved_count} tone="good" />
            <StatCard
              label="Minutos registrados"
              value={noveltyKpiQuery.data.total_logged_minutes}
            />
          </div>
        </Card>
      )}
    </div>
  );
}
