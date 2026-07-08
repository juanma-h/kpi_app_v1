import { useAuth } from "@/lib/session/AuthContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { RoleBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { IconLogout } from "@/components/ui/Icon";

export function ProfilePage() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Mi perfil" subtitle="Información de tu cuenta en la plataforma." />

      <Card className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl brand-gradient text-2xl font-bold text-white shadow-[0_0_24px_-6px_rgba(109,91,208,0.9)]">
            {user.name.charAt(0).toUpperCase()}
          </span>
          <div>
            <p className="text-lg font-semibold text-ink">{user.name}</p>
            <p className="text-sm text-ink-muted">{user.email}</p>
            <div className="mt-2">
              <RoleBadge role={user.role} />
            </div>
          </div>
        </div>
        <Button variant="secondary" icon={<IconLogout />} onClick={logout}>
          Cerrar sesión
        </Button>
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-ink">Identificación</h3>
        <dl className="mt-3 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-ink-muted">ID de usuario</dt>
            <dd className="text-ink">{user.id}</dd>
          </div>
          <div>
            <dt className="text-ink-muted">Rol</dt>
            <dd className="text-ink">{user.role}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
