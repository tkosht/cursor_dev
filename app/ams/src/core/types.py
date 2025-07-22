"""
Type definitions for the Article Market Simulator
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeAlias, Literal
from pydantic import BaseModel, Field


# Type aliases
AgentID: TypeAlias = str
SimulationID: TypeAlias = str
ActionType: TypeAlias = str


class PersonalityType(str, Enum):
    """Personality types based on Big Five model"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class InformationChannel(str, Enum):
    """Information channels for content consumption"""
    SOCIAL_MEDIA = "social_media"
    NEWS_WEBSITE = "news_website"
    EMAIL = "email"
    WORD_OF_MOUTH = "word_of_mouth"
    SEARCH_ENGINE = "search_engine"
    RSS_FEED = "rss_feed"


@dataclass
class PersonaAttributes:
    """Attributes defining a persona"""
    
    # Demographics (dynamically generated)
    age: Optional[int] = None
    occupation: Optional[str] = None
    location: Optional[str] = None
    education_level: Optional[str] = None
    income_bracket: Optional[str] = None
    
    # Psychographics
    values: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    personality_traits: Dict[PersonalityType, float] = field(default_factory=dict)
    
    # Behavioral patterns
    information_seeking_behavior: str = "passive"
    decision_making_style: str = "analytical"
    content_sharing_likelihood: float = 0.5
    influence_susceptibility: float = 0.5
    
    # Micro-details
    daily_routines: List[str] = field(default_factory=list)
    cognitive_biases: List[str] = field(default_factory=list)
    emotional_triggers: List[str] = field(default_factory=list)
    preferred_channels: List[InformationChannel] = field(default_factory=list)
    
    # Network position
    connections: List[AgentID] = field(default_factory=list)
    influence_score: float = 0.5
    network_centrality: float = 0.5
    
    # Dynamic attributes
    current_mood: str = "neutral"
    attention_span: float = 1.0
    trust_level: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "demographics": {
                "age": self.age,
                "occupation": self.occupation,
                "location": self.location,
                "education_level": self.education_level,
                "income_bracket": self.income_bracket,
            },
            "psychographics": {
                "values": self.values,
                "interests": self.interests,
                "personality_traits": {k.value: v for k, v in self.personality_traits.items()},
            },
            "behavioral": {
                "information_seeking": self.information_seeking_behavior,
                "decision_making": self.decision_making_style,
                "sharing_likelihood": self.content_sharing_likelihood,
                "influence_susceptibility": self.influence_susceptibility,
            },
            "micro_details": {
                "daily_routines": self.daily_routines,
                "cognitive_biases": self.cognitive_biases,
                "emotional_triggers": self.emotional_triggers,
                "preferred_channels": [ch.value for ch in self.preferred_channels],
            },
            "network": {
                "connections": self.connections,
                "influence_score": self.influence_score,
                "network_centrality": self.network_centrality,
            },
            "dynamic": {
                "current_mood": self.current_mood,
                "attention_span": self.attention_span,
                "trust_level": self.trust_level,
            },
        }


@dataclass
class ActionResult:
    """Result of an agent's action"""
    success: bool
    action_type: ActionType
    agent_id: AgentID
    timestamp: datetime = field(default_factory=datetime.now)
    effects: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action_type": self.action_type,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "effects": self.effects,
            "message": self.message,
        }


class EvaluationMetric(BaseModel):
    """Individual evaluation metric"""
    name: str
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    details: Optional[str] = None


class EvaluationResult(BaseModel):
    """Result of persona evaluation"""
    persona_id: AgentID
    persona_type: str
    article_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Evaluation scores
    metrics: List[EvaluationMetric] = Field(default_factory=list)
    overall_score: float = Field(ge=0.0, le=100.0)
    
    # Qualitative feedback
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    # Predicted behaviors
    sharing_probability: float = Field(ge=0.0, le=1.0)
    engagement_level: Literal["low", "medium", "high"]
    sentiment: Literal["negative", "neutral", "positive"]
    
    # Additional context
    reasoning: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class SimulationState:
    """State of the simulation at a given time"""
    timestep: int = 0
    agents: Dict[AgentID, PersonaAttributes] = field(default_factory=dict)
    
    # Article being evaluated
    article_content: str = ""
    article_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Simulation metrics
    total_shares: int = 0
    total_engagements: int = 0
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Network state
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    information_cascade: List[Dict[str, Any]] = field(default_factory=list)
    
    # Time series data
    metrics_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestep": self.timestep,
            "num_agents": len(self.agents),
            "article_metadata": self.article_metadata,
            "metrics": {
                "total_shares": self.total_shares,
                "total_engagements": self.total_engagements,
                "sentiment_distribution": self.sentiment_distribution,
            },
            "network": {
                "interactions": len(self.interaction_history),
                "cascades": len(self.information_cascade),
            },
        }


class VisualizationUpdate(BaseModel):
    """Update message for visualization clients"""
    update_type: Literal["full", "differential", "event"]
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }