import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { addDays, format, parseISO } from "date-fns";
import { es } from "date-fns/locale";
import { getMyResolvedSchedule } from "@/lib/api/schedules";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { ScheduleResolutionCard } from "./ScheduleResolutionCard";
import { formatDate, todayIsoDate } from "@/lib/utils/format";

export function MySchedulePage() {
  const [targetDate, setTargetDate] = useState(todayIsoDate());

  const query = useQuery({
    queryKey: ["schedule", "me", targetDate],
    queryFn: () => getMyResolvedSchedule(targetDate),
  });

  function shiftDay(delta: number) {
    const next = addDays(parseISO(targetDate), delta);
    setTargetDate(format(next, "yyyy-MM-dd"));
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Mi horario"
        subtitle="Consulta tu horario esperado por día."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => shiftDay(-1)}>
              ← Anterior
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setTargetDate(todayIsoDate())}>
              Hoy
            </Button>
            <Button variant="secondary" size="sm" onClick={() => shiftDay(1)}>
              Siguiente →
            </Button>
          </div>
        }
      />

      <p className="-mt-3 text-sm capitalize text-ink-muted">
        {format(parseISO(targetDate), "EEEE d 'de' MMMM yyyy", { locale: es })}
      </p>

      {query.isLoading ? (
        <Card>
          <LoadingState label="Consultando horario…" />
        </Card>
      ) : query.isError ? (
        <ErrorState message="No se pudo cargar tu horario para esta fecha." onRetry={() => query.refetch()} />
      ) : query.data ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <ScheduleResolutionCard resolution={query.data} />
          <Card className="flex flex-col gap-2">
            <h3 className="text-sm font-semibold text-ink">Vigencia de la asignación</h3>
            <dl className="mt-2 grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-xs text-ink-muted">Desde</dt>
                <dd className="text-ink-secondary">{formatDate(query.data.effective_from)}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-muted">Hasta</dt>
                <dd className="text-ink-secondary">{query.data.effective_to ? formatDate(query.data.effective_to) : "Indefinido"}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-muted">Zona horaria</dt>
                <dd className="text-ink-secondary">{query.data.timezone_name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-muted">Notas</dt>
                <dd className="text-ink-secondary">{query.data.notes ?? "—"}</dd>
              </div>
            </dl>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
