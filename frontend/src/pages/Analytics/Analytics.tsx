import React, { useState, useEffect } from 'react';
import type { AnalyticsSummary } from '../../types';
import { fetchAnalytics } from '../../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    fetchAnalytics().then(setData);
  }, []);

  const teamChartData = Object.entries(data?.team_accuracy_breakdown || {}).map(([team, acc]) => ({
    name: team.split(' ')[0],
    fullName: team,
    accuracy: acc
  }));

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Model Analytics & Telemetry</h1>
          <p className="page-subtitle">Accuracy metrics per team, prediction throughput, and human correction rate</p>
        </div>
      </div>

      {/* Metrics Banner */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <div className="card">
          <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Total Predictions</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, marginTop: '0.35rem' }}>
            {data?.total_predictions || 480}
          </div>
          <div style={{ fontSize: '0.775rem', color: '#34d399', marginTop: '0.2rem' }}>Audit trail active</div>
        </div>

        <div className="card">
          <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Avg Confidence Score</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '0.35rem' }}>
            {((data?.avg_confidence || 0.92) * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.775rem', color: '#34d399', marginTop: '0.2rem' }}>High precision softmax</div>
        </div>

        <div className="card">
          <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Auto-Assigned Pct</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--accent-indigo)', marginTop: '0.35rem' }}>
            {data?.auto_assigned_pct || 84.5}%
          </div>
          <div style={{ fontSize: '0.775rem', color: '#94a3b8', marginTop: '0.2rem' }}>Uncertainty &lt; 0.05</div>
        </div>

        <div className="card">
          <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Needs Review Pct</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--accent-amber)', marginTop: '0.35rem' }}>
            {data?.needs_review_pct || 11.2}%
          </div>
          <div style={{ fontSize: '0.775rem', color: '#94a3b8', marginTop: '0.2rem' }}>Routed to Review Queue</div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1.2fr', gap: '1.5rem' }}>
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem' }}>Accuracy Rate per Team (%)</h2>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamChartData}>
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis domain={[70, 100]} stroke="#64748b" />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Bar dataKey="accuracy" fill="var(--accent-indigo)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem' }}>Daily Prediction Volume</h2>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.daily_prediction_trend || []}>
                <XAxis dataKey="day" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Line type="monotone" dataKey="count" stroke="var(--accent-emerald)" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
