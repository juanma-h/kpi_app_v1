import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";

const FAQS = [
  {
    q: "¿Cómo inicio mi turno?",
    a: "Ve a “Mi turno” en el menú lateral y presiona “Iniciar turno”. Se abrirá una sesión de trabajo asociada.",
  },
  {
    q: "¿Qué pasa si olvido cerrar mi turno?",
    a: "El turno queda abierto hasta que lo cierres manualmente. Tu supervisor puede ver turnos abiertos desde “Turnos de hoy”.",
  },
  {
    q: "¿Cómo se mide mi puntualidad?",
    a: "Se compara la hora de inicio de tu turno contra el horario asignado y el margen de tolerancia configurado por un administrador.",
  },
  {
    q: "¿Qué es una novedad?",
    a: "Es un caso operativo (por ejemplo, un pedido con problema en el ecommerce) que reportas, gestionas y documentas con bitácora diaria hasta cerrarlo.",
  },
  {
    q: "¿Quién puede ver mis datos?",
    a: "Tus supervisores y administradores pueden consultar tu actividad, turnos y KPIs para fines de supervisión operativa.",
  },
];

export function HelpPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Ayuda" subtitle="Preguntas frecuentes sobre el uso de la plataforma." />
      <div className="grid gap-4">
        {FAQS.map((faq) => (
          <Card key={faq.q}>
            <h3 className="text-sm font-semibold text-ink">{faq.q}</h3>
            <p className="mt-2 text-sm text-ink-secondary">{faq.a}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
