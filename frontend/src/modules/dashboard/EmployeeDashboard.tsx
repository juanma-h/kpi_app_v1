import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "@/lib/session/AuthContext";
import { getMyResolvedSchedule } from "@/lib/api/schedules";
import { getMyKpiOverview } from "@/lib/api/kpis";
import { listMyActivityEvents } from "@/lib/api/activity";
import { getMyNoveltyKpis } from "@/lib/api/novelties";
import { ShiftPanel } from "@/modules/shifts/ShiftPanel";
import { ScheduleResolutionCard } from "@/modules/schedules/ScheduleResolutionCard";
import { PunctualityCard } from "@/modules/kpis/PunctualityCard";
import { ActivityTimeline } from "@/modules/activity/ActivityTimeline";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, StatCard } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { formatDuration, formatPercent, formatRelative, todayIsoDate } from "@/lib/utils/format";
import { IconActivity, IconAlert, IconArrowRight, IconCalendar, IconChart } from "@/components/ui/Icon";

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 19) return "Buenas tardes";
  return "Buenas noches";
}

export function EmployeeDashboard() {
  const { user } = useAuth();

  const scheduleQuery = useQuery({
    queryKey: ["schedule", "me", todayIsoDate()],
    queryFn: () => getMyResolvedSchedule(),
  });
  const kpiQuery = useQuery({ queryKey: ["kpis", "me", "overview"], queryFn: () => getMyKpiOverview() });
  const activityQuery = useQuery({
    queryKey: ["activity", "me", "recent"],
    queryFn: () => listMyActivityEvents({ limit: 6 }),
  });
  const noveltyKpiQuery = useQuery({ queryKey: ["novelties", "kpis", "me"], queryFn: () => getMyNoveltyKpis() });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`${greeting()}, ${user?.name.split(" ")[0]}`}
        subtitle="Esto es lo que necesitas saber hoy."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <ShiftPanel />
        {scheduleQuery.isLoading ? (
          <Card>
            <LoadingState label="Cargando horario…" />
          </Card>
        ) : scheduleQuery.data ? (
          <ScheduleResolutionCard resolution={scheduleQuery.data} />
        ) : (
          <ErrorState message="No se pudo cargar tu horario." onRetry={() => scheduleQuery.refetch()} />
        )}
        {kpiQuery.isLoading ? (
          <Card>
            <LoadingState label="Cargando puntualidad…" />
          </Card>
        ) : kpiQuery.data ? (
          <PunctualityCard kpi={kpiQuery.data} />
        ) : (
          <ErrorState message="No se pudo cargar tu puntualidad." onRetry={() => kpiQuery.refetch()} />
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        <Link to="/app/schedule">
          <Button variant="secondary" size="sm" icon={<IconCalendar />}>
            Ver mi horario
          </Button>
        </Link>
        <Link to="/app/kpis/me">
          <Button variant="secondary" size="sm" icon={<IconChart />}>
            Ver mis KPIs
          </Button>
        </Link>
        <Link to="/app/novelties">
          <Button variant="secondary" size="sm" icon={<IconAlert />}>
            Novedades
          </Button>
        </Link>
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink-secondary">Resumen de actividad de hoy</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Cobertura"
            value={kpiQuery.data ? formatPercent(kpiQuery.data.activity_coverage_rate) : "—"}
            hint="Actividad trazada vs. tiempo de sesión"
          />
          <StatCard
            label="Tiempo activo"
            value={kpiQuery.data ? formatDuration(kpiQuery.data.total_active_seconds) : "—"}
            tone="good"
          />
          <StatCard
            label="Tiempo inactivo"
            value={kpiQuery.data ? formatDuration(kpiQuery.data.total_idle_seconds) : "—"}
            tone="warning"
          />
          <StatCard
            label="Último evento"
            value={kpiQuery.data ? formatRelative(kpiQuery.data.last_activity_at) : "—"}
            icon={<IconActivity />}
          />
        </div>
      </div>

      {noveltyKpiQuery.data && noveltyKpiQuery.data.total_novelties > 0 && (
        <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-sm font-semibold text-ink">Novedades a tu cargo</h3>
            <p className="mt-1 text-xs text-ink-muted">
              {noveltyKpiQuery.data.backlog_count} en backlog · {noveltyKpiQuery.data.assigned_count} asignadas a ti
            </p>
          </div>
          <Link to="/app/novelties">
            <Button variant="secondary" size="sm" icon={<IconArrowRight />}>
              Ver novedades
            </Button>
          </Link>
        </Card>
      )}

      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-ink-secondary">Actividad reciente</h2>
          <Link to="/app/activity" className="text-xs font-medium text-brand-2 hover:underline">
            Ver todo
          </Link>
        </div>
        <Card>
          {activityQuery.isLoading ? (
            <LoadingState label="Cargando actividad…" />
          ) : (
            <ActivityTimeline events={activityQuery.data ?? []} />
          )}
        </Card>
      </div>
    </div>
  );
}
