import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Cpu,
  GitBranch,
  MessageSquare,
  Send,
  Shield,
  Tag,
  Terminal,
  User,
  Users,
} from 'lucide-react';
import {
  getIssue,
  updateIssue,
  addComment,
  getIssueAuditTrail,
  getTeams,
  syncToGitHub,
} from '../../api';
import type { IssueStatus, IssueSeverity, IssuePriority } from '../../types';

export const IssueDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const [newComment, setNewComment] = useState('');
  const [syncStatus, setSyncStatus] = useState<string | null>(null);

  const {
    data: issue,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['issue_detail', id],
    queryFn: () => getIssue(id!),
    enabled: !!id,
  });

  const { data: teams } = useQuery({
    queryKey: ['teams'],
    queryFn: getTeams,
  });

  const { data: auditTrail } = useQuery({
    queryKey: ['issue_audit', id],
    queryFn: () => getIssueAuditTrail(id!),
    enabled: !!id,
  });

  const updateMutation = useMutation({
    mutationFn: (updates: {
      status?: IssueStatus;
      team_id?: string;
      severity?: IssueSeverity;
      priority?: IssuePriority;
    }) => updateIssue(id!, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issue_detail', id] });
      queryClient.invalidateQueries({ queryKey: ['issue_audit', id] });
    },
  });

  const commentMutation = useMutation({
    mutationFn: (content: string) => addComment(id!, content),
    onSuccess: () => {
      setNewComment('');
      queryClient.invalidateQueries({ queryKey: ['issue_detail', id] });
      queryClient.invalidateQueries({ queryKey: ['issue_audit', id] });
    },
  });

  const handleSyncToGitHub = async () => {
    if (!id) return;
    setSyncStatus('Syncing to GitHub...');
    try {
      const res = await syncToGitHub(id);
      if (res.success) {
        setSyncStatus(
          `Synced as GitHub Issue #${res.github_issue_number}: ${res.github_issue_url}`,
        );
      } else {
        setSyncStatus(`Sync uncompleted: ${res.message}`);
      }
    } catch (err: any) {
      setSyncStatus(`Sync error: ${err.message}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        Loading issue record...
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-sm">
        Failed to load issue: {(error as Error)?.message || 'Issue not found.'}
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Navigation */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
        <Link
          to="/issues"
          className="flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Issue Explorer
        </Link>
        <button
          onClick={handleSyncToGitHub}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono rounded-lg border border-slate-700 flex items-center gap-1.5 transition-colors"
        >
          <GitBranch className="w-3.5 h-3.5 text-brand-400" />
          Sync to GitHub
        </button>
      </div>

      {syncStatus && (
        <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-slate-300">
          {syncStatus}
        </div>
      )}

      {/* Issue Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="font-mono text-base font-bold text-brand-600 dark:text-brand-400">
              {issue.issue_key}
            </span>
            <span className="text-xs px-2.5 py-1 rounded font-semibold bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200">
              {issue.status}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={issue.status}
              onChange={(e) =>
                updateMutation.mutate({ status: e.target.value as IssueStatus })
              }
              className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none"
            >
              <option value="NEW">Status: New</option>
              <option value="TRIAGE">Status: Triage</option>
              <option value="IN_PROGRESS">Status: In Progress</option>
              <option value="FIXED">Status: Fixed</option>
              <option value="VERIFICATION">Status: Verification</option>
              <option value="CLOSED">Status: Closed</option>
              <option value="REOPENED">Status: Reopened</option>
            </select>
          </div>
        </div>

        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          {issue.title}
        </h1>

        <div className="flex flex-wrap items-center gap-5 text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
          <span className="flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-slate-400" />
            Reported by:{' '}
            <strong className="text-slate-700 dark:text-slate-300">
              {issue.reporter.full_name}
            </strong>
          </span>
          <span className="flex items-center gap-1.5 font-mono">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            {new Date(issue.created_at).toLocaleString()}
          </span>
          <span className="flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-slate-400" />
            Severity:{' '}
            <strong className="text-slate-700 dark:text-slate-300">
              {issue.severity}
            </strong>
          </span>
          <span className="flex items-center gap-1.5">
            Priority:{' '}
            <strong className="text-slate-700 dark:text-slate-300">
              {issue.priority}
            </strong>
          </span>
        </div>
      </div>

      {/* Main Grid: Description & Triage Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Bug Description & Logs */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Description
              </h3>
              <p className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-wrap leading-relaxed">
                {issue.description}
              </p>
            </div>

            {issue.steps_to_reproduce && (
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                  Steps to Reproduce
                </h3>
                <p className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-sans">
                  {issue.steps_to_reproduce}
                </p>
              </div>
            )}

            {issue.technical_logs && (
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5" />
                  Technical Logs / Stack Trace
                </h3>
                <pre className="p-3 bg-slate-950 text-slate-200 rounded-lg text-xs font-mono overflow-x-auto border border-slate-800">
                  {issue.technical_logs}
                </pre>
              </div>
            )}
          </div>

          {/* Comments Discussion Section */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-brand-500" />
              Activity & Discussion ({issue.comments?.length || 0})
            </h3>

            <div className="space-y-3">
              {issue.comments?.map((comment) => (
                <div
                  key={comment.id}
                  className="p-3 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between text-slate-500">
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {comment.author.full_name} ({comment.author.role})
                    </span>
                    <span className="font-mono text-[11px]">
                      {new Date(comment.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300">
                    {comment.content}
                  </p>
                </div>
              ))}
            </div>

            {/* Comment Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (newComment.trim()) commentMutation.mutate(newComment);
              }}
              className="pt-2 flex gap-2"
            >
              <input
                type="text"
                placeholder="Add engineering notes, investigation findings, or reproduction notes..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500"
              />
              <button
                type="submit"
                disabled={commentMutation.isPending || !newComment.trim()}
                className="px-4 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                Comment
              </button>
            </form>
          </div>
        </div>

        {/* Right Col: Triage Routing & Assignment Details */}
        <div className="space-y-6">
          {/* Triage Recommendation Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-500" />
              Triage Classification
            </h3>

            <div className="space-y-2 text-xs">
              <div>
                <span className="text-slate-400 block text-[11px]">
                  Assigned Team:
                </span>
                <select
                  value={issue.team?.id || ''}
                  onChange={(e) =>
                    updateMutation.mutate({ team_id: e.target.value })
                  }
                  className="mt-1 w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 focus:outline-none"
                >
                  <option value="">Unassigned (Needs Triage)</option>
                  {teams?.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>

              {issue.recommended_team && (
                <div className="p-2.5 rounded-lg bg-brand-950/30 border border-brand-800/40 text-brand-300 text-xs">
                  <span className="text-[10px] text-slate-400 block">
                    Classifier Recommended:
                  </span>
                  <span className="font-semibold text-brand-200">
                    {issue.recommended_team.name}
                  </span>
                </div>
              )}

              <div>
                <span className="text-slate-400 block text-[11px]">
                  Triage State:
                </span>
                <span className="font-mono text-xs font-semibold text-slate-800 dark:text-slate-200">
                  {issue.triage_status}
                </span>
              </div>
            </div>
          </div>

          {/* Audit Trail Timeline Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-brand-500" />
              Audit Timeline
            </h3>

            <div className="space-y-2.5">
              {auditTrail?.map((event) => (
                <div
                  key={event.id}
                  className="text-xs border-l-2 border-slate-300 dark:border-slate-700 pl-2.5 py-0.5 space-y-0.5"
                >
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span className="font-semibold text-slate-700 dark:text-slate-300 font-mono">
                      {event.action}
                    </span>
                    <span className="font-mono">
                      {new Date(event.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    by {event.actor ? event.actor.full_name : 'System'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
