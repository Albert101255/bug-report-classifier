import React, { useState } from 'react';
import type { PredictionResult } from '../../types';
import { predictBatch } from '../../api';
import { UploadCloud, FileText, Download, CheckCircle2, RefreshCw, Sparkles } from 'lucide-react';

export const BatchUpload: React.FC = () => {
  const [csvContent, setCsvContent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<PredictionResult[]>([]);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const sampleCSV = `description,subject
"User login failed with HTTP 500 error in OAuth auth service","Auth Failure"
"Database connection pool exhausted during high load queries on postgres","DB Query Timeout"
"React component CSS dropdown menu overflow issue in dark mode","UI Overflow"
"Stripe payment webhook verification failed due to missing signature","Stripe Webhook"
"Kubernetes pod crashing with OOMKilled memory limit exception","K8s Pod OOM"`;

  const handleLoadSample = () => {
    setCsvContent(sampleCSV);
    showToast('Loaded sample CSV data into upload editor');
  };

  const handleProcessBatch = async () => {
    if (!csvContent.trim()) return;
    setIsProcessing(true);

    const lines = csvContent.trim().split('\n').filter(l => l.trim().length > 0);
    const items: Array<{ description: string; subject?: string }> = [];

    lines.forEach((line, idx) => {
      if (idx === 0 && (line.toLowerCase().includes('description') || line.toLowerCase().includes('subject'))) return;
      const parts = line.split(',');
      const desc = parts[0].replace(/^"|"$/g, '').trim();
      const subj = parts[1] ? parts[1].replace(/^"|"$/g, '').trim() : undefined;
      if (desc) items.push({ description: desc, subject: subj });
    });

    try {
      const res = await predictBatch(items);
      setResults(res);
      showToast(`Successfully processed batch of ${res.length} bug items!`);
    } catch (err: any) {
      showToast(`Batch Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const exportResultsCSV = () => {
    let csv = "ID,Subject,Description,Predicted_Team,Confidence,Uncertainty,Level,Status\n";
    results.forEach(r => {
      csv += `"${r.id}","${r.subject || ''}","${r.bug_description.replace(/"/g, '""')}","${r.predicted_team}",${r.confidence_score},${r.uncertainty_score},"${r.confidence_level}","${r.status}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch_predictions_${Date.now()}.csv`;
    a.click();
    showToast('Exported batch predictions to CSV!');
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
          <h1 className="page-title">Batch CSV Prediction</h1>
          <p className="page-subtitle">Upload CSV files for high-throughput automated bug assignment</p>
        </div>
        {results.length > 0 && (
          <button className="btn-primary" onClick={exportResultsCSV}>
            <Download size={16} /> Export Results CSV
          </button>
        )}
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <UploadCloud size={18} color="var(--accent-indigo)" /> CSV Input Editor & Drag-and-Drop
        </h2>

        <textarea
          className="chat-input"
          style={{ width: '100%', height: 160, fontFamily: 'var(--font-mono)', fontSize: '0.85rem', marginBottom: '1rem' }}
          placeholder="Paste CSV rows here (format: description, subject)..."
          value={csvContent}
          onChange={(e) => setCsvContent(e.target.value)}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button className="btn-secondary" onClick={handleLoadSample}>
            <FileText size={16} /> Load Sample CSV
          </button>
          <button className="btn-primary" onClick={handleProcessBatch} disabled={isProcessing}>
            {isProcessing ? <RefreshCw size={16} className="spin" /> : <UploadCloud size={16} />}
            <span>{isProcessing ? 'Processing Batch...' : 'Process Batch Predictions'}</span>
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem' }}>Batch Execution Results ({results.length} items)</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>Bug Description</th>
                <th>Predicted Team</th>
                <th>Confidence</th>
                <th>Uncertainty</th>
                <th>Level</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {results.map(r => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 600 }}>{r.bug_description.slice(0, 75)}...</td>
                  <td style={{ color: 'var(--accent-indigo)', fontWeight: 700 }}>{r.predicted_team}</td>
                  <td style={{ color: '#34d399', fontWeight: 700 }}>{(r.confidence_score * 100).toFixed(1)}%</td>
                  <td>{r.uncertainty_score}</td>
                  <td><span className={`badge badge-${r.confidence_level}`}>{r.confidence_level}</span></td>
                  <td><span className="badge badge-HIGH">{r.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
