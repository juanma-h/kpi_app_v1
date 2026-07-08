import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "@/lib/session/AuthContext";
import { getGlobalKpiOverview } from "@/lib/api/kpis";
import { getGlobalNoveltyKpis } from "@/lib/api/novelties";
import { listUsers } from "@/lib/api/users";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, StatCard } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/States";
import { formatPercent, startOfTodayIso } from "@/lib/utils/format";
import { hasPunctualityData } from "@/lib/utils/kpi";
import {
  IconAlert,
  IconArrowRight,
  IconBuilding,
  IconCalendar,
  IconChart,
  IconGlobe,
  IconTeam,
  IconUsers,
} from "@/components/ui/Icon";

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 19) return "Buenas tardes";
  return "Buenas noches";
}

export function SupervisorDashboard() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";

  const kpiQuery = useQuery({
    queryKey: ["kpis", "overview", "today"],
    queryFn: () => getGlobalKpiOverview({ started_from: startOfTodayIso() }),
  });
  const noveltyKpiQuery = useQuery({
    queryKey: ["novelties", "kpis", "overview"],
    queryFn: () => getGlobalNoveltyKpis(),
  });
  const usersQuery = useQuery({ queryKey: ["users", "active"], queryFn: () => listUsers({ is_active: true }) });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`${greeting()}, ${user?.name.split(" ")[0]}`}
        subtitle="Así va tu equipo hoy."
        actions={
          <Link to="/app/team/overview">
            <Button icon={<IconArrowRight />}>Ver equipo hoy</Button>
          </Link>
        }
      />

      {kpiQuery.isLoading ? (
        <Card>
          <LoadingState label="Cargando indicadores del equipo…" />
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Turnos abiertos hoy"
            value={kpiQuery.data?.open_shift_count ?? "—"}
            tone="good"
            icon={<IconTeam />}
          />
          <StatCard
            label="Puntualidad"
            value={kpiQuery.data && hasPunctualityData(kpiQuery.data) ? formatPercent(kpiQuery.data.punctuality_rate) : "N/D"}
            hint={`${kpiQuery.data?.late_shift_count ?? 0} turno(s) tarde`}
            tone={
              !kpiQuery.data || !hasPunctualityData(kpiQuery.data)
                ? "neutral"
                : kpiQuery.data.punctuality_rate < 0.7
                  ? "critical"
                  : kpiQuery.data.punctuality_rate < 0.9
                    ? "warning"
                    : "good"
            }
          />
          <StatCard
            label="Cobertura de actividad"
            value={kpiQuery.data ? formatPercent(kpiQuery.data.activity_coverage_rate) : "—"}
          />
          <StatCard label="Empleados activos" value={usersQuery.data?.length ?? "—"} icon={<IconUsers />} />
        </div>
      )}

      {noveltyKpiQuery.data && (
        <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-sm font-semibold text-ink">Backlog de novedades</h3>
            <p className="mt-1 text-xs text-ink-muted">
              {noveltyKpiQuery.data.backlog_count} abiertas o en progreso ·{" "}
              {noveltyKpiQuery.data.unassigned_count} sin asignar
            </p>
          </div>
          <Link to="/app/novelties">
            <Button variant="secondary" size="sm" icon={<IconAlert />}>
              Gestionar novedades
            </Button>
          </Link>
        </Card>
      )}

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink-secondary">Accesos rápidos</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <QuickLink to="/app/team/overview" icon={<IconTeam />} label="Equipo hoy" />
          <QuickLink to="/app/team/kpis" icon={<IconChart />} label="KPIs del equipo" />
          <QuickLink to="/app/team/schedules" icon={<IconCalendar />} label="Horarios" />
          {isAdmin && <QuickLink to="/app/admin/users" icon={<IconUsers />} label="Administrar usuarios" />}
          {isAdmin && <QuickLink to="/app/admin/allowlist" icon={<IconGlobe />} label="Dominios permitidos" />}
          {isAdmin && <QuickLink to="/app/admin/settings" icon={<IconBuilding />} label="Catálogos operativos" />}
        </div>
      </div>
    </div>
  );
}

function QuickLink({ to, icon, label }: { to: string; icon: ReactNode; label: string }) {
  return (
    <Link to={to}>
      <Card className="flex items-center gap-3 transition-colors hover:bg-white/[0.04]">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-(--color-brand-soft) text-brand-2">
          {icon}
        </span>
        <span className="text-sm font-medium text-ink">{label}</span>
        <IconArrowRight className="ml-auto text-ink-muted" />
      </Card>
    </Link>
  );
}
