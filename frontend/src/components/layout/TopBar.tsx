import React from 'react';
import { Activity, Cpu, Sparkles } from 'lucide-react';

export const TopBar: React.FC = () => {
  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <Sparkles size={20} color="var(--accent-indigo)" />
        <span style={{ fontWeight: 700, fontSize: '1.05rem' }}>Automated Bug Assignment & Triage Engine</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#94a3b8' }}>
          <Cpu size={16} color="var(--accent-cyan)" />
          <span>Model: <strong style={{ color: 'white' }}>TF-IDF + MC Dropout v1.0</strong></span>
        </div>

        <div className="badge badge-HIGH" style={{ fontSize: '0.7rem' }}>
          <Activity size={12} /> Model Active
        </div>
      </div>
    </header>
  );
};
