import type { OperationalKpiOverviewResponse } from "@/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconBolt } from "@/components/ui/Icon";
import { formatPercent } from "@/lib/utils/format";
import { hasPunctualityData } from "@/lib/utils/kpi";

export function PunctualityCard({ kpi }: { kpi: OperationalKpiOverviewResponse }) {
  if (!hasPunctualityData(kpi)) {
    return (
      <Card className="flex flex-col gap-3">
        <span className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-ink-muted">
          <IconBolt className="text-brand-2" />
          Puntualidad
        </span>
        <span className="text-lg font-medium text-ink-secondary">Sin datos suficientes</span>
        <span className="text-xs text-ink-muted">{kpi.punctuality_reason ?? "No hay turnos evaluables aún."}</span>
      </Card>
    );
  }

  const tone = kpi.punctuality_rate >= 0.85 ? "good" : kpi.punctuality_rate >= 0.6 ? "warning" : "critical";

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-ink-muted">
          <IconBolt className="text-brand-2" />
          Puntualidad
        </span>
        <Badge tone={tone}>{kpi.late_shift_count === 0 ? "Al día" : `${kpi.late_shift_count} tarde(s)`}</Badge>
      </div>
      <span className="text-3xl font-semibold tabular-nums text-ink">{formatPercent(kpi.punctuality_rate)}</span>
      <span className="text-xs text-ink-muted">
        {kpi.punctual_shift_count}/{kpi.punctuality_evaluated_shift_count} turnos puntuales
        {kpi.average_late_by_minutes > 0 ? ` · retraso prom. ${kpi.average_late_by_minutes.toFixed(0)} min` : ""}
      </span>
    </Card>
  );
}
