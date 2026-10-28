import type {
  AnalyticsSummary,
  AuditEvent,
  Comment,
  GitHubConfig,
  Issue,
  ModelInfo,
  Organization,
  OrganizationSettings,
  PaginatedIssues,
  Project,
  ReviewQueueItem,
  SinglePredictResult,
  Team,
  User,
} from './types';

export const API_BASE =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function getAuthToken(): string | null {
  return localStorage.getItem('triage_access_token');
}

export function setAuthToken(token: string | null) {
  if (token) {
    localStorage.setItem('triage_access_token', token);
  } else {
    localStorage.removeItem('triage_access_token');
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = getAuthToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === 'string') {
          errorMessage = errorJson.detail;
        } else if (Array.isArray(errorJson.detail)) {
          errorMessage = errorJson.detail
            .map((d: any) => {
              const field = d.loc ? d.loc[d.loc.length - 1] : '';
              const msg = d.msg || d.message || 'Validation error';
              return field ? `${field}: ${msg}` : msg;
            })
            .join('; ');
        } else {
          errorMessage = JSON.stringify(errorJson.detail);
        }
      }
    } catch {
      // Use fallback error message
    }

    if (
      response.status === 401 &&
      !endpoint.includes('/auth/login') &&
      !endpoint.includes('/auth/register')
    ) {
      setAuthToken(null);
      window.dispatchEvent(new Event('triage_auth_expired'));
    }

    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}

// ==================== Auth ====================
export async function register(data: {
  email: string;
  password: string;
  full_name: string;
  organization_name?: string;
  role?: string;
}): Promise<{ access_token: string; user: User }> {
  const res = await request<{ access_token: string; user: User }>(
    '/auth/register',
    {
      method: 'POST',
      body: JSON.stringify(data),
    },
  );
  setAuthToken(res.access_token);
  return res;
}

export async function login(credentials: {
  email: string;
  password: string;
}): Promise<{ access_token: string; user: User }> {
  const res = await request<{ access_token: string; user: User }>(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify(credentials),
    },
  );
  setAuthToken(res.access_token);
  return res;
}

export async function getMe(): Promise<User> {
  return request<User>('/auth/me');
}

export function logout() {
  setAuthToken(null);
}

// ==================== Org, Projects & Teams ====================
export async function getCurrentOrg(): Promise<Organization> {
  return request<Organization>('/organizations/current');
}

export async function getProjects(): Promise<Project[]> {
  return request<Project[]>('/projects');
}

export async function createProject(data: {
  name: string;
  key: string;
  description?: string;
}): Promise<Project> {
  return request<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getTeams(): Promise<Team[]> {
  return request<Team[]>('/teams');
}

export async function createTeam(data: {
  code: string;
  name: string;
  description: string;
  category?: string;
}): Promise<Team> {
  return request<Team>('/teams', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ==================== Issues ====================
export async function listIssues(params: {
  project_id?: string;
  status?: string;
  severity?: string;
  priority?: string;
  team_id?: string;
  assignee_id?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<PaginatedIssues> {
  const query = new URLSearchParams();
  if (params.project_id) query.append('project_id', params.project_id);
  if (params.status) query.append('status', params.status);
  if (params.severity) query.append('severity', params.severity);
  if (params.priority) query.append('priority', params.priority);
  if (params.team_id) query.append('team_id', params.team_id);
  if (params.assignee_id) query.append('assignee_id', params.assignee_id);
  if (params.search) query.append('search', params.search);
  if (params.page) query.append('page', params.page.toString());
  if (params.page_size) query.append('page_size', params.page_size.toString());

  const qs = query.toString();
  return request<PaginatedIssues>(`/issues${qs ? `?${qs}` : ''}`);
}

export async function getIssue(issueId: string): Promise<Issue> {
  return request<Issue>(`/issues/${issueId}`);
}

export async function createIssue(data: {
  title: string;
  description: string;
  project_id: string;
  severity?: string;
  priority?: string;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
  build_version?: string;
  browser_os?: string;
  technical_logs?: string;
  team_id?: string;
  assignee_id?: string;
}): Promise<Issue> {
  return request<Issue>('/issues', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateIssue(
  issueId: string,
  data: Partial<Issue> & { triage_status?: string },
): Promise<Issue> {
  return request<Issue>(`/issues/${issueId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function addComment(
  issueId: string,
  content: string,
): Promise<Comment> {
  return request<Comment>(`/issues/${issueId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export async function getIssueAuditTrail(
  issueId: string,
): Promise<AuditEvent[]> {
  return request<AuditEvent[]>(`/issues/${issueId}/audit-trail`);
}

// ==================== Triage & ML ====================
export async function predictSingleIssue(data: {
  description: string;
  subject?: string;
  project_id?: string;
}): Promise<SinglePredictResult> {
  return request<SinglePredictResult>('/triage/predict', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getReviewQueue(): Promise<ReviewQueueItem[]> {
  return request<ReviewQueueItem[]>('/triage/review-queue');
}

export async function approvePrediction(
  predictionId: string,
  issueId?: string,
): Promise<{ success: boolean; confirmed_team: string; message: string }> {
  return request('/triage/approve', {
    method: 'POST',
    body: JSON.stringify({ prediction_id: predictionId, issue_id: issueId }),
  });
}

export async function overridePrediction(data: {
  prediction_id: string;
  corrected_team: string;
  reason?: string;
  issue_id?: string;
}): Promise<{
  success: boolean;
  original_team: string;
  corrected_team: string;
  message: string;
}> {
  return request('/triage/override', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ==================== Analytics ====================
export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  return request<AnalyticsSummary>('/analytics/summary');
}

// ==================== Settings ====================
export async function getOrgSettings(): Promise<OrganizationSettings> {
  return request<OrganizationSettings>('/settings/organization');
}

export async function updateOrgSettings(
  data: Partial<OrganizationSettings>,
): Promise<OrganizationSettings> {
  return request<OrganizationSettings>('/settings/organization', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// ==================== Integrations ====================
export async function getGitHubConfig(): Promise<GitHubConfig> {
  return request<GitHubConfig>('/integrations/github');
}

export async function configureGitHub(data: {
  is_enabled: boolean;
  repo: string;
  access_token?: string;
}): Promise<GitHubConfig> {
  return request<GitHubConfig>('/integrations/github', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function syncToGitHub(issueId: string): Promise<{
  success: boolean;
  github_issue_number?: number;
  github_issue_url?: string;
  message: string;
}> {
  return request('/integrations/github/sync', {
    method: 'POST',
    body: JSON.stringify({ issue_id: issueId }),
  });
}

// ==================== Models ====================
export async function getModelInfo(): Promise<ModelInfo> {
  return request<ModelInfo>('/models/info');
}

export async function triggerRetrain(): Promise<{
  success: boolean;
  message: string;
  metrics?: Record<string, any>;
}> {
  return request('/models/retrain', {
    method: 'POST',
  });
}
