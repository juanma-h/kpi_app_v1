import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listScheduleAssignments, listScheduleTemplates } from "@/lib/api/schedules";
import { listUsers } from "@/lib/api/users";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { Tabs } from "@/components/ui/Tabs";
import { TemplateList } from "@/modules/schedules/TemplateList";
import { AssignmentList } from "@/modules/schedules/AssignmentList";

export function TeamSchedulesPage() {
  const [tab, setTab] = useState<"templates" | "assignments">("templates");

  const templatesQuery = useQuery({ queryKey: ["schedules", "templates"], queryFn: () => listScheduleTemplates() });
  const assignmentsQuery = useQuery({ queryKey: ["schedules", "assignments"], queryFn: () => listScheduleAssignments() });
  const usersQuery = useQuery({ queryKey: ["users", "all"], queryFn: () => listUsers() });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Horarios"
        subtitle="Consulta plantillas y asignaciones vigentes del equipo."
        actions={
          <Tabs
            items={[
              { key: "templates", label: "Plantillas" },
              { key: "assignments", label: "Asignaciones" },
            ]}
            active={tab}
            onChange={(k) => setTab(k as typeof tab)}
          />
        }
      />

      {tab === "templates" ? (
        templatesQuery.isLoading ? (
          <Card>
            <LoadingState label="Cargando plantillas…" />
          </Card>
        ) : templatesQuery.isError ? (
          <ErrorState onRetry={() => templatesQuery.refetch()} />
        ) : (
          <TemplateList templates={templatesQuery.data ?? []} />
        )
      ) : assignmentsQuery.isLoading || usersQuery.isLoading ? (
        <Card>
          <LoadingState label="Cargando asignaciones…" />
        </Card>
      ) : assignmentsQuery.isError ? (
        <ErrorState onRetry={() => assignmentsQuery.refetch()} />
      ) : (
        <AssignmentList assignments={assignmentsQuery.data ?? []} users={usersQuery.data ?? []} />
      )}
    </div>
  );
}
