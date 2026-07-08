import type {
  ActivityEventType,
  NoveltyLogType,
  NoveltyPriority,
  NoveltyStatus,
  ShiftStatus,
  UserRole,
  Weekday,
} from "@/types";

export const roleLabels: Record<UserRole, string> = {
  ADMIN: "Administrador",
  SUPERVISOR: "Supervisor",
  EMPLOYEE: "Empleado",
};

export const shiftStatusLabels: Record<ShiftStatus, string> = {
  OPEN: "Turno activo",
  CLOSED: "Turno cerrado",
};

export const activityEventLabels: Record<ActivityEventType, string> = {
  PAGE_VIEW: "Vista de página",
  HEARTBEAT: "Actividad",
  IDLE: "Inactividad",
  RESUME: "Reanudación",
};

export const weekdayLabels: Record<Weekday, string> = {
  MONDAY: "Lunes",
  TUESDAY: "Martes",
  WEDNESDAY: "Miércoles",
  THURSDAY: "Jueves",
  FRIDAY: "Viernes",
  SATURDAY: "Sábado",
  SUNDAY: "Domingo",
};

export const weekdayShort: Record<Weekday, string> = {
  MONDAY: "Lun",
  TUESDAY: "Mar",
  WEDNESDAY: "Mié",
  THURSDAY: "Jue",
  FRIDAY: "Vie",
  SATURDAY: "Sáb",
  SUNDAY: "Dom",
};

export const noveltyPriorityLabels: Record<NoveltyPriority, string> = {
  LOW: "Baja",
  MEDIUM: "Media",
  HIGH: "Alta",
  CRITICAL: "Crítica",
};

export const noveltyStatusLabels: Record<NoveltyStatus, string> = {
  OPEN: "Abierta",
  IN_PROGRESS: "En progreso",
  BLOCKED: "Bloqueada",
  RESOLVED: "Resuelta",
  CLOSED: "Cerrada",
};

export const noveltyLogTypeLabels: Record<NoveltyLogType, string> = {
  DAILY_UPDATE: "Avance diario",
  STATUS_CHANGE: "Cambio de estado",
  ASSIGNMENT: "Asignación",
  COMMENT: "Comentario",
  RESOLUTION: "Resolución",
};

export const NOVELTY_STATUS_ORDER: NoveltyStatus[] = [
  "OPEN",
  "IN_PROGRESS",
  "BLOCKED",
  "RESOLVED",
  "CLOSED",
];

export const WEEKDAY_ORDER: Weekday[] = [
  "MONDAY",
  "TUESDAY",
  "WEDNESDAY",
  "THURSDAY",
  "FRIDAY",
  "SATURDAY",
  "SUNDAY",
];
