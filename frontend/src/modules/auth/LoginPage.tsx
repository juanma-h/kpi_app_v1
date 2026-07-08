import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/lib/session/AuthContext";
import { extractErrorMessage } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";
import { InputField } from "@/components/ui/Form";
import { IconAlert, IconBolt, IconChart } from "@/components/ui/Icon";

export function LoginPage() {
  const { login, status } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (status === "authenticated") {
    const state = location.state as { from?: { pathname?: string } } | null;
    const from = state?.from?.pathname ?? "/app/dashboard";
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "No pudimos validar tus credenciales."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <div className="relative flex flex-1 flex-col justify-between overflow-hidden px-8 py-10 lg:px-16 lg:py-16">
        <div
          className="pointer-events-none absolute inset-0 opacity-70"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
            backgroundSize: "42px 42px",
            maskImage: "radial-gradient(circle at 30% 20%, black 0%, transparent 70%)",
          }}
        />
        <div
          className="pointer-events-none absolute -left-24 -top-24 h-96 w-96 rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, rgba(109,91,208,0.35), transparent 70%)" }}
        />
        <div
          className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, rgba(34,211,238,0.25), transparent 70%)" }}
        />

        <div className="relative z-10 flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl brand-gradient text-sm font-bold text-white shadow-[0_0_24px_-4px_rgba(109,91,208,0.9)]">
            N
          </div>
          <span className="text-sm font-semibold tracking-wide text-ink">NEXUS OPS</span>
        </div>

        <div className="relative z-10 max-w-lg">
          <h1 className="text-3xl font-semibold leading-tight text-ink sm:text-4xl">
            Supervisión operativa <span className="brand-gradient-text">en tiempo real</span>
          </h1>
          <p className="mt-4 text-sm text-ink-secondary sm:text-base">
            Controla turnos, horarios, actividad y novedades de tu equipo desde un solo panel:
            claro para el día a día, potente para la supervisión.
          </p>

          <div className="mt-8 flex flex-col gap-3">
            <Feature icon={<IconBolt />} text="Inicio y cierre de turno en un clic" />
            <Feature icon={<IconChart />} text="KPIs de cobertura, puntualidad y actividad" />
            <Feature icon={<IconAlert />} text="Backlog de novedades operativas al día" />
          </div>
        </div>

        <p className="relative z-10 text-xs text-ink-muted">
          © {new Date().getFullYear()} Nexus Ops · Plataforma interna de supervisión
        </p>
      </div>

      <div className="flex flex-1 items-center justify-center border-t border-(--color-border) bg-(--color-surface) px-6 py-12 lg:border-l lg:border-t-0">
        <div className="w-full max-w-sm animate-in">
          <h2 className="text-xl font-semibold text-ink">Inicia sesión</h2>
          <p className="mt-1 text-sm text-ink-muted">Ingresa con tu correo institucional para continuar.</p>

          <form onSubmit={handleSubmit} className="mt-7 flex flex-col gap-4" noValidate>
            <InputField
              label="Correo"
              type="email"
              autoComplete="username"
              placeholder="nombre@empresa.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={submitting}
            />
            <InputField
              label="Contraseña"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={submitting}
            />

            {error && (
              <div className="rounded-lg border border-critical/30 bg-critical/10 px-3 py-2.5 text-sm text-critical">
                {error}
              </div>
            )}

            <Button type="submit" loading={submitting} className="mt-1 w-full">
              Entrar
            </Button>
          </form>

          <p className="mt-6 text-center text-xs text-ink-muted">
            ¿Problemas para acceder? Contacta a tu administrador de plataforma.
          </p>
        </div>
      </div>
    </div>
  );
}

function Feature({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-ink-secondary">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/5 text-brand-2">
        {icon}
      </span>
      {text}
    </div>
  );
}
