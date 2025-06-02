"""
A2A server application for MVP.
"""

from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException

from app.a2a_mvp.agents.task_agent import TaskAgent
from app.a2a_mvp.core.types import TaskRequest
from app.a2a_mvp.storage.memory import InMemoryStorage

# Create FastAPI app
app = FastAPI(
    title="A2A Task Manager",
    description="A2A-compliant task management service",
    version="1.0.0",
)

# Initialize storage and agent
storage = InMemoryStorage()
task_agent = TaskAgent(storage)


@app.get("/")
async def root():
    """Root endpoint returning agent card."""
    agent_card = task_agent.get_agent_card()
    return {
        "name": agent_card.name,
        "description": agent_card.description,
        "version": agent_card.version,
        "capabilities": {
            "streaming": agent_card.capabilities.streaming,
            "push_notifications": agent_card.capabilities.push_notifications,
        },
        "skills": [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "tags": skill.tags,
                "examples": skill.examples,
            }
            for skill in agent_card.skills
        ],
    }


@app.post("/task")
async def handle_task(request_data: Dict[str, Any]):
    """Handle task requests following A2A protocol."""
    try:
        # Create TaskRequest from incoming data
        task_request = TaskRequest(
            action=request_data.get("action", "list"),
            data=request_data.get("data"),
            task_id=request_data.get("task_id"),
        )

        # Process request
        response = task_agent.process_request(task_request)

        # Return response
        if response.success:
            return {"success": True, "data": response.data}
        else:
            raise HTTPException(status_code=400, detail=response.error)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal error: {str(e)}"
        )


@app.post("/a2a/message")
async def handle_a2a_message(message: Dict[str, Any]):
    """Handle A2A protocol messages."""
    return task_agent.handle_a2a_message(message)


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the A2A server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
