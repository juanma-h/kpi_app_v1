import type { ScheduleAssignmentResponse, UserResponse } from "@/types";
import { DataTable } from "@/components/ui/DataTable";
import { ActiveBadge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/utils/format";

export function AssignmentList({
  assignments,
  users,
}: {
  assignments: ScheduleAssignmentResponse[];
  users: UserResponse[];
}) {
  return (
    <DataTable
      rows={assignments}
      rowKey={(row) => row.id}
      emptyTitle="Sin asignaciones de horario"
      columns={[
        {
          key: "user",
          header: "Empleado",
          render: (a) => users.find((u) => u.id === a.user_id)?.name ?? `#${a.user_id}`,
        },
        { key: "template", header: "Plantilla", render: (a) => a.schedule_template.name },
        { key: "from", header: "Desde", render: (a) => formatDate(a.effective_from) },
        { key: "to", header: "Hasta", render: (a) => (a.effective_to ? formatDate(a.effective_to) : "Indefinido") },
        { key: "status", header: "Estado", render: (a) => <ActiveBadge active={a.is_active} /> },
        { key: "notes", header: "Notas", render: (a) => a.notes ?? "—" },
      ]}
    />
  );
}
