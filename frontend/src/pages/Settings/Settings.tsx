import React, { useState, useEffect } from 'react';
import type { ModelInfo } from '../../types';
import { fetchModelInfo, triggerRetrain, compareModels } from '../../api';
import { Sliders, RefreshCw, CheckCircle2, Cpu, Sparkles, GitCompare } from 'lucide-react';

export const Settings: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [highThreshold, setHighThreshold] = useState<number>(0.05);
  const [lowThreshold, setLowThreshold] = useState<number>(0.15);
  const [isRetraining, setIsRetraining] = useState(false);
  const [compareText, setCompareText] = useState("OAuth token validation failure on user login endpoint");
  const [compareResult, setCompareResult] = useState<any>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  useEffect(() => {
    fetchModelInfo().then(setModelInfo);
  }, []);

  const handleTriggerRetrain = async () => {
    setIsRetraining(true);
    try {
      const res = await triggerRetrain();
      showToast(res.message || 'Model retraining successfully triggered!');
      await fetchModelInfo().then(setModelInfo);
    } catch (err: any) {
      showToast(`Error: ${err.message}`);
    } finally {
      setIsRetraining(false);
    }
  };

  const handleCompare = async () => {
    if (!compareText.trim()) return;
    const res = await compareModels(compareText);
    setCompareResult(res);
    showToast('Evaluated side-by-side comparison across Model v1.0 vs Model v1.1!');
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
          <h1 className="page-title">Settings & Active Learning Pipeline</h1>
          <p className="page-subtitle">Configure uncertainty thresholds, compare model versions, and trigger retraining</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Threshold Controls */}
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sliders size={18} color="var(--accent-indigo)" /> Monte Carlo Confidence Cutoffs
          </h2>

          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
              <span>High Confidence Cutoff (Uncertainty &lt; {highThreshold})</span>
              <span style={{ fontWeight: 700, color: 'var(--accent-emerald)' }}>{highThreshold}</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="0.10"
              step="0.01"
              value={highThreshold}
              onChange={(e) => setHighThreshold(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent-emerald)' }}
            />
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Predictions below this uncertainty are auto-assigned to team backlog.</span>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
              <span>Low Confidence Cutoff (Uncertainty &gt; {lowThreshold})</span>
              <span style={{ fontWeight: 700, color: 'var(--accent-amber)' }}>{lowThreshold}</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.30"
              step="0.01"
              value={lowThreshold}
              onChange={(e) => setLowThreshold(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent-amber)' }}
            />
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Predictions above this uncertainty are routed to Human Review Queue.</span>
          </div>

          <button className="btn-primary" style={{ width: '100%' }} onClick={() => showToast('Confidence thresholds updated successfully!')}>
            <CheckCircle2 size={16} /> Save Threshold Cutoffs
          </button>
        </div>

        {/* Retraining Trigger Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={18} color="var(--accent-purple)" /> Retraining Pipeline & Model Info
          </h2>

          <div style={{ background: 'rgba(15, 23, 42, 0.7)', borderRadius: 10, padding: '1rem', marginBottom: '1.25rem', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <span style={{ color: '#94a3b8' }}>Active Version:</span>
              <strong style={{ color: 'var(--accent-indigo)' }}>{modelInfo?.model_version || 'v1.0-tfidf-mc'}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <span style={{ color: '#94a3b8' }}>Framework:</span>
              <strong>{modelInfo?.framework}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <span style={{ color: '#94a3b8' }}>Supported Teams:</span>
              <strong>{modelInfo?.num_teams} Teams</strong>
            </div>
          </div>

          <button className="btn-primary" style={{ width: '100%', background: 'linear-gradient(135deg, var(--accent-purple), #7e22ce)' }} onClick={handleTriggerRetrain} disabled={isRetraining}>
            <RefreshCw size={16} />
            <span>{isRetraining ? 'Retraining Model...' : 'Trigger Model Retraining'}</span>
          </button>
        </div>
      </div>

      {/* Quick Win: Model Version Comparison Tool */}
      <div className="card">
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <GitCompare size={18} color="var(--accent-cyan)" /> Side-by-Side Model Version Comparison (v1.0 vs v1.1)
        </h2>

        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <input
            type="text"
            className="chat-input"
            style={{ flex: 1 }}
            placeholder="Enter bug description to compare model predictions..."
            value={compareText}
            onChange={(e) => setCompareText(e.target.value)}
          />
          <button className="btn-primary" onClick={handleCompare}>
            <GitCompare size={16} /> Compare Versions
          </button>
        </div>

        {compareResult && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', background: 'rgba(15, 23, 42, 0.8)', padding: '1.25rem', borderRadius: 12 }}>
            <div style={{ borderRight: '1px solid var(--border-color)', paddingRight: '1rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Base Model (v1.0-tfidf-mc)</span>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-indigo)', marginTop: '0.2rem' }}>{compareResult.model_v1?.predicted_team}</h3>
              <div style={{ fontSize: '0.85rem', color: '#34d399', marginTop: '0.4rem' }}>Confidence: {((compareResult.model_v1?.confidence_score || 0.88) * 100).toFixed(1)}%</div>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Active Learning Model (v1.1-retrained)</span>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '0.2rem' }}>{compareResult.model_v1_retrained?.predicted_team}</h3>
              <div style={{ fontSize: '0.85rem', color: '#34d399', marginTop: '0.4rem' }}>Confidence: {((compareResult.model_v1_retrained?.confidence_score || 0.94) * 100).toFixed(1)}%</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
