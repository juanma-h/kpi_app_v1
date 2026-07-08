import { Navigate, Route, Routes } from "react-router-dom";
import { RequireAuth } from "@/app/guards/RequireAuth";
import { RequireRole } from "@/app/guards/RequireRole";
import { AppShell } from "@/app/layout/AppShell";
import { LoginPage } from "@/modules/auth/LoginPage";
import { UnauthorizedPage } from "@/modules/misc/UnauthorizedPage";
import { NotFoundPage } from "@/modules/misc/NotFoundPage";
import { HelpPage } from "@/modules/misc/HelpPage";
import { ProfilePage } from "@/modules/profile/ProfilePage";
import { DashboardPage } from "@/modules/dashboard/DashboardPage";
import { ShiftPage } from "@/modules/shifts/ShiftPage";
import { MySchedulePage } from "@/modules/schedules/MySchedulePage";
import { MyActivityPage } from "@/modules/activity/MyActivityPage";
import { MyKpisPage } from "@/modules/kpis/MyKpisPage";
import { NoveltiesPage } from "@/modules/novelties/NoveltiesPage";
import { NoveltyDetailPage } from "@/modules/novelties/NoveltyDetailPage";
import { TeamOverviewPage } from "@/modules/supervisor/TeamOverviewPage";
import { TeamKpisPage } from "@/modules/supervisor/TeamKpisPage";
import { TeamShiftsPage } from "@/modules/supervisor/TeamShiftsPage";
import { TeamActivityPage } from "@/modules/supervisor/TeamActivityPage";
import { TeamSchedulesPage } from "@/modules/supervisor/TeamSchedulesPage";
import { UserDetailPage } from "@/modules/users/UserDetailPage";
import { UsersAdminPage } from "@/modules/admin/UsersAdminPage";
import { AllowlistAdminPage } from "@/modules/admin/AllowlistAdminPage";
import { SchedulesAdminPage } from "@/modules/admin/SchedulesAdminPage";
import { SettingsPage } from "@/modules/admin/SettingsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route path="/app/dashboard" element={<DashboardPage />} />
          <Route path="/app/profile" element={<ProfilePage />} />
          <Route path="/app/help" element={<HelpPage />} />
          <Route path="/app/novelties" element={<NoveltiesPage />} />
          <Route path="/app/novelties/:id" element={<NoveltyDetailPage />} />

          <Route element={<RequireRole roles={["EMPLOYEE"]} />}>
            <Route path="/app/shift" element={<ShiftPage />} />
            <Route path="/app/schedule" element={<MySchedulePage />} />
            <Route path="/app/activity" element={<MyActivityPage />} />
            <Route path="/app/kpis/me" element={<MyKpisPage />} />
          </Route>

          <Route element={<RequireRole roles={["SUPERVISOR", "ADMIN"]} />}>
            <Route path="/app/team/overview" element={<TeamOverviewPage />} />
            <Route path="/app/team/kpis" element={<TeamKpisPage />} />
            <Route path="/app/team/shifts" element={<TeamShiftsPage />} />
            <Route path="/app/team/activity" element={<TeamActivityPage />} />
            <Route path="/app/team/schedules" element={<TeamSchedulesPage />} />
            <Route path="/app/team/users/:id" element={<UserDetailPage />} />
          </Route>

          <Route element={<RequireRole roles={["ADMIN"]} />}>
            <Route path="/app/admin/users" element={<UsersAdminPage />} />
            <Route path="/app/admin/users/:id" element={<UserDetailPage />} />
            <Route path="/app/admin/allowlist" element={<AllowlistAdminPage />} />
            <Route path="/app/admin/schedules" element={<SchedulesAdminPage />} />
            <Route path="/app/admin/settings" element={<SettingsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
