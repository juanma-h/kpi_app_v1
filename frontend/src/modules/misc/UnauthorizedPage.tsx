import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { IconAlert } from "@/components/ui/Icon";

export function UnauthorizedPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-warning/15 text-warning">
        <IconAlert />
      </div>
      <h1 className="text-2xl font-semibold text-ink">No tienes acceso a esta sección</h1>
      <p className="max-w-sm text-sm text-ink-muted">
        Tu rol actual no tiene permisos para ver esta pantalla. Si crees que es un error, contacta a tu
        administrador.
      </p>
      <Link to="/app/dashboard">
        <Button variant="secondary">Volver al dashboard</Button>
      </Link>
    </div>
  );
}
