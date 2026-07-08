import { apiClient } from "./client";
import type { OperationalKpiOverviewResponse, ShiftKpiResponse } from "@/types";

export interface KpiRangeParams {
  started_from?: string;
  started_to?: string;
  limit?: number;
}

export async function getMyKpiOverview(params: KpiRangeParams = {}): Promise<OperationalKpiOverviewResponse> {
  const { data } = await apiClient.get<OperationalKpiOverviewResponse>("/kpis/me/overview", { params });
  return data;
}

export async function getGlobalKpiOverview(
  params: KpiRangeParams = {},
): Promise<OperationalKpiOverviewResponse> {
  const { data } = await apiClient.get<OperationalKpiOverviewResponse>("/kpis/overview", { params });
  return data;
}

export async function getUserKpiOverview(
  userId: number,
  params: KpiRangeParams = {},
): Promise<OperationalKpiOverviewResponse> {
  const { data } = await apiClient.get<OperationalKpiOverviewResponse>(
    `/kpis/users/${userId}/overview`,
    { params },
  );
  return data;
}

export async function getShiftKpiOverview(shiftId: number): Promise<ShiftKpiResponse> {
  const { data } = await apiClient.get<ShiftKpiResponse>(`/kpis/shifts/${shiftId}`);
  return data;
}
