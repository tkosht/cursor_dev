"""
Core type definitions for AMS

シミュレーション、ペルソナ、結果などの中心的なデータ型定義。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, NewType

from pydantic import BaseModel, Field


# Type aliases
AgentID = NewType("AgentID", str)
PersonaAttributes = Dict[str, Any]  # TODO: Replace with proper Persona type
SimulationState = Dict[str, Any]
ActionResult = Dict[str, Any]
EvaluationResult = Dict[str, Any]


class SimulationStatus(str, Enum):
    """シミュレーションのステータス"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PersonaDemographics(BaseModel):
    """ペルソナの人口統計学的属性"""
    age_range: str = Field(..., description="年齢範囲（例: 25-34）")
    occupation: str = Field(..., description="職業")
    education_level: str = Field(..., description="教育レベル")
    location: str = Field(..., description="居住地域")
    income_bracket: Optional[str] = Field(None, description="収入層")


class PersonaPsychographics(BaseModel):
    """ペルソナの心理的属性"""
    values: List[str] = Field(..., description="価値観")
    interests: List[str] = Field(..., description="興味・関心")
    lifestyle: str = Field(..., description="ライフスタイル")
    personality_traits: List[str] = Field(..., description="性格特性")


class PersonaBehavior(BaseModel):
    """ペルソナの行動パターン"""
    media_consumption: List[str] = Field(..., description="メディア消費習慣")
    decision_making_style: str = Field(..., description="意思決定スタイル")
    technology_adoption: str = Field(..., description="技術採用傾向")
    social_influence: float = Field(..., ge=0.0, le=1.0, description="社会的影響度")


class Persona(BaseModel):
    """評価を行うペルソナ"""
    id: str = Field(..., description="ペルソナID")
    name: str = Field(..., description="ペルソナ名")
    demographics: PersonaDemographics = Field(..., description="人口統計学的属性")
    psychographics: PersonaPsychographics = Field(..., description="心理的属性")
    behavior: PersonaBehavior = Field(..., description="行動パターン")
    background_story: str = Field(..., description="背景ストーリー")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ArticleEvaluation(BaseModel):
    """記事に対する個別評価"""
    persona_id: str = Field(..., description="評価したペルソナのID")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="関連性スコア")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="品質スコア")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="エンゲージメントスコア")
    sentiment: str = Field(..., description="感情（positive/neutral/negative）")
    reasoning: str = Field(..., description="評価の理由")
    would_share: bool = Field(..., description="共有意向")
    would_take_action: bool = Field(..., description="行動意向")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketSegment(BaseModel):
    """市場セグメント分析結果"""
    segment_name: str = Field(..., description="セグメント名")
    size: int = Field(..., description="セグメントサイズ")
    average_scores: Dict[str, float] = Field(..., description="平均スコア")
    key_characteristics: List[str] = Field(..., description="主要特性")
    opportunities: List[str] = Field(..., description="機会")
    challenges: List[str] = Field(..., description="課題")


class SimulationResult(BaseModel):
    """シミュレーション結果"""
    simulation_id: str = Field(..., description="シミュレーションID")
    total_personas: int = Field(..., description="評価ペルソナ総数")
    evaluations: List[ArticleEvaluation] = Field(..., description="個別評価結果")
    
    # 集計結果
    overall_relevance: float = Field(..., ge=0.0, le=1.0, description="全体関連性スコア")
    overall_quality: float = Field(..., ge=0.0, le=1.0, description="全体品質スコア")
    overall_engagement: float = Field(..., ge=0.0, le=1.0, description="全体エンゲージメントスコア")
    
    # セグメント分析
    market_segments: List[MarketSegment] = Field(..., description="市場セグメント分析")
    
    # 推奨事項
    key_insights: List[str] = Field(..., description="主要な洞察")
    recommendations: List[str] = Field(..., description="推奨アクション")
    
    # メタデータ
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: float = Field(..., description="処理時間（秒）")


class SimulationConfig(BaseModel):
    """シミュレーション設定"""
    num_personas: int = Field(default=50, ge=10, le=1000, description="生成するペルソナ数")
    diversity_level: float = Field(default=0.7, ge=0.0, le=1.0, description="多様性レベル")
    analysis_depth: str = Field(default="standard", description="分析深度（quick/standard/deep）")
    focus_segments: Optional[List[str]] = Field(None, description="重点セグメント")
    llm_provider: str = Field(default="gemini", description="使用するLLMプロバイダー")
    parallel_processing: bool = Field(default=True, description="並列処理の有効化")
    include_minority_perspectives: bool = Field(default=True, description="マイノリティ視点の包含")


class ProgressUpdate(BaseModel):
    """進捗更新メッセージ"""
    simulation_id: str
    status: SimulationStatus
    progress: float = Field(..., ge=0.0, le=1.0)
    current_step: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorInfo(BaseModel):
    """エラー情報"""
    error_type: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    traceback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)