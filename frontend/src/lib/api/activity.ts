import { apiClient } from "./client";
import type { ActivityEventResponse, ActivityEventType } from "@/types";

export interface ActivityQueryParams {
  user_id?: number;
  shift_id?: number;
  session_id?: number;
  allowlist_domain_id?: number;
  event_type?: ActivityEventType;
  occurred_from?: string;
  occurred_to?: string;
  limit?: number;
}

export async function listMyActivityEvents(
  params: Omit<ActivityQueryParams, "user_id" | "shift_id" | "session_id"> = {},
): Promise<ActivityEventResponse[]> {
  const { data } = await apiClient.get<ActivityEventResponse[]>("/activity/events/me", { params });
  return data;
}

export async function listActivityEvents(params: ActivityQueryParams = {}): Promise<ActivityEventResponse[]> {
  const { data } = await apiClient.get<ActivityEventResponse[]>("/activity/events", { params });
  return data;
}
