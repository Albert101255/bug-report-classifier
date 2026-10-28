import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Users2,
  FolderGit2,
  Plus,
  Shield,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import { getProjects, getTeams, createProject, createTeam } from '../../api';

export const TeamsAndProjects: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'teams' | 'projects'>('teams');

  // New Team Form State
  const [teamCode, setTeamCode] = useState('');
  const [teamName, setTeamName] = useState('');
  const [teamDesc, setTeamDesc] = useState('');
  const [teamCategory, setTeamCategory] = useState('Core Engineering');

  // New Project Form State
  const [projName, setProjName] = useState('');
  const [projKey, setProjKey] = useState('');
  const [projDesc, setProjDesc] = useState('');

  const { data: teams } = useQuery({ queryKey: ['teams'], queryFn: getTeams });
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const teamMutation = useMutation({
    mutationFn: createTeam,
    onSuccess: () => {
      setTeamCode('');
      setTeamName('');
      setTeamDesc('');
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });

  const projectMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      setProjName('');
      setProjKey('');
      setProjDesc('');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          Teams & Projects
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Organization engineering domain structures and project tracking keys
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 gap-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab('teams')}
          className={`pb-2.5 transition-colors flex items-center gap-2 ${
            activeTab === 'teams'
              ? 'border-b-2 border-brand-500 text-brand-500 font-semibold'
              : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <Users2 className="w-4 h-4" />
          Engineering Teams ({teams?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`pb-2.5 transition-colors flex items-center gap-2 ${
            activeTab === 'projects'
              ? 'border-b-2 border-brand-500 text-brand-500 font-semibold'
              : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <FolderGit2 className="w-4 h-4" />
          Projects ({projects?.length || 0})
        </button>
      </div>

      {activeTab === 'teams' ? (
        <div className="space-y-6">
          {/* Create Team Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
            <h3 className="text-xs font-semibold uppercase text-slate-500 tracking-wider mb-3">
              Add Engineering Team
            </h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (teamCode && teamName && teamDesc) {
                  teamMutation.mutate({
                    code: teamCode,
                    name: `${teamCode} (${teamName})`,
                    description: teamDesc,
                    category: teamCategory,
                  });
                }
              }}
              className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end"
            >
              <div>
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Team Code (e.g. BL-111)
                </label>
                <input
                  type="text"
                  required
                  placeholder="BL-111"
                  value={teamCode}
                  onChange={(e) => setTeamCode(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Team Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="Observability & APM"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Domain Description
                </label>
                <input
                  type="text"
                  required
                  placeholder="Distributed tracing, logs..."
                  value={teamDesc}
                  onChange={(e) => setTeamDesc(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs focus:outline-none focus:border-brand-500"
                />
              </div>

              <button
                type="submit"
                disabled={teamMutation.isPending}
                className="px-4 py-1.5 bg-brand-600 hover:bg-brand-500 text-white rounded text-xs font-medium transition-colors flex items-center justify-center gap-1.5 shadow-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                Add Team
              </button>
            </form>
          </div>

          {/* Teams Table */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 text-slate-500">
                  <th className="py-2.5 px-4 w-28">Code</th>
                  <th className="py-2.5 px-4 w-48">Name</th>
                  <th className="py-2.5 px-4 w-36">Category</th>
                  <th className="py-2.5 px-4">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {teams?.map((team) => (
                  <tr
                    key={team.id}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/40"
                  >
                    <td className="py-2.5 px-4 font-mono font-medium text-brand-600 dark:text-brand-400">
                      {team.code}
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                      {team.name}
                    </td>
                    <td className="py-2.5 px-4 text-slate-500">
                      {team.category}
                    </td>
                    <td className="py-2.5 px-4 text-slate-600 dark:text-slate-300">
                      {team.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Create Project Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
            <h3 className="text-xs font-semibold uppercase text-slate-500 tracking-wider mb-3">
              Add Project
            </h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (projName && projKey) {
                  projectMutation.mutate({
                    name: projName,
                    key: projKey.toUpperCase(),
                    description: projDesc || undefined,
                  });
                }
              }}
              className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end"
            >
              <div>
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="Billing Microservice"
                  value={projName}
                  onChange={(e) => setProjName(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Issue Key (e.g. BILL)
                </label>
                <input
                  type="text"
                  required
                  maxLength={10}
                  placeholder="BILL"
                  value={projKey}
                  onChange={(e) => setProjKey(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Description
                </label>
                <input
                  type="text"
                  placeholder="Payments and invoicing"
                  value={projDesc}
                  onChange={(e) => setProjDesc(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs focus:outline-none focus:border-brand-500"
                />
              </div>

              <button
                type="submit"
                disabled={projectMutation.isPending}
                className="px-4 py-1.5 bg-brand-600 hover:bg-brand-500 text-white rounded text-xs font-medium transition-colors flex items-center justify-center gap-1.5 shadow-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                Add Project
              </button>
            </form>
          </div>

          {/* Projects Table */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 text-slate-500">
                  <th className="py-2.5 px-4 w-28">Key Prefix</th>
                  <th className="py-2.5 px-4 w-48">Project Name</th>
                  <th className="py-2.5 px-4">Description</th>
                  <th className="py-2.5 px-4 w-36">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {projects?.map((proj) => (
                  <tr
                    key={proj.id}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/40"
                  >
                    <td className="py-2.5 px-4 font-mono font-medium text-brand-600 dark:text-brand-400">
                      {proj.key}
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                      {proj.name}
                    </td>
                    <td className="py-2.5 px-4 text-slate-600 dark:text-slate-300">
                      {proj.description || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(proj.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
