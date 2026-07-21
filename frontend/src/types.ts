export interface AlternativePrediction {
  team: string;
  confidence: number;
  uncertainty: number;
}

export interface KeywordInfluence {
  word: string;
  score: number;
}

export interface PredictionResult {
  id: string;
  bug_description: string;
  subject?: string;
  predicted_team: string;
  confidence_score: number;
  uncertainty_score: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  status: string;
  top_alternatives: AlternativePrediction[];
  top_keywords: KeywordInfluence[];
  latency_ms: number;
  created_at: string;
}

export interface TeamInfo {
  code: string;
  name: string;
  description: string;
  category: string;
  accuracy_rate: number;
  total_bugs_assigned: number;
}

export interface AnalyticsSummary {
  total_predictions: number;
  avg_confidence: number;
  avg_uncertainty: number;
  auto_assigned_pct: number;
  needs_review_pct: number;
  corrected_pct: number;
  team_accuracy_breakdown: Record<string, number>;
  daily_prediction_trend: Array<{ day: string; count: number; avg_confidence: number }>;
}

export interface ModelInfo {
  model_version: string;
  framework: string;
  tf_idf_vocab_size: number;
  num_teams: number;
  confidence_threshold_high: number;
  confidence_threshold_low: number;
  last_trained_at: string;
  is_active: boolean;
}
