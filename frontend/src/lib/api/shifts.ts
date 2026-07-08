import { apiClient } from "./client";
import type { ShiftResponse } from "@/types";

export async function getCurrentShift(): Promise<ShiftResponse | null> {
  try {
    const { data } = await apiClient.get<ShiftResponse>("/shifts/current");
    return data;
  } catch (error) {
    if (isNotFound(error)) return null;
    throw error;
  }
}

export async function startShift(deviceLabel?: string): Promise<ShiftResponse> {
  const { data } = await apiClient.post<ShiftResponse>("/shifts/start", {
    device_label: deviceLabel ?? null,
  });
  return data;
}

export async function endShift(): Promise<ShiftResponse> {
  const { data } = await apiClient.post<ShiftResponse>("/shifts/end");
  return data;
}

function isNotFound(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    (error as { response?: { status?: number } }).response?.status === 404
  );
}
