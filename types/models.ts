export interface ModelInfo {
  id: string
  name: string
  provider: string
  max_tokens: number
  context_length?: number
  description?: string
  capabilities?: string[]
  is_available: boolean
}

export interface ModelParameters {
  temperature: number
  max_tokens: number
  top_p: number
  frequency_penalty: number
  top_k?: number
  presence_penalty?: number
}

export interface ProviderConfig {
  name: string
  api_key: string
  base_url?: string
  timeout: number
  max_retries: number
}

export interface EvaluationResult {
  id: string | number
  prompt: string
  model_response: string
  expected_output: string
  exact_match: number
  fuzzy_match: number
  toxicity: boolean
  model: string
  provider?: string
  timestamp: string
  parameters?: ModelParameters
  security_flags?: string[]
  advanced_metrics?: AdvancedMetrics
}

export interface AdvancedMetrics {
  bleu_score: number
  rouge_scores: {
    "rouge-1": { precision: number; recall: number; f1: number }
    "rouge-2": { precision: number; recall: number; f1: number }
    "rouge-l": { precision: number; recall: number; f1: number }
  }
  semantic_similarity: {
    tfidf: number
    jaccard: number
    sequence: number
  }
}

export interface EvaluationSummary {
  total_prompts: number
  average_exact_match: number
  average_fuzzy_match: number
  flagged_prompts: number
  security_score: number
  models_used: string[]
  evaluation_time: number
  advanced_metrics_summary?: AdvancedMetricsSummary
}

export interface AdvancedMetricsSummary {
  average_bleu_score: number
  average_rouge_f1: {
    "rouge-1": number
    "rouge-2": number
    "rouge-l": number
  }
  average_semantic_similarity: {
    tfidf: number
    jaccard: number
    sequence: number
  }
}

export interface EvaluationRequest {
  prompts: Array<{
    prompt: string
    expected_output: string
  }>
  model: string
  parameters?: ModelParameters
}

export interface EvaluationResponse {
  evaluation_id: string
  results: EvaluationResult[]
  summary: EvaluationSummary
  status: "completed" | "failed"
  error?: string
}

export interface Provider {
  name: string
  models: ModelInfo[]
  is_configured: boolean
  api_key_configured: boolean
}

export interface ProviderStatus {
  providers: Provider[]
  total_models: number
  available_models: number
} 