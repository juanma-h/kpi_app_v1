import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listMyNovelties, listNovelties } from "@/lib/api/novelties";
import type { NoveltyPriority, NoveltyStatus } from "@/types";
import { useAuth } from "@/lib/session/AuthContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { SelectField } from "@/components/ui/Form";
import { DataTable } from "@/components/ui/DataTable";
import { NoveltyPriorityBadge, NoveltyStatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Tabs } from "@/components/ui/Tabs";
import { NewNoveltyModal } from "./NewNoveltyModal";
import { noveltyPriorityLabels, noveltyStatusLabels } from "@/lib/utils/labels";
import { formatRelative } from "@/lib/utils/format";
import { IconPlus } from "@/components/ui/Icon";

export function NoveltiesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const canSeeGlobal = user?.role === "ADMIN" || user?.role === "SUPERVISOR";
  const [scope, setScope] = useState<"mine" | "all">("mine");
  const [status, setStatus] = useState<NoveltyStatus | "">("");
  const [priority, setPriority] = useState<NoveltyPriority | "">("");
  const [modalOpen, setModalOpen] = useState(false);

  const query = useQuery({
    queryKey: ["novelties", scope, status, priority],
    queryFn: () => {
      const params = { status: status || undefined, priority: priority || undefined, limit: 200 };
      return scope === "all" && canSeeGlobal ? listNovelties(params) : listMyNovelties(params);
    },
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Novedades"
        subtitle="Casos operativos reportados, en gestión y bitácora de avance."
        actions={
          <Button icon={<IconPlus />} onClick={() => setModalOpen(true)}>
            Nueva novedad
          </Button>
        }
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        {canSeeGlobal && (
          <Tabs
            items={[
              { key: "mine", label: "Mías y asignadas" },
              { key: "all", label: "Todas" },
            ]}
            active={scope}
            onChange={(k) => setScope(k as typeof scope)}
          />
        )}
        <div className="flex flex-wrap gap-3">
          <div className="w-44">
            <SelectField value={status} onChange={(e) => setStatus(e.target.value as NoveltyStatus | "")}>
              <option value="">Todos los estados</option>
              {(Object.keys(noveltyStatusLabels) as NoveltyStatus[]).map((s) => (
                <option key={s} value={s}>
                  {noveltyStatusLabels[s]}
                </option>
              ))}
            </SelectField>
          </div>
          <div className="w-40">
            <SelectField value={priority} onChange={(e) => setPriority(e.target.value as NoveltyPriority | "")}>
              <option value="">Toda prioridad</option>
              {(Object.keys(noveltyPriorityLabels) as NoveltyPriority[]).map((p) => (
                <option key={p} value={p}>
                  {noveltyPriorityLabels[p]}
                </option>
              ))}
            </SelectField>
          </div>
        </div>
      </div>

      {query.isLoading ? (
        <Card>
          <LoadingState label="Cargando novedades…" />
        </Card>
      ) : query.isError ? (
        <ErrorState message="No se pudieron cargar las novedades." onRetry={() => query.refetch()} />
      ) : (
        <DataTable
          rows={query.data ?? []}
          rowKey={(row) => row.id}
          onRowClick={(row) => navigate(`/app/novelties/${row.id}`)}
          emptyTitle="Sin novedades para este filtro"
          emptyDescription="Cuando reportes o te asignen una novedad, aparecerá aquí."
          columns={[
            {
              key: "title",
              header: "Novedad",
              render: (n) => (
                <div className="flex flex-col">
                  <span className="max-w-xs truncate font-medium text-ink">{n.title}</span>
                  <span className="text-xs text-ink-muted">{n.novelty_type} · {n.area.name}</span>
                </div>
              ),
            },
            { key: "priority", header: "Prioridad", render: (n) => <NoveltyPriorityBadge priority={n.priority} /> },
            { key: "status", header: "Estado", render: (n) => <NoveltyStatusBadge status={n.status} /> },
            { key: "assigned", header: "Asignada a", render: (n) => n.assigned_user?.name ?? "Sin asignar" },
            { key: "reported_by", header: "Reportó", render: (n) => n.reported_by.name },
            { key: "reported_at", header: "Reportada", render: (n) => formatRelative(n.reported_at), align: "right" },
          ]}
        />
      )}

      <NewNoveltyModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
