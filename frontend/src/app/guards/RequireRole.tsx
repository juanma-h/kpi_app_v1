import { Navigate, Outlet } from "react-router-dom";
import type { UserRole } from "@/types";
import { useAuth } from "@/lib/session/AuthContext";

export function RequireRole({ roles }: { roles: UserRole[] }) {
  const { user } = useAuth();
  if (!user) return null;
  if (!roles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }
  return <Outlet />;
}
