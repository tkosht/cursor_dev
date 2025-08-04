// API Types matching the backend

export enum SimulationStatus {
  PENDING = "pending",
  INITIALIZING = "initializing",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export interface SimulationConfig {
  num_personas?: number;
  diversity_level?: number;
  analysis_depth?: "quick" | "standard" | "deep";
  focus_segments?: string[] | null;
  llm_provider?: string;
  parallel_processing?: boolean;
  include_minority_perspectives?: boolean;
}

export interface SimulationCreateRequest {
  article_content: string;
  article_metadata?: Record<string, any>;
  config?: SimulationConfig;
}

export interface SimulationResponse {
  id: string;
  status: SimulationStatus;
  created_at: string;
  updated_at: string;
  progress: number;
  result?: SimulationResult | null;
  error?: string | null;
}

export interface ArticleEvaluation {
  persona_id: string;
  relevance_score: number;
  quality_score: number;
  engagement_score: number;
  sentiment: string;
  reasoning: string;
  would_share: boolean;
  would_take_action: boolean;
  timestamp: string;
}

export interface MarketSegment {
  segment_name: string;
  size: number;
  average_scores: Record<string, number>;
  key_characteristics: string[];
  opportunities: string[];
  challenges: string[];
}

export interface SimulationResult {
  simulation_id: string;
  total_personas: number;
  evaluations: ArticleEvaluation[];
  overall_relevance: number;
  overall_quality: number;
  overall_engagement: number;
  market_segments: MarketSegment[];
  key_insights: string[];
  recommendations: string[];
  completed_at: string;
  processing_time_seconds: number;
}

export interface WebSocketMessage {
  type: "status_update" | "phase_update" | "error";
  data: {
    status?: SimulationStatus;
    progress?: number;
    phase?: string;
    message?: string;
    error?: string;
    timestamp: string;
  };
}