import React, { useState, useEffect } from 'react';
import type { PredictionResult } from '../../types';
import { fetchHistory } from '../../api';
import { History as HistoryIcon, Search, Download, Sparkles, Filter } from 'lucide-react';

export const History: React.FC = () => {
  const [history, setHistory] = useState<PredictionResult[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  useEffect(() => {
    fetchHistory(100).then(setHistory);
  }, []);

  const filtered = history.filter(item => {
    if (levelFilter !== 'all' && item.confidence_level !== levelFilter) return false;
    if (searchQuery && !item.bug_description.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const exportAuditJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(history, null, 2));
    const dl = document.createElement('a');
    dl.setAttribute("href", dataStr);
    dl.setAttribute("download", `prediction_audit_trail_${Date.now()}.json`);
    dl.click();
    showToast('Exported audit trail JSON!');
  };

  return (
    <div>
      {toastMessage && (
        <div className="toast-banner">
          <Sparkles size={18} color="var(--accent-cyan)" />
          <span>{toastMessage}</span>
        </div>
      )}

      <div className="page-header">
        <div>
          <h1 className="page-title">Prediction History & Audit Trail</h1>
          <p className="page-subtitle">Complete audit log of all predictions, confidence levels, and human overrides</p>
        </div>
        <button className="btn-primary" onClick={exportAuditJSON}>
          <Download size={16} /> Export Audit JSON
        </button>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            type="text"
            className="chat-input"
            style={{ width: '100%', paddingLeft: '2.2rem' }}
            placeholder="Search bug descriptions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Search size={14} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
        </div>

        <div style={{ width: 200 }}>
          <select
            className="chat-input"
            style={{ width: '100%' }}
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
          >
            <option value="all">All Confidence Levels</option>
            <option value="HIGH">HIGH Confidence</option>
            <option value="MEDIUM">MEDIUM Confidence</option>
            <option value="LOW">LOW Confidence</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem' }}>Audit Log ({filtered.length} entries)</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Bug Description</th>
              <th>Predicted Team</th>
              <th>Confidence</th>
              <th>Uncertainty</th>
              <th>Level</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(item => (
              <tr key={item.id}>
                <td style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{new Date(item.created_at).toLocaleTimeString()}</td>
                <td style={{ fontWeight: 600 }}>{item.bug_description.slice(0, 70)}...</td>
                <td style={{ color: 'var(--accent-indigo)', fontWeight: 700 }}>{item.predicted_team}</td>
                <td style={{ color: '#34d399', fontWeight: 700 }}>{(item.confidence_score * 100).toFixed(1)}%</td>
                <td>{item.uncertainty_score}</td>
                <td><span className={`badge badge-${item.confidence_level}`}>{item.confidence_level}</span></td>
                <td><span className="badge badge-HIGH">{item.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
