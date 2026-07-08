import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <p className="brand-gradient-text text-6xl font-bold">404</p>
      <h1 className="text-xl font-semibold text-ink">Esta pantalla no existe</h1>
      <p className="max-w-sm text-sm text-ink-muted">
        Revisa la dirección o vuelve al panel principal.
      </p>
      <Link to="/app/dashboard">
        <Button variant="secondary">Ir al dashboard</Button>
      </Link>
    </div>
  );
}
