"""
AMS FastAPI Server Application

Article Market Simulator のWebAPI/WebSocketサーバー実装。
シミュレーションの作成、実行、結果取得、リアルタイム更新を提供。
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.types import SimulationConfig, SimulationResult, SimulationStatus
from .app_types import SimulationData
from .simulation_service import SimulationService

# Structured logging setup
logger = structlog.get_logger()

# In-memory storage for simulations (後でRedis/DBに置き換え)
simulations: dict[str, SimulationData] = {}

# Simulation service instance
simulation_service: SimulationService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPIアプリケーションのライフサイクル管理"""
    # Startup
    logger.info("Starting AMS API Server")
    global simulation_service
    simulation_service = SimulationService(simulations, manager)
    logger.info("Simulation service initialized")
    yield
    # Shutdown
    logger.info("Shutting down AMS API Server")


# FastAPI app initialization
app = FastAPI(
    title="Article Market Simulator API",
    description="Dynamic multi-agent article evaluation system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS設定（開発環境用）
# 開発環境では全てのオリジンを許可（本番環境では制限すること）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発環境のみ。本番では特定のドメインに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class SimulationCreateRequest(BaseModel):
    """シミュレーション作成リクエスト"""

    article_content: str = Field(..., description="評価対象の記事内容")
    article_metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="記事のメタデータ（タイトル、著者など）"
    )
    config: SimulationConfig | None = Field(
        default=None, description="シミュレーション設定（省略時はデフォルト使用）"
    )


class SimulationResponse(BaseModel):
    """シミュレーションレスポンス"""

    id: str = Field(..., description="シミュレーションID")
    status: SimulationStatus = Field(..., description="現在のステータス")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="進捗率")
    result: SimulationResult | None = Field(None, description="シミュレーション結果")
    error: str | None = Field(None, description="エラーメッセージ")


class HealthCheckResponse(BaseModel):
    """ヘルスチェックレスポンス"""

    status: str = "healthy"
    timestamp: datetime
    version: str = "0.1.0"


# WebSocket manager
class ConnectionManager:
    """WebSocket接続管理"""

    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, simulation_id: str) -> None:
        await websocket.accept()
        if simulation_id not in self.active_connections:
            self.active_connections[simulation_id] = []
        self.active_connections[simulation_id].append(websocket)
        logger.info(f"WebSocket connected for simulation {simulation_id}")

    def disconnect(self, websocket: WebSocket, simulation_id: str) -> None:
        if simulation_id in self.active_connections:
            self.active_connections[simulation_id].remove(websocket)
            if not self.active_connections[simulation_id]:
                del self.active_connections[simulation_id]
        logger.info(f"WebSocket disconnected for simulation {simulation_id}")

    async def send_update(self, simulation_id: str, message: dict[str, Any]) -> None:
        if simulation_id in self.active_connections:
            disconnected_clients = []
            for websocket in self.active_connections[simulation_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected_clients.append(websocket)

            # Remove disconnected clients
            for websocket in disconnected_clients:
                self.disconnect(websocket, simulation_id)


manager = ConnectionManager()


# Routes
@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """ヘルスチェックエンドポイント"""
    return HealthCheckResponse(status="healthy", timestamp=datetime.utcnow(), version="0.1.0")


@app.post(
    "/api/simulations", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED
)
async def create_simulation(request: SimulationCreateRequest, background_tasks: BackgroundTasks) -> SimulationResponse:
    """シミュレーション作成エンドポイント"""
    simulation_id = str(uuid.uuid4())

    # シミュレーション情報を保存
    simulation_data = SimulationData(
        id=simulation_id,
        status=SimulationStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        progress=0.0,
        article_content=request.article_content,
        article_metadata=request.article_metadata or {},
        config=request.config or SimulationConfig(focus_segments=None),
        result=None,
        error=None,
    )

    simulations[simulation_id] = simulation_data

    # バックグラウンドタスクでシミュレーション実行
    if simulation_service:
        background_tasks.add_task(simulation_service.run_simulation, simulation_id)
    else:
        logger.error("Simulation service not initialized")
        simulation_data["status"] = SimulationStatus.FAILED
        simulation_data["error"] = "Simulation service not available"

    return SimulationResponse(
        id=simulation_id,
        status=simulation_data["status"],
        created_at=simulation_data["created_at"],
        updated_at=simulation_data["updated_at"],
        progress=simulation_data["progress"],
        result=simulation_data["result"],
        error=simulation_data["error"],
    )


@app.get("/api/simulations/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: str) -> SimulationResponse:
    """シミュレーション情報取得エンドポイント"""
    if simulation_id not in simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation {simulation_id} not found"
        )

    sim_data = simulations[simulation_id]
    return SimulationResponse(
        id=sim_data["id"],
        status=sim_data["status"],
        created_at=sim_data["created_at"],
        updated_at=sim_data["updated_at"],
        progress=sim_data["progress"],
        result=sim_data["result"],
        error=sim_data["error"],
    )


@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str) -> dict[str, Any]:
    """シミュレーションステータス取得エンドポイント"""
    if simulation_id not in simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation {simulation_id} not found"
        )

    sim_data = simulations[simulation_id]
    return {
        "id": simulation_id,
        "status": sim_data["status"],
        "progress": sim_data["progress"],
        "updated_at": sim_data["updated_at"],
    }


@app.get("/api/simulations/{simulation_id}/results")
async def get_simulation_results(simulation_id: str) -> dict[str, Any]:
    """シミュレーション結果取得エンドポイント"""
    if simulation_id not in simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation {simulation_id} not found"
        )

    sim_data = simulations[simulation_id]
    if sim_data["status"] != SimulationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation {simulation_id} is not completed yet",
        )

    return {
        "id": simulation_id,
        "result": sim_data["result"],
        "completed_at": sim_data["updated_at"],
    }


@app.websocket("/ws/simulations/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str) -> None:
    """WebSocketエンドポイント for リアルタイム更新"""
    if simulation_id not in simulations:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, simulation_id)
    try:
        # Send initial status
        sim_data = simulations[simulation_id]
        await websocket.send_json(
            {
                "type": "status",
                "data": {"status": sim_data["status"], "progress": sim_data["progress"]},
            }
        )

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, simulation_id)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
        },
    )
