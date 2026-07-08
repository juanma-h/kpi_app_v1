import { useAuth } from "@/lib/session/AuthContext";
import { EmployeeDashboard } from "./EmployeeDashboard";
import { SupervisorDashboard } from "./SupervisorDashboard";

export function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;
  if (user.role === "EMPLOYEE") return <EmployeeDashboard />;
  return <SupervisorDashboard />;
}
