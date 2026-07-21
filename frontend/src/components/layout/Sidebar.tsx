import React from 'react';
import { NavLink } from 'react-router-dom';
import { Zap, UploadCloud, History, BarChart3, ShieldCheck, Settings, Bug } from 'lucide-react';

export const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Bug size={22} />
        </div>
        <div>
          <div className="brand-title">Bug Classifier</div>
          <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>MC Dropout SaaS Platform</div>
        </div>
      </div>

      <ul className="nav-list">
        <li className="nav-item">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
            <Zap size={18} /> Quick Predict
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink to="/batch" className={({ isActive }) => (isActive ? 'active' : '')}>
            <UploadCloud size={18} /> Batch Upload
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink to="/history" className={({ isActive }) => (isActive ? 'active' : '')}>
            <History size={18} /> Prediction History
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink to="/analytics" className={({ isActive }) => (isActive ? 'active' : '')}>
            <BarChart3 size={18} /> Model Analytics
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink to="/review" className={({ isActive }) => (isActive ? 'active' : '')}>
            <ShieldCheck size={18} /> Review Queue
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink to="/settings" className={({ isActive }) => (isActive ? 'active' : '')}>
            <Settings size={18} /> Settings & Admin
          </NavLink>
        </li>
      </ul>
    </aside>
  );
};
