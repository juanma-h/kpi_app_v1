import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listScheduleAssignments, listScheduleTemplates, setScheduleTemplateStatus } from "@/lib/api/schedules";
import { listUsers } from "@/lib/api/users";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/States";
import { Tabs } from "@/components/ui/Tabs";
import { Button } from "@/components/ui/Button";
import { TemplateList } from "@/modules/schedules/TemplateList";
import { AssignmentList } from "@/modules/schedules/AssignmentList";
import { NewTemplateModal } from "./NewTemplateModal";
import { NewAssignmentModal } from "./NewAssignmentModal";
import { IconPlus } from "@/components/ui/Icon";

export function SchedulesAdminPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"templates" | "assignments">("templates");
  const [templateModalOpen, setTemplateModalOpen] = useState(false);
  const [assignmentModalOpen, setAssignmentModalOpen] = useState(false);

  const templatesQuery = useQuery({ queryKey: ["schedules", "templates"], queryFn: () => listScheduleTemplates() });
  const assignmentsQuery = useQuery({ queryKey: ["schedules", "assignments"], queryFn: () => listScheduleAssignments() });
  const usersQuery = useQuery({ queryKey: ["users", "all"], queryFn: () => listUsers() });

  const toggleTemplateStatus = useMutation({
    mutationFn: (vars: { id: number; isActive: boolean }) => setScheduleTemplateStatus(vars.id, vars.isActive),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["schedules", "templates"] }),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Plantillas de horario"
        subtitle="Define franjas horarias y asígnalas a los empleados."
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

      <div className="flex justify-end">
        {tab === "templates" ? (
          <Button icon={<IconPlus />} onClick={() => setTemplateModalOpen(true)}>
            Nueva plantilla
          </Button>
        ) : (
          <Button icon={<IconPlus />} onClick={() => setAssignmentModalOpen(true)}>
            Nueva asignación
          </Button>
        )}
      </div>

      {tab === "templates" ? (
        templatesQuery.isLoading ? (
          <Card>
            <LoadingState label="Cargando plantillas…" />
          </Card>
        ) : templatesQuery.isError ? (
          <ErrorState onRetry={() => templatesQuery.refetch()} />
        ) : (
          <TemplateList
            templates={templatesQuery.data ?? []}
            onToggleStatus={(t) => toggleTemplateStatus.mutate({ id: t.id, isActive: !t.is_active })}
          />
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

      <NewTemplateModal open={templateModalOpen} onClose={() => setTemplateModalOpen(false)} />
      <NewAssignmentModal open={assignmentModalOpen} onClose={() => setAssignmentModalOpen(false)} />
    </div>
  );
}
