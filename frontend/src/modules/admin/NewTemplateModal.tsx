import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createScheduleTemplate } from "@/lib/api/schedules";
import { extractErrorMessage } from "@/lib/api/client";
import type { Weekday } from "@/types";
import { Modal } from "@/components/ui/Modal";
import { InputField, SelectField } from "@/components/ui/Form";
import { Button } from "@/components/ui/Button";
import { IconPlus, IconX } from "@/components/ui/Icon";
import { weekdayLabels, WEEKDAY_ORDER } from "@/lib/utils/labels";

interface SlotDraft {
  weekday: Weekday;
  start_time: string;
  end_time: string;
}

export function NewTemplateModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [timezone, setTimezone] = useState("America/Bogota");
  const [graceMinutes, setGraceMinutes] = useState(10);
  const [slots, setSlots] = useState<SlotDraft[]>([{ weekday: "MONDAY", start_time: "08:00", end_time: "17:00" }]);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createScheduleTemplate({
        name,
        description: description || undefined,
        timezone_name: timezone,
        grace_minutes: graceMinutes,
        is_active: true,
        slots,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules", "templates"] });
      setName("");
      setDescription("");
      setSlots([{ weekday: "MONDAY", start_time: "08:00", end_time: "17:00" }]);
      onClose();
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo crear la plantilla.")),
  });

  function updateSlot(idx: number, patch: Partial<SlotDraft>) {
    setSlots((prev) => prev.map((s, i) => (i === idx ? { ...s, ...patch } : s)));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Modal open={open} onClose={onClose} title="Nueva plantilla de horario" width="max-w-2xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <InputField label="Nombre" required minLength={2} value={name} onChange={(e) => setName(e.target.value)} />
          <InputField
            label="Zona horaria"
            required
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            hint="Ej. America/Bogota"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <InputField
            label="Descripción"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <InputField
            label="Tolerancia (minutos)"
            type="number"
            min={0}
            max={180}
            value={graceMinutes}
            onChange={(e) => setGraceMinutes(Number(e.target.value))}
          />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-ink-secondary">Franjas horarias</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              icon={<IconPlus />}
              onClick={() => setSlots((prev) => [...prev, { weekday: "MONDAY", start_time: "08:00", end_time: "17:00" }])}
            >
              Agregar franja
            </Button>
          </div>
          <div className="flex flex-col gap-2">
            {slots.map((slot, idx) => (
              <div key={idx} className="flex items-center gap-2 rounded-lg border border-(--color-border) p-2">
                <div className="flex-1">
                  <SelectField value={slot.weekday} onChange={(e) => updateSlot(idx, { weekday: e.target.value as Weekday })}>
                    {WEEKDAY_ORDER.map((day) => (
                      <option key={day} value={day}>
                        {weekdayLabels[day]}
                      </option>
                    ))}
                  </SelectField>
                </div>
                <input
                  type="time"
                  value={slot.start_time}
                  onChange={(e) => updateSlot(idx, { start_time: e.target.value })}
                  className="rounded-lg border border-(--color-border-strong) bg-white/[0.03] px-2 py-2 text-sm text-ink"
                />
                <span className="text-ink-muted">–</span>
                <input
                  type="time"
                  value={slot.end_time}
                  onChange={(e) => updateSlot(idx, { end_time: e.target.value })}
                  className="rounded-lg border border-(--color-border-strong) bg-white/[0.03] px-2 py-2 text-sm text-ink"
                />
                <button
                  type="button"
                  onClick={() => setSlots((prev) => prev.filter((_, i) => i !== idx))}
                  className="rounded-lg p-2 text-ink-muted hover:bg-white/5 hover:text-critical"
                  disabled={slots.length <= 1}
                >
                  <IconX />
                </button>
              </div>
            ))}
          </div>
        </div>

        {error && <p className="text-sm text-critical">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Crear plantilla
          </Button>
        </div>
      </form>
    </Modal>
  );
}
