import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createUser } from "@/lib/api/users";
import { extractErrorMessage } from "@/lib/api/client";
import type { UserRole } from "@/types";
import { Modal } from "@/components/ui/Modal";
import { InputField, SelectField } from "@/components/ui/Form";
import { Button } from "@/components/ui/Button";
import { roleLabels } from "@/lib/utils/labels";

export function NewUserModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "EMPLOYEE" as UserRole });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => createUser({ ...form, is_active: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setForm({ name: "", email: "", password: "", role: "EMPLOYEE" });
      onClose();
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear el usuario.")),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo usuario">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <InputField
          label="Nombre completo"
          required
          minLength={2}
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <InputField
          label="Correo"
          type="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <InputField
          label="Contraseña temporal"
          type="password"
          required
          minLength={8}
          hint="Mínimo 8 caracteres."
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <SelectField label="Rol" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as UserRole })}>
          {(Object.keys(roleLabels) as UserRole[]).map((role) => (
            <option key={role} value={role}>
              {roleLabels[role]}
            </option>
          ))}
        </SelectField>

        {error && <p className="text-sm text-critical">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Crear usuario
          </Button>
        </div>
      </form>
    </Modal>
  );
}
