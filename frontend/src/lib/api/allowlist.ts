import { apiClient } from "./client";
import type { AllowlistDomainCreatePayload, AllowlistDomainResponse } from "@/types";

export async function listAllowlistDomains(): Promise<AllowlistDomainResponse[]> {
  const { data } = await apiClient.get<AllowlistDomainResponse[]>("/allowlist/domains");
  return data;
}

export async function createAllowlistDomain(
  payload: AllowlistDomainCreatePayload,
): Promise<AllowlistDomainResponse> {
  const { data } = await apiClient.post<AllowlistDomainResponse>("/allowlist/domains", payload);
  return data;
}

export async function setAllowlistDomainStatus(
  domainId: number,
  isActive: boolean,
): Promise<AllowlistDomainResponse> {
  const { data } = await apiClient.patch<AllowlistDomainResponse>(
    `/allowlist/domains/${domainId}/status`,
    { is_active: isActive },
  );
  return data;
}
