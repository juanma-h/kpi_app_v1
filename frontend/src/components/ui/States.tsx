import type { ReactNode } from "react";
import { Spinner } from "./Button";
import { Button } from "./Button";

export function LoadingState({ label = "Cargando información…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-ink-muted">
      <Spinner className="h-6 w-6 text-brand-2" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function ErrorState({
  message = "No se pudo cargar la información.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-critical/30 bg-critical/5 py-14 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-critical/15 text-critical">
        !
      </div>
      <p className="max-w-sm text-sm text-ink-secondary">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Reintentar
        </Button>
      )}
    </div>
  );
}

export function EmptyState({
  title = "Sin datos por ahora",
  description,
  icon,
  action,
}: {
  title?: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-(--color-border-strong) py-14 text-center">
      {icon && <div className="text-3xl opacity-70">{icon}</div>}
      <p className="text-sm font-medium text-ink">{title}</p>
      {description && <p className="max-w-sm text-xs text-ink-muted">{description}</p>}
      {action}
    </div>
  );
}
