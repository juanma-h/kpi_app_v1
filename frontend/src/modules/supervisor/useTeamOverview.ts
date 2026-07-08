import { useQueries, useQuery } from "@tanstack/react-query";
import { listUsers } from "@/lib/api/users";
import { getUserKpiOverview } from "@/lib/api/kpis";
import type { KpiRangeParams } from "@/lib/api/kpis";
import type { OperationalKpiOverviewResponse, UserResponse } from "@/types";

export interface TeamMemberRow {
  user: UserResponse;
  kpi: OperationalKpiOverviewResponse | undefined;
  isLoading: boolean;
}

export function useTeamOverview(rangeParams: KpiRangeParams) {
  const usersQuery = useQuery({
    queryKey: ["users", "employees"],
    queryFn: () => listUsers({ is_active: true }),
  });

  const users = usersQuery.data ?? [];

  const kpiQueries = useQueries({
    queries: users.map((user) => ({
      queryKey: ["kpis", "user", user.id, rangeParams.started_from ?? "all"],
      queryFn: () => getUserKpiOverview(user.id, rangeParams),
      enabled: !!usersQuery.data,
    })),
  });

  const rows: TeamMemberRow[] = users.map((user, idx) => ({
    user,
    kpi: kpiQueries[idx]?.data,
    isLoading: kpiQueries[idx]?.isLoading ?? true,
  }));

  return {
    rows,
    isLoading: usersQuery.isLoading,
    isError: usersQuery.isError,
    refetch: usersQuery.refetch,
  };
}
