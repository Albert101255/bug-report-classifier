import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Settings as SettingsIcon,
  Shield,
  Sliders,
  GitBranch,
  Save,
  CheckCircle2,
  AlertCircle,
  Key,
} from 'lucide-react';
import {
  getOrgSettings,
  updateOrgSettings,
  getGitHubConfig,
  configureGitHub,
} from '../../api';

export const Settings: React.FC = () => {
  const [highThreshold, setHighThreshold] = useState(0.25);
  const [lowThreshold, setLowThreshold] = useState(0.5);
  const [autoAssign, setAutoAssign] = useState(true);
  const [dedupThreshold, setDedupThreshold] = useState(0.22);

  const [githubEnabled, setGithubEnabled] = useState(false);
  const [githubRepo, setGithubRepo] = useState('');
  const [githubToken, setGithubToken] = useState('');

  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const { data: orgSettings } = useQuery({
    queryKey: ['org_settings'],
    queryFn: getOrgSettings,
  });

  const { data: ghConfig } = useQuery({
    queryKey: ['github_config'],
    queryFn: getGitHubConfig,
  });

  useEffect(() => {
    if (orgSettings) {
      setHighThreshold(orgSettings.confidence_high_threshold);
      setLowThreshold(orgSettings.confidence_low_threshold);
      setAutoAssign(orgSettings.auto_assign_enabled);
      setDedupThreshold(orgSettings.duplicate_detection_threshold);
    }
  }, [orgSettings]);

  useEffect(() => {
    if (ghConfig) {
      setGithubEnabled(ghConfig.is_enabled);
      setGithubRepo(ghConfig.repo || '');
    }
  }, [ghConfig]);

  const orgSettingsMutation = useMutation({
    mutationFn: updateOrgSettings,
    onSuccess: () => {
      setSaveSuccess('Triage routing policies persisted successfully.');
      setTimeout(() => setSaveSuccess(null), 4000);
    },
    onError: (err: any) => {
      setSaveError(err.message || 'Failed to update settings');
    },
  });

  const ghMutation = useMutation({
    mutationFn: configureGitHub,
    onSuccess: () => {
      setSaveSuccess('GitHub integration credentials saved successfully.');
      setGithubToken('');
      setTimeout(() => setSaveSuccess(null), 4000);
    },
    onError: (err: any) => {
      setSaveError(err.message || 'Failed to configure GitHub');
    },
  });

  const handleSavePolicy = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(null);
    setSaveError(null);
    orgSettingsMutation.mutate({
      confidence_high_threshold: highThreshold,
      confidence_low_threshold: lowThreshold,
      auto_assign_enabled: autoAssign,
      duplicate_detection_threshold: dedupThreshold,
    });
  };

  const handleSaveGitHub = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(null);
    setSaveError(null);
    ghMutation.mutate({
      is_enabled: githubEnabled,
      repo: githubRepo,
      access_token: githubToken || undefined,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-brand-500" />
          Workspace Configuration
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Manage triage policies, uncertainty thresholds, and external issue
          synchronization
        </p>
      </div>

      {saveSuccess && (
        <div className="p-3 bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs rounded-lg flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{saveSuccess}</span>
        </div>
      )}

      {saveError && (
        <div className="p-3 bg-red-950/40 border border-red-800 text-red-300 text-xs rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{saveError}</span>
        </div>
      )}

      {/* Triage Decision Policy Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Sliders className="w-4 h-4 text-brand-500" />
          Intelligent Triage & Routing Thresholds
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Uncertainty is evaluated as{' '}
          <code className="font-mono text-[11px] bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">
            1.0 - predicted_probability
          </code>
          . Lower uncertainty corresponds to higher classification confidence.
        </p>

        <form onSubmit={handleSavePolicy} className="space-y-4 pt-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Auto-Assign Uncertainty Threshold (Default: 0.25)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.05"
                max="0.50"
                value={highThreshold}
                onChange={(e) => setHighThreshold(parseFloat(e.target.value))}
                className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs font-mono focus:outline-none focus:border-brand-500"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">
                Predictions with uncertainty below this value are automatically
                assigned.
              </span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Review Queue Threshold (Default: 0.50)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.25"
                max="0.80"
                value={lowThreshold}
                onChange={(e) => setLowThreshold(parseFloat(e.target.value))}
                className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs font-mono focus:outline-none focus:border-brand-500"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">
                Predictions exceeding this uncertainty require mandatory human
                lead review.
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <input
              type="checkbox"
              id="autoAssignCheckbox"
              checked={autoAssign}
              onChange={(e) => setAutoAssign(e.target.checked)}
              className="w-4 h-4 rounded text-brand-600 focus:ring-0"
            />
            <label
              htmlFor="autoAssignCheckbox"
              className="text-xs font-medium text-slate-700 dark:text-slate-300"
            >
              Enable automatic team assignment for high-confidence predictions
            </label>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={orgSettingsMutation.isPending}
              className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors shadow-xs"
            >
              <Save className="w-3.5 h-3.5" />
              Save Routing Policy
            </button>
          </div>
        </form>
      </div>

      {/* GitHub Integration Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-brand-500" />
          GitHub Issues Integration
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Sync verified software defects directly to your target GitHub
          repository.
        </p>

        <form onSubmit={handleSaveGitHub} className="space-y-4 pt-2">
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="ghEnabledCheckbox"
              checked={githubEnabled}
              onChange={(e) => setGithubEnabled(e.target.checked)}
              className="w-4 h-4 rounded text-brand-600 focus:ring-0"
            />
            <label
              htmlFor="ghEnabledCheckbox"
              className="text-xs font-medium text-slate-700 dark:text-slate-300"
            >
              Enable GitHub Issue Synchronization
            </label>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Repository (owner/repo)
              </label>
              <input
                type="text"
                placeholder="acme/platform-core"
                value={githubRepo}
                onChange={(e) => setGithubRepo(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs font-mono focus:outline-none focus:border-brand-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Personal Access Token (PAT)
              </label>
              <input
                type="password"
                placeholder={
                  ghConfig?.has_token
                    ? '•••••••••••••••• (configured)'
                    : 'ghp_...'
                }
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs font-mono focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={ghMutation.isPending}
              className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors shadow-xs"
            >
              <Save className="w-3.5 h-3.5" />
              Save GitHub Credentials
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
