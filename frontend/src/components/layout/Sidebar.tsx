import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CheckCircle2,
  PlusCircle,
  Inbox,
  BarChart3,
  Users2,
  Settings,
  Cpu,
  LogOut,
  Shield,
  Layers,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();

  const isAdmin = user?.role === 'ORG_ADMIN';

  const navItems = isAdmin
    ? [
        { to: '/', label: 'Overview', icon: LayoutDashboard },
        { to: '/triage', label: 'Triage Inbox', icon: Inbox },
        { to: '/analytics', label: 'Analytics', icon: BarChart3 },
        { to: '/teams', label: 'Teams & Projects', icon: Users2 },
        { to: '/settings', label: 'Settings', icon: Settings },
        { to: '/models', label: 'Models', icon: Cpu },
      ]
    : [
        { to: '/issues/new', label: 'Create Issue', icon: PlusCircle },
        { to: '/issues', label: 'Issue Explorer', icon: CheckCircle2 },
      ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Workspace Brand Header */}
        <div className="h-14 flex items-center px-4 border-b border-slate-800 gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            <Layers className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm text-slate-100 tracking-tight">
              Triage
            </span>
            <span className="text-[11px] text-slate-400 font-mono leading-none">
              Engineering Platform
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-brand-400 font-semibold shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Footer Profile */}
      <div className="p-3 border-t border-slate-800">
        <div className="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-slate-800/50">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center text-slate-200 text-xs font-semibold">
              {user?.full_name ? user.full_name[0].toUpperCase() : 'U'}
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-xs font-medium text-slate-200 truncate">
                {user?.full_name || 'User'}
              </span>
              <span className="text-[10px] text-slate-400 font-mono truncate flex items-center gap-1">
                <Shield className="w-2.5 h-2.5 text-brand-400" />
                {user?.role || 'DEVELOPER'}
              </span>
            </div>
          </div>
          <button
            onClick={logout}
            title="Sign out"
            className="p-1.5 text-slate-400 hover:text-red-400 rounded transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
