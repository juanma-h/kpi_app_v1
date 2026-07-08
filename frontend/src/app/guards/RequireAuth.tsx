import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/lib/session/AuthContext";
import { LoadingState } from "@/components/ui/States";

export function RequireAuth() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "idle" || status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingState label="Verificando sesión…" />
      </div>
    );
  }

  if (status === "unauthenticated") {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
