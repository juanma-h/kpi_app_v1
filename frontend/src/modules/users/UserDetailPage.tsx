import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getUser, setUserStatus, updateUser } from "@/lib/api/users";
import { getUserKpiOverview } from "@/lib/api/kpis";
import { getUserResolvedSchedule } from "@/lib/api/schedules";
import { getUserNoveltyKpis } from "@/lib/api/novelties";
import { extractErrorMessage } from "@/lib/api/client";
import { useAuth } from "@/lib/session/AuthContext";
import type { UserRole } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, StatCard } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { ActiveBadge, RoleBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { InputField, SelectField } from "@/components/ui/Form";
import { ScheduleResolutionCard } from "@/modules/schedules/ScheduleResolutionCard";
import { formatDuration, formatPercent } from "@/lib/utils/format";
import { roleLabels } from "@/lib/utils/labels";
import { hasPunctualityData } from "@/lib/utils/kpi";

export function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const userId = Number(id);
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = currentUser?.role === "ADMIN";
  const [error, setError] = useState<string | null>(null);

  const userQuery = useQuery({ queryKey: ["users", userId], queryFn: () => getUser(userId), enabled: !!userId });
  const kpiQuery = useQuery({ queryKey: ["kpis", "user", userId], queryFn: () => getUserKpiOverview(userId), enabled: !!userId });
  const scheduleQuery = useQuery({
    queryKey: ["schedule", "user", userId],
    queryFn: () => getUserResolvedSchedule(userId),
    enabled: !!userId,
  });
  const noveltyKpiQuery = useQuery({
    queryKey: ["novelties", "kpis", "user", userId],
    queryFn: () => getUserNoveltyKpis(userId),
    enabled: !!userId,
  });

  const [form, setForm] = useState<{ name: string; email: string; role: UserRole } | null>(null);

  const updateMutation = useMutation({
    mutationFn: () =>
      updateUser(userId, {
        name: form?.name,
        email: form?.email,
        role: form?.role,
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["users", userId] });
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo actualizar el usuario.")),
  });

  const statusMutation = useMutation({
    mutationFn: (isActive: boolean) => setUserStatus(userId, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users", userId] });
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo cambiar el estado del usuario.")),
  });

  if (userQuery.isLoading) return <LoadingState label="Cargando usuario…" />;
  if (userQuery.isError || !userQuery.data) {
    return <ErrorState message="No se pudo cargar este usuario." onRetry={() => userQuery.refetch()} />;
  }

  const user = userQuery.data;
  const activeForm = form ?? { name: user.name, email: user.email, role: user.role };

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    updateMutation.mutate();
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={user.name}
        subtitle={user.email}
        actions={
          <Button variant="secondary" size="sm" onClick={() => navigate(-1)}>
            ← Volver
          </Button>
        }
      />

      <Card className="flex flex-wrap items-center gap-3">
        <RoleBadge role={user.role} />
        <ActiveBadge active={user.is_active} />
        {isAdmin && (
          <Button
            variant={user.is_active ? "danger" : "secondary"}
            size="sm"
            className="ml-auto"
            loading={statusMutation.isPending}
            onClick={() => statusMutation.mutate(!user.is_active)}
          >
            {user.is_active ? "Desactivar usuario" : "Activar usuario"}
          </Button>
        )}
      </Card>

      {kpiQuery.data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Turnos" value={kpiQuery.data.shift_count} hint={`${kpiQuery.data.open_shift_count} abierto(s)`} />
          <StatCard label="Cobertura" value={formatPercent(kpiQuery.data.activity_coverage_rate)} />
          <StatCard label="Tiempo activo" value={formatDuration(kpiQuery.data.total_active_seconds)} tone="good" />
          <StatCard
            label="Puntualidad"
            value={hasPunctualityData(kpiQuery.data) ? formatPercent(kpiQuery.data.punctuality_rate) : "N/D"}
          />
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {scheduleQuery.data && <ScheduleResolutionCard resolution={scheduleQuery.data} />}

        {noveltyKpiQuery.data && (
          <Card className="flex flex-col gap-3">
            <h3 className="text-sm font-semibold text-ink">Novedades</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-xs text-ink-muted">Total</dt>
                <dd className="text-ink">{noveltyKpiQuery.data.total_novelties}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-muted">Backlog</dt>
                <dd className="text-ink">{noveltyKpiQuery.data.backlog_count}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-muted">Asignadas</dt>
                <dd className="text-ink">{noveltyKpiQuery.data.assigned_count}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-muted">Resueltas</dt>
                <dd className="text-ink">{noveltyKpiQuery.data.resolved_count}</dd>
              </div>
            </div>
          </Card>
        )}
      </div>

      {isAdmin && (
        <Card>
          <h3 className="mb-4 text-sm font-semibold text-ink">Editar usuario</h3>
          <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-3">
            <InputField
              label="Nombre"
              value={activeForm.name}
              onChange={(e) => setForm({ ...activeForm, name: e.target.value })}
              required
            />
            <InputField
              label="Correo"
              type="email"
              value={activeForm.email}
              onChange={(e) => setForm({ ...activeForm, email: e.target.value })}
              required
            />
            <SelectField
              label="Rol"
              value={activeForm.role}
              onChange={(e) => setForm({ ...activeForm, role: e.target.value as UserRole })}
              disabled={currentUser?.id === user.id}
            >
              {(Object.keys(roleLabels) as UserRole[]).map((role) => (
                <option key={role} value={role}>
                  {roleLabels[role]}
                </option>
              ))}
            </SelectField>
            <div className="sm:col-span-3">
              {error && <p className="mb-3 text-sm text-critical">{error}</p>}
              <Button type="submit" loading={updateMutation.isPending}>
                Guardar cambios
              </Button>
            </div>
          </form>
        </Card>
      )}
    </div>
  );
}
