import { apiClient } from "./client";
import type {
  ScheduleAssignmentCreatePayload,
  ScheduleAssignmentResponse,
  ScheduleResolutionResponse,
  ScheduleTemplateCreatePayload,
  ScheduleTemplateResponse,
} from "@/types";

export async function listScheduleTemplates(isActive?: boolean): Promise<ScheduleTemplateResponse[]> {
  const { data } = await apiClient.get<ScheduleTemplateResponse[]>("/schedules/templates", {
    params: isActive === undefined ? {} : { is_active: isActive },
  });
  return data;
}

export async function createScheduleTemplate(
  payload: ScheduleTemplateCreatePayload,
): Promise<ScheduleTemplateResponse> {
  const { data } = await apiClient.post<ScheduleTemplateResponse>("/schedules/templates", payload);
  return data;
}

export async function setScheduleTemplateStatus(
  templateId: number,
  isActive: boolean,
): Promise<ScheduleTemplateResponse> {
  const { data } = await apiClient.patch<ScheduleTemplateResponse>(
    `/schedules/templates/${templateId}/status`,
    { is_active: isActive },
  );
  return data;
}

export async function listScheduleAssignments(params: {
  user_id?: number;
  is_active?: boolean;
} = {}): Promise<ScheduleAssignmentResponse[]> {
  const { data } = await apiClient.get<ScheduleAssignmentResponse[]>("/schedules/assignments", {
    params,
  });
  return data;
}

export async function createScheduleAssignment(
  payload: ScheduleAssignmentCreatePayload,
): Promise<ScheduleAssignmentResponse> {
  const { data } = await apiClient.post<ScheduleAssignmentResponse>(
    "/schedules/assignments",
    payload,
  );
  return data;
}

export async function getMyResolvedSchedule(targetDate?: string): Promise<ScheduleResolutionResponse> {
  const { data } = await apiClient.get<ScheduleResolutionResponse>("/schedules/me/resolved", {
    params: targetDate ? { target_date: targetDate } : {},
  });
  return data;
}

export async function getUserResolvedSchedule(
  userId: number,
  targetDate?: string,
): Promise<ScheduleResolutionResponse> {
  const { data } = await apiClient.get<ScheduleResolutionResponse>(
    `/schedules/users/${userId}/resolved`,
    { params: targetDate ? { target_date: targetDate } : {} },
  );
  return data;
}
