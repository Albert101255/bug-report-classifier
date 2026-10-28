import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  Clock,
  Tag,
  Shield,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import { listIssues, getTeams } from '../../api';
import type { IssueStatus, IssueSeverity } from '../../types';

export const IssueExplorer: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [teamFilter, setTeamFilter] = useState<string>('');
  const [page, setPage] = useState(1);

  const { data: teams } = useQuery({
    queryKey: ['teams_list'],
    queryFn: getTeams,
  });

  const {
    data: issuesData,
    isLoading,
    isPlaceholderData,
  } = useQuery({
    queryKey: [
      'issues',
      { search, statusFilter, severityFilter, teamFilter, page },
    ],
    queryFn: () =>
      listIssues({
        search: search || undefined,
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
        team_id: teamFilter || undefined,
        page,
        page_size: 20,
      }),
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'P0 - Blocker':
        return 'bg-red-500/15 text-red-500 border-red-500/30';
      case 'P1 - Critical':
        return 'bg-amber-500/15 text-amber-500 border-amber-500/30';
      case 'P2 - Major':
        return 'bg-blue-500/15 text-blue-500 border-blue-500/30';
      default:
        return 'bg-slate-500/15 text-slate-400 border-slate-500/30';
    }
  };

  const getStatusBadge = (status: IssueStatus) => {
    switch (status) {
      case 'NEW':
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';
      case 'TRIAGE':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-400';
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-400';
      case 'FIXED':
      case 'VERIFICATION':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-400';
      case 'CLOSED':
        return 'bg-slate-200 text-slate-800 dark:bg-slate-800/80 dark:text-slate-400';
      case 'REOPENED':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-400';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header and Action */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Issue Explorer
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Search, filter, and inspect tracked software defects
          </p>
        </div>
        <Link
          to="/issues/new"
          className="px-3.5 py-2 text-xs font-medium rounded-lg bg-brand-600 hover:bg-brand-500 text-white flex items-center gap-1.5 transition-colors shadow-xs"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          Create Bug Report
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex flex-wrap items-center gap-3 shadow-xs">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by title, key, or description..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-700 dark:text-slate-300 focus:outline-none"
        >
          <option value="">All Statuses</option>
          <option value="NEW">New</option>
          <option value="TRIAGE">Triage</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="FIXED">Fixed</option>
          <option value="VERIFICATION">Verification</option>
          <option value="CLOSED">Closed</option>
          <option value="REOPENED">Reopened</option>
        </select>

        <select
          value={severityFilter}
          onChange={(e) => {
            setSeverityFilter(e.target.value);
            setPage(1);
          }}
          className="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-700 dark:text-slate-300 focus:outline-none"
        >
          <option value="">All Severities</option>
          <option value="P0 - Blocker">P0 - Blocker</option>
          <option value="P1 - Critical">P1 - Critical</option>
          <option value="P2 - Major">P2 - Major</option>
          <option value="P3 - Minor">P3 - Minor</option>
        </select>

        <select
          value={teamFilter}
          onChange={(e) => {
            setTeamFilter(e.target.value);
            setPage(1);
          }}
          className="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-700 dark:text-slate-300 focus:outline-none"
        >
          <option value="">All Teams</option>
          {teams?.map((t) => (
            <option key={t.id} value={t.id}>
              {t.code} - {t.name}
            </option>
          ))}
        </select>
      </div>

      {/* Issues Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
        {isLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            Loading issues...
          </div>
        ) : issuesData?.items.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle2 className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              No bug reports found
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Adjust your search filters or submit a new bug report.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/50 text-slate-500 font-medium">
                  <th className="py-2.5 px-4 w-28">Issue Key</th>
                  <th className="py-2.5 px-4">Title</th>
                  <th className="py-2.5 px-4 w-28">Status</th>
                  <th className="py-2.5 px-4 w-28">Severity</th>
                  <th className="py-2.5 px-4 w-48">Responsible Team</th>
                  <th className="py-2.5 px-4 w-36">Assignee</th>
                  <th className="py-2.5 px-4 w-28">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {issuesData?.items.map((issue) => (
                  <tr
                    key={issue.id}
                    onClick={() => navigate(`/issues/${issue.id}`)}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-4 font-mono font-medium text-brand-600 dark:text-brand-400">
                      {issue.issue_key}
                    </td>
                    <td className="py-2.5 px-4 font-medium text-slate-900 dark:text-slate-100 truncate max-w-xs">
                      {issue.title}
                    </td>
                    <td className="py-2.5 px-4">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide ${getStatusBadge(
                          issue.status,
                        )}`}
                      >
                        {issue.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4">
                      <span
                        className={`inline-block px-1.5 py-0.5 rounded border text-[10px] font-mono font-medium ${getSeverityBadge(
                          issue.severity,
                        )}`}
                      >
                        {issue.severity.split(' ')[0]}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-600 dark:text-slate-300 truncate">
                      {issue.team ? (
                        issue.team.name
                      ) : (
                        <span className="text-amber-500 italic">
                          Needs Triage
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-slate-500 dark:text-slate-400 truncate">
                      {issue.assignee ? (
                        issue.assignee.full_name
                      ) : (
                        <span className="text-slate-400">Unassigned</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 text-[11px] font-mono">
                      {new Date(issue.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {issuesData && issuesData.total_pages > 1 && (
          <div className="p-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing {issuesData.items.length} of {issuesData.total} issues
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded border border-slate-300 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-mono">
                Page {page} of {issuesData.total_pages}
              </span>
              <button
                disabled={page >= issuesData.total_pages}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded border border-slate-300 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
