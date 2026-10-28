import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  CheckCircle2,
  Inbox,
  Flame,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  Layers,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { getAnalyticsSummary } from '../../api';

export const Overview: React.FC = () => {
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
        Loading operational telemetry...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-sm">
        Failed to load operational overview: {(error as Error).message}
      </div>
    );
  }

  const p0Count =
    (summary?.severity_breakdown?.['P0 - Blocker'] || 0) +
    (summary?.severity_breakdown?.['P1 - Critical'] || 0);
  const teamWorkloadData = Object.entries(summary?.team_workload || {}).map(
    ([team, count]) => ({
      team: team.split(' ')[0],
      fullName: team,
      count,
    }),
  );

  return (
    <div className="space-y-6">
      {/* Top Banner Actions */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Engineering Triage Overview
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time operational queue health and classification metrics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/triage"
            className="px-3.5 py-2 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 flex items-center gap-1.5 transition-colors border border-slate-300 dark:border-slate-700"
          >
            <Inbox className="w-3.5 h-3.5 text-amber-500" />
            Triage Queue ({summary?.triage_pending_count || 0})
          </Link>
          <Link
            to="/issues/new"
            className="px-3.5 py-2 text-xs font-medium rounded-lg bg-brand-600 hover:bg-brand-500 text-white flex items-center gap-1.5 transition-colors shadow-xs"
          >
            Create Issue
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Open Bugs</span>
            <CheckCircle2 className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-slate-100 font-mono">
            {summary?.open_issues ?? 0}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Active across all teams
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Awaiting Triage</span>
            <Inbox className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-amber-500 font-mono">
            {summary?.triage_pending_count ?? 0}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Requires lead confirmation
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Blocker / Critical</span>
            <Flame className="w-4 h-4 text-red-500" />
          </div>
          <div className="text-2xl font-bold text-red-500 font-mono">
            {p0Count}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            P0/P1 incidents
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Classifier Confidence</span>
            <Cpu className="w-4 h-4 text-brand-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-slate-100 font-mono">
            {summary?.avg_confidence
              ? `${(summary.avg_confidence * 100).toFixed(1)}%`
              : '0.0%'}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            TF-IDF + Logistic Regression
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Human Override Rate</span>
            <TrendingUp className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-slate-100 font-mono">
            {summary?.human_override_rate
              ? `${summary.human_override_rate.toFixed(1)}%`
              : '0.0%'}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Audited lead corrections
          </span>
        </div>
      </div>

      {/* Visual Analytics Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Ingestion Trend */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                Issue Ingestion Volume (7 Days)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Incoming bug reports logged per day
              </p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary?.daily_volume_trend || []}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0e8ce9" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0e8ce9" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="day"
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
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#0e8ce9"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#areaGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Team Workload Allocation */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                Team Workload Distribution
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Bugs currently routed by engineering domain
              </p>
            </div>
          </div>
          <div className="h-64 w-full">
            {teamWorkloadData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No bugs assigned to teams yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={teamWorkloadData}>
                  <XAxis
                    dataKey="team"
                    stroke="#64748b"
                    fontSize={10}
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
                  <Bar dataKey="count" fill="#38a8f8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
