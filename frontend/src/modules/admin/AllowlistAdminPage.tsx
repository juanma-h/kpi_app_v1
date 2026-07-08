import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createAllowlistDomain, listAllowlistDomains, setAllowlistDomainStatus } from "@/lib/api/allowlist";
import { extractErrorMessage } from "@/lib/api/client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { DataTable } from "@/components/ui/DataTable";
import { ActiveBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { InputField } from "@/components/ui/Form";
import { formatDate } from "@/lib/utils/format";
import { IconPlus } from "@/components/ui/Icon";

export function AllowlistAdminPage() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ domain: "", description: "" });
  const [error, setError] = useState<string | null>(null);

  const query = useQuery({ queryKey: ["allowlist"], queryFn: listAllowlistDomains });

  const createMutation = useMutation({
    mutationFn: () => createAllowlistDomain({ domain: form.domain, description: form.description || undefined }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allowlist"] });
      setForm({ domain: "", description: "" });
      setModalOpen(false);
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear el dominio.")),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: number; isActive: boolean }) => setAllowlistDomainStatus(id, isActive),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["allowlist"] }),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    createMutation.mutate();
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Dominios permitidos"
        subtitle="Controla qué dominios pueden capturar actividad del cliente web."
        actions={
          <Button icon={<IconPlus />} onClick={() => setModalOpen(true)}>
            Nuevo dominio
          </Button>
        }
      />

      {query.isLoading ? (
        <Card>
          <LoadingState label="Cargando dominios…" />
        </Card>
      ) : query.isError ? (
        <ErrorState message="No se pudieron cargar los dominios." onRetry={() => query.refetch()} />
      ) : (
        <DataTable
          rows={query.data ?? []}
          rowKey={(row) => row.id}
          emptyTitle="Sin dominios registrados"
          columns={[
            { key: "domain", header: "Dominio", render: (d) => <span className="font-medium text-ink">{d.domain}</span> },
            { key: "description", header: "Descripción", render: (d) => d.description ?? "—" },
            { key: "status", header: "Estado", render: (d) => <ActiveBadge active={d.is_active} /> },
            { key: "created", header: "Creado", render: (d) => formatDate(d.created_at), align: "right" },
            {
              key: "actions",
              header: "",
              align: "right",
              render: (d) => (
                <Button
                  variant="ghost"
                  size="sm"
                  loading={statusMutation.isPending}
                  onClick={() => statusMutation.mutate({ id: d.id, isActive: !d.is_active })}
                >
                  {d.is_active ? "Desactivar" : "Activar"}
                </Button>
              ),
            },
          ]}
        />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Nuevo dominio permitido">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <InputField
            label="Dominio"
            required
            placeholder="ejemplo.com"
            value={form.domain}
            onChange={(e) => setForm({ ...form, domain: e.target.value })}
          />
          <InputField
            label="Descripción"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          {error && <p className="text-sm text-critical">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" loading={createMutation.isPending}>
              Crear dominio
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
