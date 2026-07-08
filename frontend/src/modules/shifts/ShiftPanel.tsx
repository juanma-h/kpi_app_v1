import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { endShift, getCurrentShift, startShift } from "@/lib/api/shifts";
import { extractErrorMessage } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ShiftStatusBadge } from "@/components/ui/Badge";
import { LoadingState } from "@/components/ui/States";
import { formatDuration, formatTime } from "@/lib/utils/format";
import { IconClock } from "@/components/ui/Icon";

export function ShiftPanel({ compact = false }: { compact?: boolean }) {
  const queryClient = useQueryClient();
  const [now, setNow] = useState(() => Date.now());
  const [error, setError] = useState<string | null>(null);

  const shiftQuery = useQuery({ queryKey: ["shift", "current"], queryFn: getCurrentShift });

  useEffect(() => {
    if (shiftQuery.data?.status !== "OPEN") return;
    const id = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(id);
  }, [shiftQuery.data?.status]);

  const startMutation = useMutation({
    mutationFn: () => startShift(),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["shift", "current"] });
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo iniciar el turno.")),
  });

  const endMutation = useMutation({
    mutationFn: () => endShift(),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["shift", "current"] });
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
    },
    onError: (err) => setError(extractErrorMessage(err, "No se pudo cerrar el turno.")),
  });

  if (shiftQuery.isLoading) {
    return (
      <Card>
        <LoadingState label="Consultando tu turno…" />
      </Card>
    );
  }

  const shift = shiftQuery.data;
  const elapsedSeconds = shift ? Math.max(0, Math.floor((now - new Date(shift.start_at).getTime()) / 1000)) : 0;

  return (
    <Card className={compact ? "" : "gap-4"}>
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-ink-muted">
          <IconClock className="text-brand-2" />
          Turno actual
        </span>
        <ShiftStatusBadge status={shift ? "OPEN" : "CLOSED"} />
      </div>

      {shift ? (
        <div className="mt-3 flex flex-col gap-1">
          <span className="text-3xl font-semibold tabular-nums text-ink">{formatDuration(elapsedSeconds)}</span>
          <span className="text-xs text-ink-muted">Iniciado a las {formatTime(shift.start_at)}</span>
        </div>
      ) : (
        <div className="mt-3 flex flex-col gap-1">
          <span className="text-sm text-ink-secondary">No tienes un turno abierto en este momento.</span>
        </div>
      )}

      {error && <p className="mt-2 text-xs text-critical">{error}</p>}

      <div className="mt-4">
        {shift ? (
          <Button
            variant="danger"
            size="sm"
            loading={endMutation.isPending}
            onClick={() => endMutation.mutate()}
            className="w-full"
          >
            Cerrar turno
          </Button>
        ) : (
          <Button
            size="sm"
            loading={startMutation.isPending}
            onClick={() => startMutation.mutate()}
            className="w-full"
          >
            Iniciar turno
          </Button>
        )}
      </div>
    </Card>
  );
}
