import React, { useState } from 'react';
import type { PredictionResult } from '../../types';
import { predictSingle, logCorrection, exportToJira, sendSlackAlert } from '../../api';
import { Zap, CheckCircle2, XCircle, Copy, Sparkles, Brain, Cpu, Send, Share2 } from 'lucide-react';

export const QuickPredict: React.FC = () => {
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [feedbackLogged, setFeedbackLogged] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    setIsPredicting(true);
    setFeedbackLogged(null);
    try {
      const pred = await predictSingle(description, subject);
      setResult(pred);
      showToast(`Classified to ${pred.predicted_team} in ${pred.latency_ms}ms`);
    } catch (err: any) {
      showToast(`Error: ${err.message}`);
    } finally {
      setIsPredicting(false);
    }
  };

  const handleFeedback = async (isCorrect: boolean) => {
    if (!result) return;
    if (isCorrect) {
      setFeedbackLogged('correct');
      showToast('Log confirmed: Prediction marked as correct!');
    } else {
      setFeedbackLogged('wrong');
      await logCorrection(result.id, 'BL-106 (API Gateway & Microservices)', 'User flagged misclassification');
      showToast('Correction logged for retraining queue!');
    }
  };

  const handleExportJira = async () => {
    if (!result) return;
    const res = await exportToJira(result.id, result.predicted_team, subject || 'Bug Ticket', description);
    showToast(`Created Jira Ticket ${res.jira_issue_key} assigned to ${result.predicted_team}`);
  };

  const handleSlackAlert = async () => {
    if (!result) return;
    await sendSlackAlert(result.id, result.bug_description, result.predicted_team, result.uncertainty_score);
    showToast('Sent triage alert notification payload to Slack channel!');
  };

  const copyResult = () => {
    if (!result) return;
    navigator.clipboard.writeText(`${result.predicted_team} (Confidence: ${(result.confidence_score * 100).toFixed(1)}%)`);
    showToast('Copied classification result to clipboard!');
  };

  const sampleBugs = [
    { title: 'User Login OAuth Error', desc: 'User login failed with HTTP 500 error when submitting OAuth token in authentication service' },
    { title: 'Database Pool Exhausted', desc: 'Database connection pool exhausted during high load queries on postgres cluster' },
    { title: 'React UI Overflow Issue', desc: 'React component CSS dropdown menu overflow issue in dark mode dashboard layout' },
    { title: 'Stripe Webhook Failure', desc: 'Stripe payment webhook verification failed due to missing signature header' },
    { title: 'K8s OOMKilled Pod Crash', desc: 'Kubernetes pod crashing with OOMKilled memory limit exception in deployment' }
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
          <h1 className="page-title">Quick Bug Predict</h1>
          <p className="page-subtitle">Real-time TF-IDF + Monte Carlo Dropout uncertainty estimation (&lt; 500ms API SLA)</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem' }}>
        {/* Form Input Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={18} color="var(--accent-indigo)" /> Submit Bug Details
          </h2>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>Bug Subject / Title (Optional)</label>
              <input
                type="text"
                className="chat-input"
                style={{ width: '100%' }}
                placeholder="e.g. OAuth token validation failure on login"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>Bug Description & Stack Trace *</label>
              <textarea
                className="chat-input"
                style={{ width: '100%', height: 160, fontFamily: 'var(--font-sans)', fontSize: '0.9rem' }}
                placeholder="Paste bug details, error stack traces, logs, or user reports here..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            {/* Preset Samples */}
            <div style={{ marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.35rem' }}>Quick Sample Inputs:</span>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                {sampleBugs.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="chip"
                    onClick={() => { setSubject(s.title); setDescription(s.desc); }}
                  >
                    {s.title}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="btn-primary" style={{ width: '100%' }} disabled={isPredicting}>
              <Zap size={16} />
              <span>{isPredicting ? 'Calculating Monte Carlo Dropout...' : 'Classify Bug Report'}</span>
            </button>
          </form>
        </div>

        {/* Prediction Results Display Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Brain size={18} color="var(--accent-purple)" /> Classification Result
          </h2>

          {!result ? (
            <div style={{ color: '#64748b', padding: '4rem 0', textAlign: 'center' }}>
              <Cpu size={48} style={{ opacity: 0.3, marginBottom: '0.75rem' }} />
              <p style={{ fontWeight: 600, color: '#94a3b8' }}>Awaiting input submission</p>
              <p style={{ fontSize: '0.825rem', marginTop: '0.2rem' }}>Fill in the form to run variance-based MC Dropout prediction.</p>
            </div>
          ) : (
            <div>
              <div style={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)', borderRadius: 14, padding: '1.25rem', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>Recommended Backlog Team</span>
                    <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--accent-indigo)', marginTop: '0.2rem' }}>{result.predicted_team}</h3>
                  </div>
                  <span className={`badge badge-${result.confidence_level}`}>
                    {result.confidence_level} CONFIDENCE
                  </span>
                </div>

                {/* Progress Visualizer */}
                <div style={{ margin: '1rem 0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                    <span>Model Softmax Probability</span>
                    <span style={{ fontWeight: 700, color: '#34d399' }}>{(result.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ height: 8, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${result.confidence_score * 100}%`, background: 'linear-gradient(90deg, var(--accent-indigo), var(--accent-emerald))' }} />
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.775rem', color: '#94a3b8', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
                  <span>MC Std Dev Uncertainty: <strong>{result.uncertainty_score}</strong></span>
                  <span>Latency: <strong>{result.latency_ms} ms</strong></span>
                </div>
              </div>

              {/* Quick Win Buttons: Jira Sync & Slack Alert */}
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <button className="btn-secondary" style={{ flex: 1, color: '#6366f1' }} onClick={handleExportJira}>
                  <Share2 size={14} /> Sync to Jira
                </button>
                <button className="btn-secondary" style={{ flex: 1, color: '#34d399' }} onClick={handleSlackAlert}>
                  <Send size={14} /> Alert Slack
                </button>
              </div>

              {/* Action Toolbar */}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn-primary" style={{ flex: 1 }} onClick={copyResult}>
                  <Copy size={14} /> Copy Result
                </button>
                <button
                  className="btn-secondary"
                  style={{ color: feedbackLogged === 'correct' ? '#34d399' : undefined }}
                  onClick={() => handleFeedback(true)}
                >
                  <CheckCircle2 size={16} /> Correct
                </button>
                <button
                  className="btn-secondary"
                  style={{ color: feedbackLogged === 'wrong' ? '#fb7185' : undefined }}
                  onClick={() => handleFeedback(false)}
                >
                  <XCircle size={16} /> Wrong
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
