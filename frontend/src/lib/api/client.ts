import axios, { AxiosError } from "axios";
import type { ApiErrorBody } from "@/types";

export const TOKEN_STORAGE_KEY = "nexusops.token";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

const UNAUTHORIZED_EVENT = "nexusops:unauthorized";

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      window.dispatchEvent(new CustomEvent(UNAUTHORIZED_EVENT));
    }
    return Promise.reject(error);
  },
);

export function onUnauthorized(handler: () => void): () => void {
  window.addEventListener(UNAUTHORIZED_EVENT, handler);
  return () => window.removeEventListener(UNAUTHORIZED_EVENT, handler);
}

export function extractErrorMessage(error: unknown, fallback = "Ocurrió un error inesperado."): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "No se pudo conectar con el servidor. Verifica tu conexión.";
    }
    const body = error.response.data as ApiErrorBody | undefined;
    const detail = body?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const first = detail[0];
      if (typeof first === "string") return first;
      if (first && typeof first === "object" && "msg" in first) return first.msg;
    }
    if (error.response.status === 404) return "No se encontró el recurso solicitado.";
    if (error.response.status === 403) return "No tienes permisos para esta acción.";
    return fallback;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
