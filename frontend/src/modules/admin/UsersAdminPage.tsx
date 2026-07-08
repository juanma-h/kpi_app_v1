import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listUsers, setUserStatus } from "@/lib/api/users";
import type { UserRole } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { SelectField } from "@/components/ui/Form";
import { DataTable } from "@/components/ui/DataTable";
import { ActiveBadge, RoleBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { NewUserModal } from "./NewUserModal";
import { formatDate } from "@/lib/utils/format";
import { roleLabels } from "@/lib/utils/labels";
import { IconPlus } from "@/components/ui/Icon";

export function UsersAdminPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [role, setRole] = useState<UserRole | "">("");
  const [activeFilter, setActiveFilter] = useState<"" | "true" | "false">("");
  const [modalOpen, setModalOpen] = useState(false);

  const query = useQuery({
    queryKey: ["users", role, activeFilter],
    queryFn: () =>
      listUsers({
        role: role || undefined,
        is_active: activeFilter === "" ? undefined : activeFilter === "true",
      }),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: number; isActive: boolean }) => setUserStatus(id, isActive),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Usuarios"
        subtitle="Administra empleados, supervisores y administradores del sistema."
        actions={
          <Button icon={<IconPlus />} onClick={() => setModalOpen(true)}>
            Nuevo usuario
          </Button>
        }
      />

      <Card className="flex flex-wrap gap-3">
        <div className="w-48">
          <SelectField label="Rol" value={role} onChange={(e) => setRole(e.target.value as UserRole | "")}>
            <option value="">Todos</option>
            {(Object.keys(roleLabels) as UserRole[]).map((r) => (
              <option key={r} value={r}>
                {roleLabels[r]}
              </option>
            ))}
          </SelectField>
        </div>
        <div className="w-44">
          <SelectField
            label="Estado"
            value={activeFilter}
            onChange={(e) => setActiveFilter(e.target.value as typeof activeFilter)}
          >
            <option value="">Todos</option>
            <option value="true">Activos</option>
            <option value="false">Inactivos</option>
          </SelectField>
        </div>
      </Card>

      {query.isLoading ? (
        <Card>
          <LoadingState label="Cargando usuarios…" />
        </Card>
      ) : query.isError ? (
        <ErrorState message="No se pudieron cargar los usuarios." onRetry={() => query.refetch()} />
      ) : (
        <DataTable
          rows={query.data ?? []}
          rowKey={(row) => row.id}
          onRowClick={(row) => navigate(`/app/admin/users/${row.id}`)}
          emptyTitle="Sin usuarios para este filtro"
          columns={[
            {
              key: "name",
              header: "Nombre",
              render: (u) => (
                <div className="flex flex-col">
                  <span className="font-medium text-ink">{u.name}</span>
                  <span className="text-xs text-ink-muted">{u.email}</span>
                </div>
              ),
            },
            { key: "role", header: "Rol", render: (u) => <RoleBadge role={u.role} /> },
            { key: "status", header: "Estado", render: (u) => <ActiveBadge active={u.is_active} /> },
            { key: "created", header: "Creado", render: (u) => formatDate(u.created_at), align: "right" },
            {
              key: "actions",
              header: "",
              align: "right",
              render: (u) => (
                <Button
                  variant="ghost"
                  size="sm"
                  loading={statusMutation.isPending}
                  onClick={(e) => {
                    e.stopPropagation();
                    statusMutation.mutate({ id: u.id, isActive: !u.is_active });
                  }}
                >
                  {u.is_active ? "Desactivar" : "Activar"}
                </Button>
              ),
            },
          ]}
        />
      )}

      <NewUserModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
