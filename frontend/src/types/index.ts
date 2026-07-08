// Tipos alineados 1:1 con los esquemas Pydantic del backend (app/schemas/*.py)

export type UserRole = "ADMIN" | "SUPERVISOR" | "EMPLOYEE";

export type ShiftStatus = "OPEN" | "CLOSED";

export type ActivityEventType = "PAGE_VIEW" | "HEARTBEAT" | "IDLE" | "RESUME";

export type Weekday =
  | "MONDAY"
  | "TUESDAY"
  | "WEDNESDAY"
  | "THURSDAY"
  | "FRIDAY"
  | "SATURDAY"
  | "SUNDAY";

export type NoveltyPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type NoveltyStatus =
  | "OPEN"
  | "IN_PROGRESS"
  | "BLOCKED"
  | "RESOLVED"
  | "CLOSED";

export type NoveltyLogType =
  | "DAILY_UPDATE"
  | "STATUS_CHANGE"
  | "ASSIGNMENT"
  | "COMMENT"
  | "RESOLUTION";

// ---------- auth / users ----------

export interface UserMe {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export interface UserResponse {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface UserCreatePayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
  is_active: boolean;
}

export interface UserUpdatePayload {
  name?: string;
  email?: string;
  password?: string;
  role?: UserRole;
}

// ---------- shifts ----------

export interface ShiftResponse {
  shift_id: number;
  session_id: number;
  status: ShiftStatus;
  start_at: string;
  end_at: string | null;
}

// ---------- activity ----------

export interface ActivityEventResponse {
  id: number;
  user_id: number;
  shift_id: number;
  session_id: number;
  allowlist_domain_id: number;
  event_type: ActivityEventType;
  source_url: string;
  source_domain: string;
  page_title: string | null;
  occurred_at: string;
  recorded_at: string;
  duration_seconds: number | null;
  event_data: Record<string, string | number | boolean | null> | null;
}

// ---------- allowlist ----------

export interface AllowlistDomainResponse {
  id: number;
  domain: string;
  description: string | null;
  is_active: boolean;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface AllowlistDomainCreatePayload {
  domain: string;
  description?: string | null;
}

// ---------- schedules ----------

export interface ScheduleTemplateSlot {
  id?: number;
  weekday: Weekday;
  start_time: string;
  end_time: string;
}

export interface ScheduleTemplateResponse {
  id: number;
  name: string;
  description: string | null;
  timezone_name: string;
  grace_minutes: number;
  is_active: boolean;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
  slots: ScheduleTemplateSlot[];
}

export interface ScheduleTemplateCreatePayload {
  name: string;
  description?: string | null;
  timezone_name: string;
  grace_minutes: number;
  is_active: boolean;
  slots: { weekday: Weekday; start_time: string; end_time: string }[];
}

export interface ScheduleAssignmentResponse {
  id: number;
  user_id: number;
  schedule_template_id: number;
  effective_from: string;
  effective_to: string | null;
  is_active: boolean;
  notes: string | null;
  assigned_by_user_id: number | null;
  created_at: string;
  updated_at: string;
  schedule_template: {
    id: number;
    name: string;
    timezone_name: string;
    grace_minutes: number;
    is_active: boolean;
  };
}

export interface ScheduleAssignmentCreatePayload {
  user_id: number;
  schedule_template_id: number;
  effective_from: string;
  effective_to?: string | null;
  is_active: boolean;
  notes?: string | null;
}

export interface ScheduleResolutionResponse {
  user_id: number;
  target_date: string;
  is_scheduled: boolean;
  resolution_reason: string | null;
  assignment_id: number | null;
  schedule_template_id: number | null;
  schedule_template_name: string | null;
  timezone_name: string | null;
  weekday: Weekday;
  expected_start_time: string | null;
  expected_end_time: string | null;
  expected_start_at: string | null;
  expected_end_at: string | null;
  grace_deadline_at: string | null;
  grace_minutes: number | null;
  effective_from: string | null;
  effective_to: string | null;
  notes: string | null;
}

// ---------- kpis ----------

export interface KpiDomainBreakdown {
  source_domain: string;
  event_count: number;
  page_view_count: number;
  heartbeat_count: number;
  idle_event_count: number;
  active_seconds: number;
  idle_seconds: number;
}

export interface KpiEventTypeBreakdown {
  event_type: ActivityEventType;
  count: number;
  tracked_seconds: number;
}

export interface OperationalKpiOverviewResponse {
  user_id: number | null;
  user_name: string | null;
  user_email: string | null;
  user_role: UserRole | null;
  shift_count: number;
  closed_shift_count: number;
  open_shift_count: number;
  session_count: number;
  open_session_count: number;
  total_shift_seconds: number;
  total_session_seconds: number;
  total_active_seconds: number;
  total_idle_seconds: number;
  total_tracked_seconds: number;
  total_untracked_session_seconds: number;
  activity_coverage_rate: number;
  active_rate: number;
  idle_rate: number;
  event_count: number;
  page_view_count: number;
  heartbeat_count: number;
  idle_event_count: number;
  resume_count: number;
  distinct_domain_count: number;
  first_activity_at: string | null;
  last_activity_at: string | null;
  punctuality_supported: boolean;
  punctuality_reason: string | null;
  scheduled_shift_count: number;
  punctuality_evaluated_shift_count: number;
  punctual_shift_count: number;
  late_shift_count: number;
  unscheduled_shift_count: number;
  punctuality_rate: number;
  average_late_by_minutes: number;
  max_late_by_minutes: number;
  average_start_delay_minutes: number;
  max_start_delay_minutes: number;
  domains: KpiDomainBreakdown[];
  event_types: KpiEventTypeBreakdown[];
}

export interface ShiftKpiResponse extends OperationalKpiOverviewResponse {
  shift_id: number;
  shift_status: ShiftStatus;
  shift_started_at: string;
  shift_ended_at: string | null;
  device_labels: string[];
  is_scheduled: boolean;
  is_punctual: boolean | null;
  late_by_minutes: number | null;
  start_delay_minutes: number | null;
  scheduled_start_at: string | null;
  scheduled_end_at: string | null;
  grace_deadline_at: string | null;
  schedule_template_id: number | null;
  schedule_template_name: string | null;
  schedule_timezone_name: string | null;
}

// ---------- novelties ----------

export interface UserSummary {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export interface AllowlistDomainSummary {
  id: number;
  domain: string;
  description: string | null;
  is_active: boolean;
}

export interface OperationalAreaResponse {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface SourceSystemResponse {
  id: number;
  code: string;
  name: string;
  description: string | null;
  allowlist_domain_id: number | null;
  is_active: boolean;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
  allowlist_domain: AllowlistDomainSummary | null;
}

export interface OperationalAreaSummary {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface SourceSystemSummary {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
  allowlist_domain: AllowlistDomainSummary | null;
}

export interface NoveltyResponse {
  id: number;
  area_id: number;
  source_system_id: number;
  reported_by_user_id: number;
  assigned_user_id: number | null;
  reported_shift_id: number | null;
  reported_session_id: number | null;
  external_reference: string | null;
  order_reference: string | null;
  customer_reference: string | null;
  title: string;
  description: string;
  novelty_type: string;
  priority: NoveltyPriority;
  status: NoveltyStatus;
  extra_data: Record<string, string | number | boolean | null> | null;
  reported_at: string;
  first_action_at: string | null;
  resolved_at: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
  area: OperationalAreaSummary;
  source_system: SourceSystemSummary;
  reported_by: UserSummary;
  assigned_user: UserSummary | null;
}

export interface NoveltyCreatePayload {
  area_id: number;
  source_system_id: number;
  assigned_user_id?: number | null;
  external_reference?: string | null;
  order_reference?: string | null;
  customer_reference?: string | null;
  title: string;
  description: string;
  novelty_type: string;
  priority: NoveltyPriority;
  reported_at?: string | null;
}

export interface NoveltyLogResponse {
  id: number;
  novelty_id: number;
  author_user_id: number;
  shift_id: number | null;
  session_id: number | null;
  work_date: string;
  log_type: NoveltyLogType;
  content: string;
  worked_minutes: number | null;
  status_after: NoveltyStatus | null;
  logged_at: string;
  author: UserSummary;
}

export interface NoveltyLogCreatePayload {
  work_date?: string | null;
  log_type: NoveltyLogType;
  content: string;
  worked_minutes?: number | null;
  status_after?: NoveltyStatus | null;
}

export interface NoveltyKpiBreakdown {
  key: string;
  label: string;
  count: number;
}

export interface NoveltyKpiOverviewResponse {
  user_id: number | null;
  user_name: string | null;
  user_email: string | null;
  user_role: UserRole | null;
  total_novelties: number;
  open_count: number;
  in_progress_count: number;
  blocked_count: number;
  resolved_count: number;
  closed_count: number;
  backlog_count: number;
  assigned_count: number;
  unassigned_count: number;
  log_entry_count: number;
  logged_novelty_count: number;
  total_logged_minutes: number;
  average_logged_minutes_per_novelty: number;
  average_time_to_first_action_minutes: number;
  average_resolution_minutes: number;
  first_reported_at: string | null;
  last_reported_at: string | null;
  priorities: NoveltyKpiBreakdown[];
  statuses: NoveltyKpiBreakdown[];
  areas: NoveltyKpiBreakdown[];
  source_systems: NoveltyKpiBreakdown[];
  novelty_types: NoveltyKpiBreakdown[];
}

export interface ApiErrorBody {
  detail?: string | { msg: string }[] | string[];
}
