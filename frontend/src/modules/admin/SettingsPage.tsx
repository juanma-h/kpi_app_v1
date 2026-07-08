import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createOperationalArea,
  createSourceSystem,
  listOperationalAreas,
  listSourceSystems,
  setOperationalAreaStatus,
  setSourceSystemStatus,
} from "@/lib/api/novelties";
import { listAllowlistDomains } from "@/lib/api/allowlist";
import { extractErrorMessage } from "@/lib/api/client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { Tabs } from "@/components/ui/Tabs";
import { DataTable } from "@/components/ui/DataTable";
import { ActiveBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { InputField, SelectField } from "@/components/ui/Form";
import { IconPlus } from "@/components/ui/Icon";

export function SettingsPage() {
  const [tab, setTab] = useState<"areas" | "sources">("areas");
  const [modalOpen, setModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const areasQuery = useQuery({ queryKey: ["novelties", "areas", "all"], queryFn: () => listOperationalAreas() });
  const sourcesQuery = useQuery({ queryKey: ["novelties", "source-systems", "all"], queryFn: () => listSourceSystems() });

  const areaStatusMutation = useMutation({
    mutationFn: (vars: { id: number; isActive: boolean }) => setOperationalAreaStatus(vars.id, vars.isActive),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["novelties", "areas"] }),
  });
  const sourceStatusMutation = useMutation({
    mutationFn: (vars: { id: number; isActive: boolean }) => setSourceSystemStatus(vars.id, vars.isActive),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["novelties", "source-systems"] }),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Catálogos operativos"
        subtitle="Áreas y sistemas fuente usados para clasificar novedades."
        actions={
          <div className="flex items-center gap-2">
            <Tabs
              items={[
                { key: "areas", label: "Áreas" },
                { key: "sources", label: "Sistemas fuente" },
              ]}
              active={tab}
              onChange={(k) => setTab(k as typeof tab)}
            />
            <Button icon={<IconPlus />} onClick={() => setModalOpen(true)}>
              Nuevo
            </Button>
          </div>
        }
      />

      {tab === "areas" ? (
        areasQuery.isLoading ? (
          <Card>
            <LoadingState label="Cargando áreas…" />
          </Card>
        ) : areasQuery.isError ? (
          <ErrorState onRetry={() => areasQuery.refetch()} />
        ) : (
          <DataTable
            rows={areasQuery.data ?? []}
            rowKey={(row) => row.id}
            emptyTitle="Sin áreas operativas"
            columns={[
              { key: "code", header: "Código", render: (a) => a.code },
              { key: "name", header: "Nombre", render: (a) => a.name },
              { key: "description", header: "Descripción", render: (a) => a.description ?? "—" },
              { key: "status", header: "Estado", render: (a) => <ActiveBadge active={a.is_active} /> },
              {
                key: "actions",
                header: "",
                align: "right",
                render: (a) => (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => areaStatusMutation.mutate({ id: a.id, isActive: !a.is_active })}
                  >
                    {a.is_active ? "Desactivar" : "Activar"}
                  </Button>
                ),
              },
            ]}
          />
        )
      ) : sourcesQuery.isLoading ? (
        <Card>
          <LoadingState label="Cargando sistemas fuente…" />
        </Card>
      ) : sourcesQuery.isError ? (
        <ErrorState onRetry={() => sourcesQuery.refetch()} />
      ) : (
        <DataTable
          rows={sourcesQuery.data ?? []}
          rowKey={(row) => row.id}
          emptyTitle="Sin sistemas fuente"
          columns={[
            { key: "code", header: "Código", render: (s) => s.code },
            { key: "name", header: "Nombre", render: (s) => s.name },
            { key: "domain", header: "Dominio vinculado", render: (s) => s.allowlist_domain?.domain ?? "—" },
            { key: "status", header: "Estado", render: (s) => <ActiveBadge active={s.is_active} /> },
            {
              key: "actions",
              header: "",
              align: "right",
              render: (s) => (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => sourceStatusMutation.mutate({ id: s.id, isActive: !s.is_active })}
                >
                  {s.is_active ? "Desactivar" : "Activar"}
                </Button>
              ),
            },
          ]}
        />
      )}

      {tab === "areas" ? (
        <NewAreaModal open={modalOpen} onClose={() => setModalOpen(false)} />
      ) : (
        <NewSourceSystemModal open={modalOpen} onClose={() => setModalOpen(false)} />
      )}
    </div>
  );
}

function NewAreaModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ code: "", name: "", description: "" });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createOperationalArea({
        code: form.code,
        name: form.name,
        description: form.description || undefined,
        is_active: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["novelties", "areas"] });
      setForm({ code: "", name: "", description: "" });
      onClose();
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear el área.")),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Modal open={open} onClose={onClose} title="Nueva área operativa">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <InputField
          label="Código"
          required
          minLength={2}
          placeholder="LOGISTICA"
          value={form.code}
          onChange={(e) => setForm({ ...form, code: e.target.value })}
        />
        <InputField label="Nombre" required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <InputField label="Descripción" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        {error && <p className="text-sm text-critical">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Crear área
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function NewSourceSystemModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const domainsQuery = useQuery({ queryKey: ["allowlist"], queryFn: listAllowlistDomains, enabled: open });
  const [form, setForm] = useState({ code: "", name: "", description: "", allowlist_domain_id: "" });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createSourceSystem({
        code: form.code,
        name: form.name,
        description: form.description || undefined,
        allowlist_domain_id: form.allowlist_domain_id ? Number(form.allowlist_domain_id) : undefined,
        is_active: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["novelties", "source-systems"] });
      setForm({ code: "", name: "", description: "", allowlist_domain_id: "" });
      onClose();
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear el sistema fuente.")),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo sistema fuente">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <InputField
          label="Código"
          required
          minLength={2}
          placeholder="VENDELO"
          value={form.code}
          onChange={(e) => setForm({ ...form, code: e.target.value })}
        />
        <InputField label="Nombre" required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <SelectField
          label="Dominio vinculado (opcional)"
          value={form.allowlist_domain_id}
          onChange={(e) => setForm({ ...form, allowlist_domain_id: e.target.value })}
        >
          <option value="">Sin vincular</option>
          {domainsQuery.data?.map((d) => (
            <option key={d.id} value={d.id}>
              {d.domain}
            </option>
          ))}
        </SelectField>
        <InputField label="Descripción" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        {error && <p className="text-sm text-critical">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Crear sistema
          </Button>
        </div>
      </form>
    </Modal>
  );
}
