import { NavLink } from "react-router-dom";
import clsx from "clsx";
import { NAV_SECTIONS } from "@/app/nav";
import { useAuth } from "@/lib/session/AuthContext";
import { IconLogout, IconX } from "@/components/ui/Icon";

export function Sidebar({ mobileOpen, onClose }: { mobileOpen: boolean; onClose: () => void }) {
  const { user, logout } = useAuth();
  if (!user) return null;

  const sections = NAV_SECTIONS.map((section) => ({
    ...section,
    items: section.items.filter((item) => item.roles.includes(user.role)),
  })).filter((section) => section.items.length > 0);

  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden" onClick={onClose} />
      )}
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-(--color-border) bg-(--color-surface) transition-transform lg:static lg:z-auto lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between px-5 py-5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl brand-gradient text-sm font-bold text-white shadow-[0_0_20px_-4px_rgba(109,91,208,0.8)]">
              N
            </div>
            <div className="leading-tight">
              <p className="text-sm font-semibold text-ink">Nexus Ops</p>
              <p className="text-[11px] text-ink-muted">Supervisión operativa</p>
            </div>
          </div>
          <button className="text-ink-muted lg:hidden" onClick={onClose} aria-label="Cerrar menú">
            <IconX />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-4">
          {sections.map((section) => (
            <div key={section.title} className="mb-5">
              <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
                {section.title}
              </p>
              <div className="flex flex-col gap-0.5">
                {section.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    onClick={onClose}
                    className={({ isActive }) =>
                      clsx(
                        "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-(--color-brand-soft) text-ink shadow-[inset_0_0_0_1px_rgba(109,91,208,0.4)]"
                          : "text-ink-secondary hover:bg-white/5 hover:text-ink",
                      )
                    }
                  >
                    <item.icon className="shrink-0 text-brand-2" />
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-(--color-border) p-3">
          <button
            onClick={logout}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-ink-secondary transition-colors hover:bg-critical/10 hover:text-critical"
          >
            <IconLogout />
            Cerrar sesión
          </button>
        </div>
      </aside>
    </>
  );
}
