import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate, Link } from 'react-router-dom';
import {
  AlertCircle,
  Cpu,
  Layers,
  ArrowRight,
  ShieldAlert,
  Copy,
  Terminal,
  Clock,
  Sparkles,
} from 'lucide-react';
import {
  createIssue,
  getProjects,
  getTeams,
  predictSingleIssue,
} from '../../api';
import type { SinglePredictResult } from '../../types';

export const CreateIssue: React.FC = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [projectId, setProjectId] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('P2 - Major');
  const [priority, setPriority] = useState('MEDIUM');
  const [steps, setSteps] = useState('');
  const [expected, setExpected] = useState('');
  const [actual, setActual] = useState('');
  const [environment, setEnvironment] = useState('Production');
  const [technicalLogs, setTechnicalLogs] = useState('');

  const [predictionPreview, setPredictionPreview] =
    useState<SinglePredictResult | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const { data: teams } = useQuery({
    queryKey: ['teams'],
    queryFn: getTeams,
  });

  useEffect(() => {
    if (projects && projects.length > 0 && !projectId) {
      setProjectId(projects[0].id);
    }
  }, [projects, projectId]);

  // Debounced live prediction preview
  useEffect(() => {
    if (description.trim().length < 15) {
      setPredictionPreview(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsPredicting(true);
      try {
        const res = await predictSingleIssue({
          subject: title,
          description,
          project_id: projectId || undefined,
        });
        setPredictionPreview(res);
      } catch {
        // Degraded or quiet fallback
      } finally {
        setIsPredicting(false);
      }
    }, 600);

    return () => clearTimeout(timer);
  }, [title, description, projectId]);

  const createMutation = useMutation({
    mutationFn: createIssue,
    onSuccess: (data) => {
      navigate(`/issues/${data.id}`);
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create issue.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!title || !description || !projectId) {
      setError('Please provide title, description, and target project.');
      return;
    }

    createMutation.mutate({
      title,
      description,
      project_id: projectId,
      severity,
      priority,
      steps_to_reproduce: steps || undefined,
      expected_behavior: expected || undefined,
      actual_behavior: actual || undefined,
      environment: environment || undefined,
      technical_logs: technicalLogs || undefined,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          Report New Software Defect
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Individual bug submission with real-time classification and duplicate
          detection
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-950/50 border border-red-800 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Real-time Triage Suggestion Banner */}
      {predictionPreview && (
        <div className="p-4 rounded-xl bg-slate-900 border border-brand-500/30 text-slate-200 shadow-md space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-semibold text-brand-400">
              <Cpu className="w-4 h-4" />
              <span>Intelligent Routing Suggestion</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
                {predictionPreview.engine}
              </span>
            </div>
            <div className="text-xs font-mono">
              Confidence:{' '}
              <span
                className={
                  predictionPreview.confidence_level === 'HIGH'
                    ? 'text-emerald-400 font-bold'
                    : 'text-amber-400 font-bold'
                }
              >
                {(predictionPreview.confidence_score * 100).toFixed(1)}% (
                {predictionPreview.confidence_level})
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs">
            <div>
              <span className="text-slate-400">Recommended Team: </span>
              <span className="font-semibold text-slate-100">
                {predictionPreview.predicted_team}
              </span>
            </div>
            <div>
              <span className="text-slate-400">Estimated SLA: </span>
              <span className="font-mono text-slate-100">
                {predictionPreview.sla_hours}h
              </span>
            </div>
          </div>

          {/* Duplicate Warnings */}
          {predictionPreview.potential_duplicates.length > 0 && (
            <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs space-y-1.5">
              <div className="flex items-center gap-1.5 font-semibold text-amber-400">
                <Copy className="w-3.5 h-3.5" />
                <span>
                  Potential Duplicate Issues Detected (
                  {predictionPreview.potential_duplicates.length}):
                </span>
              </div>
              <ul className="space-y-1">
                {predictionPreview.potential_duplicates.map((dup) => (
                  <li
                    key={dup.issue_id}
                    className="flex items-center justify-between text-[11px]"
                  >
                    <span>
                      <strong className="font-mono text-amber-200">
                        {dup.issue_key}
                      </strong>
                      : {dup.title}
                    </span>
                    <span className="text-slate-400 font-mono">
                      {(dup.similarity_score * 100).toFixed(0)}% match
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Stacktrace parser warning */}
          {predictionPreview.stacktrace_analysis.has_trace && (
            <div className="flex items-center gap-2 text-xs text-slate-300 font-mono bg-slate-950/60 p-2 rounded border border-slate-800">
              <Terminal className="w-3.5 h-3.5 text-blue-400" />
              <span>
                Detected Exception:{' '}
                {predictionPreview.stacktrace_analysis.detected_exception ||
                  'Runtime Error'}
              </span>
              {predictionPreview.stacktrace_analysis.source_file && (
                <span className="text-slate-400">
                  at {predictionPreview.stacktrace_analysis.source_file}:
                  {predictionPreview.stacktrace_analysis.line_number}
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Main Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Issue Title *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. PostgreSQL connection pool exhausted during peak queries"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Project *
            </label>
            <select
              required
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-brand-500"
            >
              {projects?.map((p) => (
                <option key={p.id} value={p.id}>
                  [{p.key}] {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Detailed Bug Description *
          </label>
          <textarea
            required
            rows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the failure mode, impacted components, user symptoms, and context..."
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500 font-sans"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Severity
            </label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-brand-500"
            >
              <option value="P0 - Blocker">
                P0 - Blocker (Outage / Security)
              </option>
              <option value="P1 - Critical">
                P1 - Critical (Core feature down)
              </option>
              <option value="P2 - Major">P2 - Major (Normal defect)</option>
              <option value="P3 - Minor">P3 - Minor (Cosmetic / Low)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-brand-500"
            >
              <option value="URGENT">Urgent</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Environment
            </label>
            <input
              type="text"
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
              placeholder="e.g. Production, Staging, v2.4.0"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Steps to Reproduce
            </label>
            <textarea
              rows={3}
              value={steps}
              onChange={(e) => setSteps(e.target.value)}
              placeholder="1. Navigate to billing checkout&#10;2. Click submit button&#10;3. Observe 500 error"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Technical Logs / Stack Trace
            </label>
            <textarea
              rows={3}
              value={technicalLogs}
              onChange={(e) => setTechnicalLogs(e.target.value)}
              placeholder="Paste exception backtrace or error output..."
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500 font-mono"
            />
          </div>
        </div>

        <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-end gap-3">
          <Link
            to="/issues"
            className="px-4 py-2 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="px-5 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-medium text-xs rounded-lg transition-colors flex items-center gap-1.5 shadow-xs"
          >
            {createMutation.isPending
              ? 'Logging issue...'
              : 'Submit Issue & Route'}
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
