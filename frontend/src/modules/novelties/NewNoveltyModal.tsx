import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createNovelty, listOperationalAreas, listSourceSystems } from "@/lib/api/novelties";
import { extractErrorMessage } from "@/lib/api/client";
import type { NoveltyPriority } from "@/types";
import { Modal } from "@/components/ui/Modal";
import { InputField, SelectField, TextareaField } from "@/components/ui/Form";
import { Button } from "@/components/ui/Button";
import { noveltyPriorityLabels } from "@/lib/utils/labels";

export function NewNoveltyModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const areasQuery = useQuery({ queryKey: ["novelties", "areas", true], queryFn: () => listOperationalAreas(true), enabled: open });
  const sourcesQuery = useQuery({
    queryKey: ["novelties", "source-systems", true],
    queryFn: () => listSourceSystems(true),
    enabled: open,
  });

  const [form, setForm] = useState({
    area_id: "",
    source_system_id: "",
    title: "",
    description: "",
    novelty_type: "",
    priority: "MEDIUM" as NoveltyPriority,
    order_reference: "",
    external_reference: "",
  });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createNovelty({
        area_id: Number(form.area_id),
        source_system_id: Number(form.source_system_id),
        title: form.title,
        description: form.description,
        novelty_type: form.novelty_type,
        priority: form.priority,
        order_reference: form.order_reference || undefined,
        external_reference: form.external_reference || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["novelties"] });
      setForm({
        area_id: "",
        source_system_id: "",
        title: "",
        description: "",
        novelty_type: "",
        priority: "MEDIUM",
        order_reference: "",
        external_reference: "",
      });
      onClose();
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear la novedad.")),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Modal open={open} onClose={onClose} title="Reportar novedad" width="max-w-xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <SelectField
            label="Área operativa"
            required
            value={form.area_id}
            onChange={(e) => setForm({ ...form, area_id: e.target.value })}
          >
            <option value="">Selecciona un área</option>
            {areasQuery.data?.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Sistema origen"
            required
            value={form.source_system_id}
            onChange={(e) => setForm({ ...form, source_system_id: e.target.value })}
          >
            <option value="">Selecciona un sistema</option>
            {sourcesQuery.data?.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </SelectField>
        </div>

        <InputField
          label="Título"
          required
          minLength={5}
          maxLength={160}
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          placeholder="Resumen breve del caso"
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <InputField
            label="Tipo de novedad"
            required
            value={form.novelty_type}
            onChange={(e) => setForm({ ...form, novelty_type: e.target.value })}
            placeholder="p. ej. pedido_retrasado"
          />
          <SelectField
            label="Prioridad"
            value={form.priority}
            onChange={(e) => setForm({ ...form, priority: e.target.value as NoveltyPriority })}
          >
            {(Object.keys(noveltyPriorityLabels) as NoveltyPriority[]).map((p) => (
              <option key={p} value={p}>
                {noveltyPriorityLabels[p]}
              </option>
            ))}
          </SelectField>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <InputField
            label="Referencia de pedido"
            value={form.order_reference}
            onChange={(e) => setForm({ ...form, order_reference: e.target.value })}
          />
          <InputField
            label="Referencia externa"
            value={form.external_reference}
            onChange={(e) => setForm({ ...form, external_reference: e.target.value })}
          />
        </div>

        <TextareaField
          label="Descripción"
          required
          minLength={10}
          maxLength={4000}
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          placeholder="Detalla qué ocurrió y qué se necesita resolver"
        />

        {error && <p className="text-sm text-critical">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Crear novedad
          </Button>
        </div>
      </form>
    </Modal>
  );
}
