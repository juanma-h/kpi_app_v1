import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createNoveltyLog,
  getNovelty,
  listNoveltyLogs,
  updateNoveltyAssignment,
  updateNoveltyStatus,
} from "@/lib/api/novelties";
import { listUsers } from "@/lib/api/users";
import { extractErrorMessage } from "@/lib/api/client";
import { useAuth } from "@/lib/session/AuthContext";
import type { NoveltyLogType, NoveltyStatus } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/States";
import { NoveltyPriorityBadge, NoveltyStatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { SelectField, TextareaField, InputField } from "@/components/ui/Form";
import { formatDateTime } from "@/lib/utils/format";
import { noveltyLogTypeLabels, noveltyStatusLabels, NOVELTY_STATUS_ORDER } from "@/lib/utils/labels";

function nextAllowedStatuses(current: NoveltyStatus): NoveltyStatus[] {
  if (current === "CLOSED") return ["CLOSED"];
  if (current === "RESOLVED") return ["RESOLVED", "CLOSED"];
  return NOVELTY_STATUS_ORDER;
}

export function NoveltyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const noveltyId = Number(id);
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const isManager = currentUser?.role === "ADMIN" || currentUser?.role === "SUPERVISOR";

  const noveltyQuery = useQuery({
    queryKey: ["novelties", noveltyId],
    queryFn: () => getNovelty(noveltyId),
    enabled: !!noveltyId,
  });
  const logsQuery = useQuery({
    queryKey: ["novelties", noveltyId, "logs"],
    queryFn: () => listNoveltyLogs(noveltyId),
    enabled: !!noveltyId,
  });
  const usersQuery = useQuery({
    queryKey: ["users", "active"],
    queryFn: () => listUsers({ is_active: true }),
    enabled: isManager,
  });

  const [statusValue, setStatusValue] = useState<NoveltyStatus | "">("");
  const [statusNote, setStatusNote] = useState("");
  const [statusError, setStatusError] = useState<string | null>(null);

  const [assigneeValue, setAssigneeValue] = useState("");
  const [assigneeError, setAssigneeError] = useState<string | null>(null);

  const [logForm, setLogForm] = useState({
    content: "",
    log_type: "DAILY_UPDATE" as NoveltyLogType,
    worked_minutes: "",
  });
  const [logError, setLogError] = useState<string | null>(null);

  function invalidateNovelty() {
    queryClient.invalidateQueries({ queryKey: ["novelties", noveltyId] });
    queryClient.invalidateQueries({ queryKey: ["novelties", noveltyId, "logs"] });
    queryClient.invalidateQueries({ queryKey: ["novelties"] });
  }

  const statusMutation = useMutation({
    mutationFn: () => updateNoveltyStatus(noveltyId, statusValue as NoveltyStatus, statusNote || undefined),
    onSuccess: () => {
      setStatusError(null);
      setStatusValue("");
      setStatusNote("");
      invalidateNovelty();
    },
    onError: (err) => setStatusError(extractErrorMessage(err, "No se pudo actualizar el estado.")),
  });

  const assignMutation = useMutation({
    mutationFn: () => updateNoveltyAssignment(noveltyId, assigneeValue ? Number(assigneeValue) : null),
    onSuccess: () => {
      setAssigneeError(null);
      invalidateNovelty();
    },
    onError: (err) => setAssigneeError(extractErrorMessage(err, "No se pudo actualizar la asignación.")),
  });

  const logMutation = useMutation({
    mutationFn: () =>
      createNoveltyLog(noveltyId, {
        content: logForm.content,
        log_type: logForm.log_type,
        worked_minutes: logForm.worked_minutes ? Number(logForm.worked_minutes) : undefined,
      }),
    onSuccess: () => {
      setLogError(null);
      setLogForm({ content: "", log_type: "DAILY_UPDATE", worked_minutes: "" });
      invalidateNovelty();
    },
    onError: (err) => setLogError(extractErrorMessage(err, "No se pudo agregar la bitácora.")),
  });

  if (noveltyQuery.isLoading) return <LoadingState label="Cargando novedad…" />;
  if (noveltyQuery.isError || !noveltyQuery.data) {
    return <ErrorState message="No se pudo cargar esta novedad." onRetry={() => noveltyQuery.refetch()} />;
  }

  const novelty = noveltyQuery.data;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={novelty.title}
        subtitle={`${novelty.novelty_type} · ${novelty.area.name} · ${novelty.source_system.name}`}
        actions={
          <Button variant="secondary" size="sm" onClick={() => navigate(-1)}>
            ← Volver
          </Button>
        }
      />

      <div className="flex flex-wrap gap-2">
        <NoveltyPriorityBadge priority={novelty.priority} />
        <NoveltyStatusBadge status={novelty.status} />
      </div>

      <Card className="grid gap-4 sm:grid-cols-2">
        <div>
          <h3 className="mb-2 text-sm font-semibold text-ink">Descripción</h3>
          <p className="whitespace-pre-line text-sm text-ink-secondary">{novelty.description}</p>
        </div>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <Detail label="Reportó" value={novelty.reported_by.name} />
          <Detail label="Asignada a" value={novelty.assigned_user?.name ?? "Sin asignar"} />
          <Detail label="Reportada" value={formatDateTime(novelty.reported_at)} />
          <Detail label="Primera acción" value={formatDateTime(novelty.first_action_at)} />
          <Detail label="Resuelta" value={formatDateTime(novelty.resolved_at)} />
          <Detail label="Cerrada" value={formatDateTime(novelty.closed_at)} />
          <Detail label="Ref. pedido" value={novelty.order_reference ?? "—"} />
          <Detail label="Ref. externa" value={novelty.external_reference ?? "—"} />
        </dl>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-ink">Cambiar estado</h3>
          <div className="flex flex-col gap-3">
            <SelectField value={statusValue} onChange={(e) => setStatusValue(e.target.value as NoveltyStatus)}>
              <option value="">Selecciona un estado</option>
              {nextAllowedStatuses(novelty.status).map((s) => (
                <option key={s} value={s}>
                  {noveltyStatusLabels[s]}
                </option>
              ))}
            </SelectField>
            <TextareaField
              placeholder="Nota opcional sobre el cambio"
              value={statusNote}
              onChange={(e) => setStatusNote(e.target.value)}
              rows={2}
            />
            {statusError && <p className="text-xs text-critical">{statusError}</p>}
            <Button
              size="sm"
              disabled={!statusValue}
              loading={statusMutation.isPending}
              onClick={() => statusMutation.mutate()}
            >
              Actualizar estado
            </Button>
          </div>
        </Card>

        {isManager && (
          <Card>
            <h3 className="mb-3 text-sm font-semibold text-ink">Reasignar novedad</h3>
            <div className="flex flex-col gap-3">
              <SelectField value={assigneeValue} onChange={(e) => setAssigneeValue(e.target.value)}>
                <option value="">Sin asignar</option>
                {usersQuery.data?.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name}
                  </option>
                ))}
              </SelectField>
              {assigneeError && <p className="text-xs text-critical">{assigneeError}</p>}
              <Button size="sm" variant="secondary" loading={assignMutation.isPending} onClick={() => assignMutation.mutate()}>
                Guardar asignación
              </Button>
            </div>
          </Card>
        )}
      </div>

      <Card>
        <h3 className="mb-4 text-sm font-semibold text-ink">Bitácora</h3>

        <form
          onSubmit={(e: FormEvent) => {
            e.preventDefault();
            setLogError(null);
            logMutation.mutate();
          }}
          className="mb-6 flex flex-col gap-3 border-b border-(--color-border) pb-6"
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <SelectField
              label="Tipo de entrada"
              value={logForm.log_type}
              onChange={(e) => setLogForm({ ...logForm, log_type: e.target.value as NoveltyLogType })}
            >
              {(Object.keys(noveltyLogTypeLabels) as NoveltyLogType[]).map((t) => (
                <option key={t} value={t}>
                  {noveltyLogTypeLabels[t]}
                </option>
              ))}
            </SelectField>
            <InputField
              label="Minutos trabajados (opcional)"
              type="number"
              min={1}
              max={720}
              value={logForm.worked_minutes}
              onChange={(e) => setLogForm({ ...logForm, worked_minutes: e.target.value })}
            />
          </div>
          <TextareaField
            label="Detalle"
            required
            minLength={5}
            value={logForm.content}
            onChange={(e) => setLogForm({ ...logForm, content: e.target.value })}
            placeholder="Describe el avance de hoy sobre este caso"
          />
          {logError && <p className="text-xs text-critical">{logError}</p>}
          <Button type="submit" size="sm" className="self-start" loading={logMutation.isPending}>
            Agregar entrada
          </Button>
        </form>

        {logsQuery.isLoading ? (
          <LoadingState label="Cargando bitácora…" />
        ) : (logsQuery.data ?? []).length === 0 ? (
          <EmptyState title="Sin entradas en la bitácora" description="Agrega la primera entrada arriba." />
        ) : (
          <ol className="flex flex-col gap-4">
            {(logsQuery.data ?? [])
              .slice()
              .reverse()
              .map((log) => (
                <li key={log.id} className="rounded-xl border border-(--color-border) bg-white/[0.02] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-medium text-ink">{log.author.name}</span>
                    <span className="text-xs text-ink-muted">{formatDateTime(log.logged_at)}</span>
                  </div>
                  <p className="mt-1 text-xs text-ink-muted">
                    {noveltyLogTypeLabels[log.log_type]}
                    {log.worked_minutes ? ` · ${log.worked_minutes} min` : ""}
                  </p>
                  <p className="mt-2 whitespace-pre-line text-sm text-ink-secondary">{log.content}</p>
                </li>
              ))}
          </ol>
        )}
      </Card>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-muted">{label}</dt>
      <dd className="text-ink-secondary">{value}</dd>
    </div>
  );
}
