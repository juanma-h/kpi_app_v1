import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createScheduleAssignment, listScheduleTemplates } from "@/lib/api/schedules";
import { listUsers } from "@/lib/api/users";
import { extractErrorMessage } from "@/lib/api/client";
import { Modal } from "@/components/ui/Modal";
import { InputField, SelectField } from "@/components/ui/Form";
import { Button } from "@/components/ui/Button";
import { todayIsoDate } from "@/lib/utils/format";

export function NewAssignmentModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const usersQuery = useQuery({ queryKey: ["users", "active"], queryFn: () => listUsers({ is_active: true }), enabled: open });
  const templatesQuery = useQuery({
    queryKey: ["schedules", "templates", true],
    queryFn: () => listScheduleTemplates(true),
    enabled: open,
  });

  const [form, setForm] = useState({ user_id: "", schedule_template_id: "", effective_from: todayIsoDate(), notes: "" });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createScheduleAssignment({
        user_id: Number(form.user_id),
        schedule_template_id: Number(form.schedule_template_id),
        effective_from: form.effective_from,
        notes: form.notes || undefined,
        is_active: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules", "assignments"] });
      setForm({ user_id: "", schedule_template_id: "", effective_from: todayIsoDate(), notes: "" });
      onClose();
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear la asignación.")),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Modal open={open} onClose={onClose} title="Nueva asignación de horario">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <SelectField label="Empleado" required value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })}>
          <option value="">Selecciona un empleado</option>
          {usersQuery.data?.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name}
            </option>
          ))}
        </SelectField>
        <SelectField
          label="Plantilla"
          required
          value={form.schedule_template_id}
          onChange={(e) => setForm({ ...form, schedule_template_id: e.target.value })}
        >
          <option value="">Selecciona una plantilla</option>
          {templatesQuery.data?.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </SelectField>
        <InputField
          label="Vigente desde"
          type="date"
          required
          value={form.effective_from}
          onChange={(e) => setForm({ ...form, effective_from: e.target.value })}
        />
        <InputField label="Notas" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />

        {error && <p className="text-sm text-critical">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Crear asignación
          </Button>
        </div>
      </form>
    </Modal>
  );
}
