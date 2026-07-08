import { useState } from "react";
import { Link } from "react-router-dom";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { useAuth } from "@/lib/session/AuthContext";
import { RoleBadge } from "@/components/ui/Badge";
import { IconHelp, IconLogout, IconMenu, IconProfile } from "@/components/ui/Icon";

export function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const today = format(new Date(), "EEEE d 'de' MMMM", { locale: es });

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-3 border-b border-(--color-border) bg-(--color-plane)/80 px-4 py-3 backdrop-blur-md sm:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded-lg p-2 text-ink-secondary hover:bg-white/5 lg:hidden"
          aria-label="Abrir menú"
        >
          <IconMenu />
        </button>
        <div className="hidden flex-col sm:flex">
          <span className="text-xs text-ink-muted capitalize">{today}</span>
        </div>
      </div>

      <div className="relative flex items-center gap-2">
        <Link
          to="/app/help"
          className="hidden items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-white/5 hover:text-ink sm:flex"
        >
          <IconHelp />
          Ayuda
        </Link>

        <button
          onClick={() => setMenuOpen((v) => !v)}
          className="flex items-center gap-2.5 rounded-full border border-(--color-border-strong) bg-white/[0.03] py-1.5 pl-1.5 pr-3 transition-colors hover:bg-white/[0.06]"
        >
          <span className="flex h-7 w-7 items-center justify-center rounded-full brand-gradient text-xs font-semibold text-white">
            {user?.name?.charAt(0).toUpperCase() ?? "?"}
          </span>
          <span className="hidden text-left sm:block">
            <span className="block text-sm font-medium leading-tight text-ink">{user?.name}</span>
          </span>
        </button>

        {menuOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
            <div className="glass-panel absolute right-0 top-12 z-20 w-56 rounded-xl bg-(--color-surface-2) p-2 shadow-2xl">
              <div className="px-3 py-2">
                <p className="text-sm font-medium text-ink">{user?.name}</p>
                <p className="truncate text-xs text-ink-muted">{user?.email}</p>
                <div className="mt-2">{user && <RoleBadge role={user.role} />}</div>
              </div>
              <div className="my-1 h-px bg-(--color-border)" />
              <Link
                to="/app/profile"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-ink-secondary hover:bg-white/5 hover:text-ink"
              >
                <IconProfile /> Mi perfil
              </Link>
              <button
                onClick={logout}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm text-ink-secondary hover:bg-critical/10 hover:text-critical"
              >
                <IconLogout /> Cerrar sesión
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
