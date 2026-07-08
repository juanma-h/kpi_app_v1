import { apiClient } from "./client";
import type { UserCreatePayload, UserResponse, UserRole, UserUpdatePayload } from "@/types";

export interface ListUsersParams {
  is_active?: boolean;
  role?: UserRole;
}

export async function listUsers(params: ListUsersParams = {}): Promise<UserResponse[]> {
  const { data } = await apiClient.get<UserResponse[]>("/users", { params });
  return data;
}

export async function getUser(userId: number): Promise<UserResponse> {
  const { data } = await apiClient.get<UserResponse>(`/users/${userId}`);
  return data;
}

export async function createUser(payload: UserCreatePayload): Promise<UserResponse> {
  const { data } = await apiClient.post<UserResponse>("/users", payload);
  return data;
}

export async function updateUser(userId: number, payload: UserUpdatePayload): Promise<UserResponse> {
  const { data } = await apiClient.patch<UserResponse>(`/users/${userId}`, payload);
  return data;
}

export async function setUserStatus(userId: number, isActive: boolean): Promise<UserResponse> {
  const { data } = await apiClient.patch<UserResponse>(`/users/${userId}/status`, {
    is_active: isActive,
  });
  return data;
}
