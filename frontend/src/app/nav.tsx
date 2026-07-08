import type { ComponentType } from "react";
import type { UserRole } from "@/types";
import {
  IconActivity,
  IconAlert,
  IconBuilding,
  IconCalendar,
  IconChart,
  IconGlobe,
  IconGrid,
  IconTeam,
  IconUsers,
} from "@/components/ui/Icon";

export interface NavItem {
  to: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
  roles: UserRole[];
  end?: boolean;
}

export const NAV_SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: "Mi día",
    items: [
      { to: "/app/dashboard", label: "Dashboard", icon: IconGrid, roles: ["ADMIN", "SUPERVISOR", "EMPLOYEE"], end: true },
      { to: "/app/shift", label: "Mi turno", icon: IconChart, roles: ["EMPLOYEE"] },
      { to: "/app/schedule", label: "Mi horario", icon: IconCalendar, roles: ["EMPLOYEE"] },
      { to: "/app/activity", label: "Mi actividad", icon: IconActivity, roles: ["EMPLOYEE"] },
      { to: "/app/kpis/me", label: "Mis KPIs", icon: IconChart, roles: ["EMPLOYEE"] },
      { to: "/app/novelties", label: "Novedades", icon: IconAlert, roles: ["EMPLOYEE"] },
    ],
  },
  {
    title: "Supervisión",
    items: [
      { to: "/app/team/overview", label: "Equipo hoy", icon: IconTeam, roles: ["SUPERVISOR", "ADMIN"] },
      { to: "/app/team/kpis", label: "KPIs del equipo", icon: IconChart, roles: ["SUPERVISOR", "ADMIN"] },
      { to: "/app/team/shifts", label: "Turnos de hoy", icon: IconChart, roles: ["SUPERVISOR", "ADMIN"] },
      { to: "/app/team/activity", label: "Actividad del equipo", icon: IconActivity, roles: ["SUPERVISOR", "ADMIN"] },
      { to: "/app/team/schedules", label: "Horarios", icon: IconCalendar, roles: ["SUPERVISOR", "ADMIN"] },
      { to: "/app/novelties", label: "Novedades", icon: IconAlert, roles: ["SUPERVISOR", "ADMIN"] },
    ],
  },
  {
    title: "Administración",
    items: [
      { to: "/app/admin/users", label: "Usuarios", icon: IconUsers, roles: ["ADMIN"] },
      { to: "/app/admin/allowlist", label: "Dominios permitidos", icon: IconGlobe, roles: ["ADMIN"] },
      { to: "/app/admin/schedules", label: "Plantillas de horario", icon: IconCalendar, roles: ["ADMIN"] },
      { to: "/app/admin/settings", label: "Catálogos operativos", icon: IconBuilding, roles: ["ADMIN"] },
    ],
  },
];
