/*Define types matching backend:

interface User {
  id: string
  email: string
  created_at: string
}

interface Experiment {
  id: string
  name: string
  description: string
  alpha: number
  two_sided: boolean
  metric: string
  created_at: string
  updated_at: string
  data?: ExperimentData
}

interface ExperimentData {
  n_a: number
  conv_a: number
  n_b: number
  conv_b: number
  data_source: string
  updated_at: string
  conv_rate_a: number
  conv_rate_b: number
  observed_lift: number
  warnings: string[]
}

interface Run {
  run_id: string
  experiment_id: string
  method: string
  status: string  // queued | running | success | failed
  progress?: number
  created_at: string
  started_at?: string
  finished_at?: string
  results?: RunResults
  error_message?: string
}

interface RunResults {
  observed_lift: number
  p_value: number
  z_statistic?: number
  ci_low: number
  ci_high: number
  significant: boolean
  summary: string
  power_results?: PowerResults
  charts?: Record<string, any>  // Plotly structures
}

interface PowerResults {
  effect_grid: number[]
  power: number[]
  n_sims: number
  method: string
  seed: number
}*/