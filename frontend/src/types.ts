export type UserRole =
  | 'ORG_ADMIN'
  | 'PROJECT_MANAGER'
  | 'TEAM_LEAD'
  | 'DEVELOPER'
  | 'QA_REPORTER'
  | 'VIEWER';

export type IssueStatus =
  | 'NEW'
  | 'TRIAGE'
  | 'IN_PROGRESS'
  | 'FIXED'
  | 'VERIFICATION'
  | 'CLOSED'
  | 'REOPENED';

export type IssueSeverity =
  | 'P0 - Blocker'
  | 'P1 - Critical'
  | 'P2 - Major'
  | 'P3 - Minor'
  | 'P4 - Trivial';

export type IssuePriority = 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';

export type TriageState = 'PENDING' | 'APPROVED' | 'OVERRIDDEN' | 'MANUAL';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  description?: string;
  created_at: string;
}

export interface Team {
  id: string;
  organization_id: string;
  code: string;
  name: string;
  description: string;
  category: string;
  created_at: string;
}

export interface Comment {
  id: string;
  issue_id: string;
  author: User;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface AuditEvent {
  id: string;
  issue_id?: string;
  actor?: User;
  action: string;
  entity_type: string;
  entity_id: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface Issue {
  id: string;
  organization_id: string;
  project_id: string;
  issue_key: string;
  title: string;
  description: string;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
  build_version?: string;
  browser_os?: string;
  technical_logs?: string;
  status: IssueStatus;
  severity: IssueSeverity;
  priority: IssuePriority;
  reporter: User;
  assignee?: User;
  team?: Team;
  recommended_team?: Team;
  triage_status: TriageState;
  created_at: string;
  updated_at: string;
  comments: Comment[];
}

export interface PaginatedIssues {
  items: Issue[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AlternativePrediction {
  team: string;
  confidence: number;
  uncertainty: number;
}

export interface KeywordInfluence {
  word: string;
  score: number;
}

export interface StacktraceAnalysis {
  has_trace: boolean;
  detected_exception?: string;
  source_file?: string;
  line_number?: number;
}

export interface DuplicateSuggestion {
  issue_id: string;
  issue_key: string;
  title: string;
  status: string;
  similarity_score: number;
  explanation: string;
}

export interface SinglePredictResult {
  id: string;
  bug_description: string;
  subject?: string;
  predicted_team: string;
  confidence_score: number;
  uncertainty_score: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  status: string;
  severity: IssueSeverity;
  sla_hours: number;
  sla_deadline: string;
  impact_summary: string;
  top_alternatives: AlternativePrediction[];
  top_keywords: KeywordInfluence[];
  potential_duplicates: DuplicateSuggestion[];
  stacktrace_analysis: StacktraceAnalysis;
  matched_rule?: string;
  latency_ms: number;
  created_at: string;
  model_version: string;
  engine: string;
}

export interface ReviewQueueItem {
  id: string;
  issue_id?: string;
  issue_key?: string;
  title?: string;
  bug_description: string;
  subject?: string;
  predicted_team: string;
  confidence_score: number;
  uncertainty_score: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  severity: string;
  top_alternatives: AlternativePrediction[];
  top_keywords: KeywordInfluence[];
  created_at: string;
}

export interface AnalyticsSummary {
  total_issues: number;
  open_issues: number;
  resolved_issues: number;
  triage_pending_count: number;
  avg_confidence: number;
  human_override_rate: number;
  severity_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
  team_workload: Record<string, number>;
  daily_volume_trend: Array<{
    day: string;
    count: number;
    avg_confidence: number;
  }>;
}

export interface OrganizationSettings {
  organization_id: string;
  organization_name: string;
  confidence_high_threshold: number;
  confidence_low_threshold: number;
  auto_assign_enabled: boolean;
  duplicate_detection_threshold: number;
}

export interface GitHubConfig {
  is_enabled: boolean;
  repo?: string;
  has_token: boolean;
}

export interface ModelInfo {
  model_version: string;
  framework: string;
  tf_idf_vocab_size: number;
  num_teams: number;
  confidence_threshold_high: number;
  confidence_threshold_low: number;
  last_trained_at: string;
  is_active: boolean;
  training_dataset_provenance: string;
  accuracy?: number;
  macro_f1?: number;
}
