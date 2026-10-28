import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Inbox,
  CheckCircle2,
  RefreshCw,
  Cpu,
  Layers,
  ArrowRight,
  ShieldAlert,
  Edit2,
  Check,
  AlertTriangle,
} from 'lucide-react';
import {
  getReviewQueue,
  approvePrediction,
  overridePrediction,
  getTeams,
} from '../../api';

export const TriageInbox: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedOverrides, setSelectedOverrides] = useState<
    Record<string, string>
  >({});
  const [overrideReasons, setOverrideReasons] = useState<
    Record<string, string>
  >({});
  const [editingItemId, setEditingItemId] = useState<string | null>(null);

  const {
    data: queueItems,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['triage_queue'],
    queryFn: getReviewQueue,
  });

  const { data: teams } = useQuery({
    queryKey: ['teams'],
    queryFn: getTeams,
  });

  const approveMutation = useMutation({
    mutationFn: (item: { predictionId: string; issueId?: string }) =>
      approvePrediction(item.predictionId, item.issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['triage_queue'] });
      queryClient.invalidateQueries({ queryKey: ['analytics_summary'] });
    },
  });

  const overrideMutation = useMutation({
    mutationFn: (data: {
      prediction_id: string;
      corrected_team: string;
      reason?: string;
      issue_id?: string;
    }) => overridePrediction(data),
    onSuccess: () => {
      setEditingItemId(null);
      queryClient.invalidateQueries({ queryKey: ['triage_queue'] });
      queryClient.invalidateQueries({ queryKey: ['analytics_summary'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        Loading triage review queue...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-sm">
        Failed to load review queue: {(error as Error).message}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <Inbox className="w-5 h-5 text-amber-500" />
            Triage Review Inbox ({queueItems?.length || 0})
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Predictions requiring human review due to low confidence or high
            uncertainty
          </p>
        </div>
      </div>

      {queueItems?.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xs">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            Triage Queue is Empty
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            All submitted bug reports have been confidently routed or verified
            by human reviewers.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {queueItems?.map((item) => {
            const isEditing = editingItemId === item.id;
            const chosenOverride =
              selectedOverrides[item.id] || (teams?.[0]?.name ?? '');
            const chosenReason =
              overrideReasons[item.id] || 'Lead domain re-assignment';

            return (
              <div
                key={item.id}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {item.issue_key && (
                      <Link
                        to={`/issues/${item.issue_id}`}
                        className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400 hover:underline"
                      >
                        {item.issue_key}
                      </Link>
                    )}
                    <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                      {item.title || item.subject || 'Bug Report'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-500 border border-amber-500/20">
                      {(item.confidence_score * 100).toFixed(1)}% (
                      {item.confidence_level})
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {item.bug_description}
                </p>

                {/* Keywords & Alternatives */}
                <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
                  <div>
                    <span className="text-slate-400">
                      Classifier Suggestion:{' '}
                    </span>
                    <strong className="text-slate-800 dark:text-slate-200 font-mono">
                      {item.predicted_team}
                    </strong>
                  </div>
                  {item.top_keywords && item.top_keywords.length > 0 && (
                    <div className="flex items-center gap-1">
                      <span>Keywords: </span>
                      {item.top_keywords.map((kw) => (
                        <span
                          key={kw.word}
                          className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-mono text-[10px]"
                        >
                          {kw.word}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Override Form Panel */}
                {isEditing && (
                  <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                          Corrected Target Team
                        </label>
                        <select
                          value={chosenOverride}
                          onChange={(e) =>
                            setSelectedOverrides({
                              ...selectedOverrides,
                              [item.id]: e.target.value,
                            })
                          }
                          className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded text-xs focus:outline-none"
                        >
                          {teams?.map((t) => (
                            <option key={t.id} value={t.name}>
                              {t.name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                          Audit Override Reason
                        </label>
                        <input
                          type="text"
                          value={chosenReason}
                          onChange={(e) =>
                            setOverrideReasons({
                              ...overrideReasons,
                              [item.id]: e.target.value,
                            })
                          }
                          placeholder="Why is this routing being changed?"
                          className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded text-xs focus:outline-none"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-end gap-2 pt-2">
                  {!isEditing ? (
                    <>
                      <button
                        onClick={() => setEditingItemId(item.id)}
                        className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                        Override Team
                      </button>
                      <button
                        disabled={approveMutation.isPending}
                        onClick={() =>
                          approveMutation.mutate({
                            predictionId: item.id,
                            issueId: item.issue_id,
                          })
                        }
                        className="px-3.5 py-1.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 shadow-xs"
                      >
                        <Check className="w-3.5 h-3.5" />
                        Approve Suggestion
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => setEditingItemId(null)}
                        className="px-3 py-1.5 text-slate-500 text-xs hover:text-slate-700 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        disabled={overrideMutation.isPending}
                        onClick={() =>
                          overrideMutation.mutate({
                            prediction_id: item.id,
                            corrected_team: chosenOverride,
                            reason: chosenReason,
                            issue_id: item.issue_id,
                          })
                        }
                        className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 shadow-xs"
                      >
                        Save Override & Log
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
