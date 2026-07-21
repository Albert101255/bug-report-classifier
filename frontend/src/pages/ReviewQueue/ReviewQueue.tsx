import React, { useState, useEffect } from 'react';
import type { PredictionResult } from '../../types';
import { fetchReviewQueue, logCorrection } from '../../api';
import { ShieldCheck, Check, X, Sparkles, AlertTriangle } from 'lucide-react';

export const ReviewQueue: React.FC = () => {
  const [items, setItems] = useState<PredictionResult[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('BL-101 (Authentication & AuthZ)');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const loadData = async () => {
    const list = await fetchReviewQueue();
    setItems(list);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApprove = async (id: string, team: string) => {
    showToast(`Approved model recommendation for '${team}'`);
    setItems(prev => prev.filter(i => i.id !== id));
  };

  const handleOverride = async (id: string) => {
    await logCorrection(id, selectedTeam, "Human review override");
    showToast(`Corrected team to '${selectedTeam}' and logged for retraining audit trail`);
    setItems(prev => prev.filter(i => i.id !== id));
  };

  const teamsOptions = [
    "BL-101 (Authentication & AuthZ)",
    "BL-102 (Database & ORM)",
    "BL-103 (UI Components & Design System)",
    "BL-104 (Payment Gateway & Billing)",
    "BL-105 (Cloud Infrastructure & K8s)",
    "BL-106 (API Gateway & Microservices)",
    "BL-107 (Search & Indexing Engine)",
    "BL-108 (Notification & Webhooks)",
    "BL-109 (Analytics & Telemetry)",
    "BL-110 (Security & Compliance)"
  ];

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
          <h1 className="page-title">Human Review Queue</h1>
          <p className="page-subtitle">Inspect low-confidence predictions (Uncertainty &gt; 0.05) and log human corrections</p>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldCheck size={18} color="var(--accent-amber)" />
          Pending Review Items ({items.length})
        </h2>

        {items.length === 0 ? (
          <div style={{ color: '#64748b', padding: '3rem 0', textAlign: 'center' }}>
            <Check size={48} style={{ opacity: 0.3, marginBottom: '0.5rem', color: '#34d399' }} />
            <p style={{ fontWeight: 600, color: '#34d399' }}>Review Queue Empty!</p>
            <p style={{ fontSize: '0.825rem', marginTop: '0.2rem', color: '#94a3b8' }}>All predictions have been auto-assigned or resolved.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {items.map(item => (
              <div key={item.id} style={{ background: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(245, 158, 11, 0.35)', borderRadius: 12, padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div>
                    <span className={`badge badge-${item.confidence_level}`}>{item.confidence_level} UNCERTAINTY</span>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginTop: '0.4rem' }}>{item.bug_description}</h3>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{new Date(item.created_at).toLocaleTimeString()}</span>
                </div>

                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', background: 'rgba(255,255,255,0.03)', padding: '0.75rem 1rem', borderRadius: 8, marginBottom: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Model Recommendation:</span>
                    <div style={{ fontWeight: 700, color: 'var(--accent-indigo)' }}>{item.predicted_team}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Confidence Score:</span>
                    <div style={{ fontWeight: 700, color: '#fbbf24' }}>{(item.confidence_score * 100).toFixed(1)}%</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Uncertainty Std Dev:</span>
                    <div style={{ fontWeight: 700, color: '#fb7185' }}>{item.uncertainty_score}</div>
                  </div>
                </div>

                {/* Review Controls */}
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', justifyContent: 'flex-end' }}>
                  <select
                    className="chat-input"
                    style={{ fontSize: '0.825rem', padding: '0.45rem 0.75rem' }}
                    onChange={(e) => setSelectedTeam(e.target.value)}
                  >
                    {teamsOptions.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>

                  <button className="btn-secondary" style={{ color: '#fb7185' }} onClick={() => handleOverride(item.id)}>
                    <X size={14} /> Override Team
                  </button>
                  <button className="btn-primary" style={{ background: 'linear-gradient(135deg, var(--accent-emerald), #059669)' }} onClick={() => handleApprove(item.id, item.predicted_team)}>
                    <Check size={14} /> Approve Model Choice
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
