import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { getAnalyticsSummary } from '../../api';

const COLORS = [
  '#ef4444',
  '#f59e0b',
  '#3b82f6',
  '#10b981',
  '#8b5cf6',
  '#64748b',
];

export const Analytics: React.FC = () => {
  const {
    data: summary,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['analytics_summary'],
    queryFn: getAnalyticsSummary,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        Loading analytics telemetry...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-sm">
        Failed to load analytics: {(error as Error).message}
      </div>
    );
  }

  const severityData = Object.entries(summary?.severity_breakdown || {}).map(
    ([name, value]) => ({
      name,
      value,
    }),
  );

  const statusData = Object.entries(summary?.status_breakdown || {}).map(
    ([name, value]) => ({
      name,
      value,
    }),
  );

  const teamData = Object.entries(summary?.team_workload || {}).map(
    ([name, count]) => ({
      name: name.split(' ')[0],
      fullName: name,
      count,
    }),
  );

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          Operational Analytics
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Aggregated engineering defect metrics and intelligent routing
          effectiveness
        </p>
      </div>

      {/* Top Level KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Total Defects Tracked
          </span>
          <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100 mt-1">
            {summary?.total_issues ?? 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Open vs Resolved
          </span>
          <div className="text-2xl font-bold font-mono text-blue-500 mt-1">
            {summary?.open_issues ?? 0} / {summary?.resolved_issues ?? 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Human Override Rate
          </span>
          <div className="text-2xl font-bold font-mono text-purple-500 mt-1">
            {summary?.human_override_rate
              ? `${summary.human_override_rate.toFixed(1)}%`
              : '0.0%'}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Mean Classifier Confidence
          </span>
          <div className="text-2xl font-bold font-mono text-emerald-500 mt-1">
            {summary?.avg_confidence
              ? `${(summary.avg_confidence * 100).toFixed(1)}%`
              : '0.0%'}
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">
            Severity Breakdown
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Proportion of bugs by incident severity level
          </p>

          <div className="h-64 flex items-center justify-center">
            {severityData.length === 0 ? (
              <span className="text-xs text-slate-400">
                No issues recorded yet.
              </span>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) =>
                      `${name.split(' ')[0]}: ${value}`
                    }
                  >
                    {severityData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Status Distribution */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">
            Status Lifecycle Distribution
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Issues by current development phase
          </p>

          <div className="h-64">
            {statusData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No issues recorded yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusData}>
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={11}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={11}
                    tickLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#f8fafc',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="value" fill="#0e8ce9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
