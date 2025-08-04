"""
Type annotations for FastAPI server
"""

from datetime import datetime
from typing import Any, AsyncGenerator, TypedDict

from fastapi import FastAPI

from src.core.types import SimulationConfig, SimulationResult, SimulationStatus


class SimulationData(TypedDict):
    """Type definition for simulation data"""

    id: str
    status: SimulationStatus
    created_at: datetime
    updated_at: datetime
    progress: float
    article_content: str
    article_metadata: dict[str, Any]
    config: SimulationConfig
    result: SimulationResult | None
    error: str | None


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Properly typed lifespan function"""
    yield