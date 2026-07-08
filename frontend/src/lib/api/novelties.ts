import { apiClient } from "./client";
import type {
  NoveltyCreatePayload,
  NoveltyKpiOverviewResponse,
  NoveltyLogCreatePayload,
  NoveltyLogResponse,
  NoveltyPriority,
  NoveltyResponse,
  NoveltyStatus,
  OperationalAreaResponse,
  SourceSystemResponse,
} from "@/types";

export interface NoveltyQueryParams {
  status?: NoveltyStatus;
  priority?: NoveltyPriority;
  area_id?: number;
  source_system_id?: number;
  novelty_type?: string;
  reported_from?: string;
  reported_to?: string;
  limit?: number;
  assigned_user_id?: number;
  reported_by_user_id?: number;
}

export async function listMyNovelties(params: NoveltyQueryParams = {}): Promise<NoveltyResponse[]> {
  const { data } = await apiClient.get<NoveltyResponse[]>("/novelties/me", { params });
  return data;
}

export async function listNovelties(params: NoveltyQueryParams = {}): Promise<NoveltyResponse[]> {
  const { data } = await apiClient.get<NoveltyResponse[]>("/novelties", { params });
  return data;
}

export async function getNovelty(noveltyId: number): Promise<NoveltyResponse> {
  const { data } = await apiClient.get<NoveltyResponse>(`/novelties/${noveltyId}`);
  return data;
}

export async function createNovelty(payload: NoveltyCreatePayload): Promise<NoveltyResponse> {
  const { data } = await apiClient.post<NoveltyResponse>("/novelties", payload);
  return data;
}

export async function updateNoveltyAssignment(
  noveltyId: number,
  assignedUserId: number | null,
  note?: string,
): Promise<NoveltyResponse> {
  const { data } = await apiClient.patch<NoveltyResponse>(`/novelties/${noveltyId}/assignment`, {
    assigned_user_id: assignedUserId,
    note: note ?? null,
  });
  return data;
}

export async function updateNoveltyStatus(
  noveltyId: number,
  status: NoveltyStatus,
  note?: string,
): Promise<NoveltyResponse> {
  const { data } = await apiClient.patch<NoveltyResponse>(`/novelties/${noveltyId}/status`, {
    status,
    note: note ?? null,
  });
  return data;
}

export async function listNoveltyLogs(noveltyId: number): Promise<NoveltyLogResponse[]> {
  const { data } = await apiClient.get<NoveltyLogResponse[]>(`/novelties/${noveltyId}/logs`);
  return data;
}

export async function createNoveltyLog(
  noveltyId: number,
  payload: NoveltyLogCreatePayload,
): Promise<NoveltyLogResponse> {
  const { data } = await apiClient.post<NoveltyLogResponse>(`/novelties/${noveltyId}/logs`, payload);
  return data;
}

export async function listOperationalAreas(isActive?: boolean): Promise<OperationalAreaResponse[]> {
  const { data } = await apiClient.get<OperationalAreaResponse[]>("/novelties/areas", {
    params: isActive === undefined ? {} : { is_active: isActive },
  });
  return data;
}

export async function createOperationalArea(payload: {
  code: string;
  name: string;
  description?: string | null;
  is_active: boolean;
}): Promise<OperationalAreaResponse> {
  const { data } = await apiClient.post<OperationalAreaResponse>("/novelties/areas", payload);
  return data;
}

export async function setOperationalAreaStatus(
  areaId: number,
  isActive: boolean,
): Promise<OperationalAreaResponse> {
  const { data } = await apiClient.patch<OperationalAreaResponse>(
    `/novelties/areas/${areaId}/status`,
    { is_active: isActive },
  );
  return data;
}

export async function listSourceSystems(isActive?: boolean): Promise<SourceSystemResponse[]> {
  const { data } = await apiClient.get<SourceSystemResponse[]>("/novelties/source-systems", {
    params: isActive === undefined ? {} : { is_active: isActive },
  });
  return data;
}

export async function createSourceSystem(payload: {
  code: string;
  name: string;
  description?: string | null;
  allowlist_domain_id?: number | null;
  is_active: boolean;
}): Promise<SourceSystemResponse> {
  const { data } = await apiClient.post<SourceSystemResponse>("/novelties/source-systems", payload);
  return data;
}

export async function setSourceSystemStatus(
  sourceSystemId: number,
  isActive: boolean,
): Promise<SourceSystemResponse> {
  const { data } = await apiClient.patch<SourceSystemResponse>(
    `/novelties/source-systems/${sourceSystemId}/status`,
    { is_active: isActive },
  );
  return data;
}

export async function getMyNoveltyKpis(params: {
  reported_from?: string;
  reported_to?: string;
} = {}): Promise<NoveltyKpiOverviewResponse> {
  const { data } = await apiClient.get<NoveltyKpiOverviewResponse>("/novelties/kpis/me", { params });
  return data;
}

export async function getGlobalNoveltyKpis(params: {
  reported_from?: string;
  reported_to?: string;
} = {}): Promise<NoveltyKpiOverviewResponse> {
  const { data } = await apiClient.get<NoveltyKpiOverviewResponse>("/novelties/kpis/overview", {
    params,
  });
  return data;
}

export async function getUserNoveltyKpis(
  userId: number,
  params: { reported_from?: string; reported_to?: string } = {},
): Promise<NoveltyKpiOverviewResponse> {
  const { data } = await apiClient.get<NoveltyKpiOverviewResponse>(`/novelties/kpis/users/${userId}`, {
    params,
  });
  return data;
}
