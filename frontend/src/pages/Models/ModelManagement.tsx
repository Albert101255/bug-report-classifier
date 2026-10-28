import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Cpu,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  FileCode2,
  BookOpen,
  Layers,
  Activity,
} from 'lucide-react';
import { getModelInfo, triggerRetrain } from '../../api';

export const ModelManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [retrainStatus, setRetrainStatus] = useState<string | null>(null);
  const [retrainError, setRetrainError] = useState<string | null>(null);

  const {
    data: modelInfo,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['model_info'],
    queryFn: getModelInfo,
  });

  const retrainMutation = useMutation({
    mutationFn: triggerRetrain,
    onSuccess: (res) => {
      setRetrainStatus(res.message);
      queryClient.invalidateQueries({ queryKey: ['model_info'] });
      setTimeout(() => setRetrainStatus(null), 5000);
    },
    onError: (err: any) => {
      setRetrainError(err.message || 'Retraining failed');
      setTimeout(() => setRetrainError(null), 5000);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        Loading model telemetry...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-sm">
        Failed to load model details: {(error as Error).message}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-3 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-brand-500" />
            Machine Learning Engine Management
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Active classification engine status, model provenance, and offline
            retraining
          </p>
        </div>
        <button
          onClick={() => retrainMutation.mutate()}
          disabled={retrainMutation.isPending}
          className="px-4 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium flex items-center gap-2 transition-colors shadow-xs"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${retrainMutation.isPending ? 'animate-spin' : ''}`}
          />
          {retrainMutation.isPending
            ? 'Retraining Baseline...'
            : 'Retrain Active Model'}
        </button>
      </div>

      {retrainStatus && (
        <div className="p-3 bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs rounded-lg flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{retrainStatus}</span>
        </div>
      )}

      {retrainError && (
        <div className="p-3 bg-red-950/40 border border-red-800 text-red-300 text-xs rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{retrainError}</span>
        </div>
      )}

      {/* Model Spec Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Model Version
          </span>
          <div className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100 mt-1 truncate">
            {modelInfo?.model_version || 'N/A'}
          </div>
          <span className="text-[10px] text-emerald-500 mt-1 block font-semibold">
            {modelInfo?.is_active
              ? '● Active in production'
              : '○ Standby / Fallback'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            TF-IDF Vocabulary Size
          </span>
          <div className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100 mt-1">
            {modelInfo?.tf_idf_vocab_size || 0} features
          </div>
          <span className="text-[10px] text-slate-400 mt-1 block">
            Sublinear TF (1-2 n-grams)
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Validation Accuracy
          </span>
          <div className="text-xl font-bold font-mono text-blue-500 mt-1">
            {modelInfo?.accuracy !== undefined && modelInfo.accuracy !== null
              ? `${(modelInfo.accuracy * 100).toFixed(1)}%`
              : 'N/A'}
          </div>
          <span className="text-[10px] text-slate-400 mt-1 block">
            Stratified test split
          </span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <span className="text-xs text-slate-500 font-medium">
            Validation Macro-F1
          </span>
          <div className="text-xl font-bold font-mono text-purple-500 mt-1">
            {modelInfo?.macro_f1 !== undefined && modelInfo.macro_f1 !== null
              ? `${(modelInfo.macro_f1 * 100).toFixed(1)}%`
              : 'N/A'}
          </div>
          <span className="text-[10px] text-slate-400 mt-1 block">
            Unweighted class mean
          </span>
        </div>
      </div>

      {/* Model Provenance & Fallback Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-brand-500" />
          Model Architecture & Limitations
        </h3>

        <div className="text-xs text-slate-600 dark:text-slate-300 space-y-3 leading-relaxed">
          <p>
            The active routing classifier uses a{' '}
            <strong>{modelInfo?.framework}</strong> baseline. Text is tokenized,
            stripped of accents, and projected into a TF-IDF feature space
            before computing multinomial class probabilities across{' '}
            {modelInfo?.num_teams} engineering teams.
          </p>

          <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 font-mono text-[11px] space-y-1">
            <div>
              Training Provenance:{' '}
              <span className="text-brand-500">
                {modelInfo?.training_dataset_provenance}
              </span>
            </div>
            <div>
              Last Trained:{' '}
              <span className="text-slate-400">
                {modelInfo?.last_trained_at}
              </span>
            </div>
          </div>

          <div className="p-3 bg-amber-950/30 border border-amber-800/40 text-amber-300 rounded-lg text-xs space-y-1">
            <div className="font-semibold text-amber-200 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              Evaluation Honesty Notice
            </div>
            <p className="text-[11px] leading-normal text-amber-300/90">
              The baseline was trained on initial seed demonstration examples.
              The reported validation accuracy (
              {modelInfo?.accuracy
                ? `${(modelInfo.accuracy * 100).toFixed(1)}%`
                : 'N/A'}
              ) reflects performance solely on that synthetic dataset split.
              Real production performance requires continuously curated feedback
              datasets from audited engineering triage overrides.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
