import type { OperationalKpiOverviewResponse } from "@/types";

export function hasPunctualityData(kpi: Pick<OperationalKpiOverviewResponse, "punctuality_supported" | "punctuality_evaluated_shift_count">): boolean {
  return kpi.punctuality_supported && kpi.punctuality_evaluated_shift_count > 0;
}
