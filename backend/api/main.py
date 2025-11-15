"""
FastAPI application for Chimera autonomous drug discovery agent
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import asyncio
import json
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agent.orchestrator import AgentOrchestrator
from agent.models import AgentRequest, AgentResponse, AgentState

# Create FastAPI app
app = FastAPI(
    title="Chimera Drug Discovery Agent API",
    description="Autonomous AI agent for drug discovery and data monetization",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for agent runs (in production, use Redis or DB)
active_runs: Dict[str, AgentState] = {}

# Agent configuration (mock mode by default)
agent_config = {
    'mock_mode': True,
    'mock_api_mode': True,
    'wallet_balance': 100.0,
}


@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "name": "Chimera Drug Discovery Agent",
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/discover", response_model=AgentResponse)
async def start_discovery(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Start an autonomous drug discovery run

    Args:
        request: Agent request with goal, target, budget, etc.

    Returns:
        Initial agent response with run_id
    """
    try:
        # Create orchestrator
        orchestrator = AgentOrchestrator(config=agent_config)

        # Start agent in background
        background_tasks.add_task(run_agent_background, orchestrator, request)

        # Return initial response
        return AgentResponse(
            run_id=f"run_{len(active_runs)}",
            status="started",
            phase="planning",
            message=f"Started drug discovery run for: {request.goal}",
            budget_remaining=request.budget,
            molecules_generated=0,
            molecules_passed=0,
            logs=[f"Starting run with goal: {request.goal}"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/discover/sync", response_model=Dict[str, Any])
async def discover_sync(request: AgentRequest):
    """
    Run drug discovery synchronously (wait for completion)

    Args:
        request: Agent request

    Returns:
        Complete agent state with results
    """
    try:
        # Create orchestrator
        orchestrator = AgentOrchestrator(config=agent_config)

        # Run agent
        state = await orchestrator.run(request)

        # Store state
        active_runs[state.run_id] = state

        # Return response
        response = orchestrator.create_response(state)

        return {
            "response": response.model_dump(),
            "final_report": state.final_results,
            "molecules": [
                {
                    "id": m.id,
                    "name": m.name,
                    "smiles": m.smiles,
                    "status": m.status.value,
                    "properties": m.properties.model_dump(),
                    "visualization_url": m.visualization_url
                }
                for m in state.molecules
                if m.status.value in ["passed", "monetized"]
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/runs/{run_id}", response_model=Dict[str, Any])
async def get_run_status(run_id: str):
    """
    Get status of a specific run

    Args:
        run_id: Run identifier

    Returns:
        Current state of the run
    """
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    state = active_runs[run_id]
    orchestrator = AgentOrchestrator(config=agent_config)
    response = orchestrator.create_response(state)

    return {
        "response": response.model_dump(),
        "state": {
            "phase": state.phase.value,
            "current_iteration": state.current_iteration,
            "molecules_count": len(state.molecules),
            "logs": state.logs[-10:]  # Last 10 logs
        }
    }


@app.get("/api/v1/runs/{run_id}/stream")
async def stream_run_logs(run_id: str):
    """
    Stream real-time logs for a run (Server-Sent Events)

    Args:
        run_id: Run identifier

    Returns:
        SSE stream of log events
    """
    async def event_generator():
        """Generate SSE events"""
        last_log_index = 0

        while True:
            if run_id in active_runs:
                state = active_runs[run_id]
                logs = state.logs[last_log_index:]

                for log in logs:
                    yield f"data: {json.dumps({'type': 'log', 'message': log})}\n\n"
                    last_log_index += 1

                # Check if run is complete
                if state.phase.value in ["completed", "failed"]:
                    yield f"data: {json.dumps({'type': 'complete', 'phase': state.phase.value})}\n\n"
                    break

            await asyncio.sleep(0.5)  # Poll every 500ms

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/api/v1/runs")
async def list_runs():
    """
    List all runs

    Returns:
        List of run summaries
    """
    runs = []
    for run_id, state in active_runs.items():
        runs.append({
            "run_id": run_id,
            "goal": getattr(state, 'goal', 'N/A'),
            "phase": state.phase.value,
            "molecules": len(state.molecules),
            "start_time": state.start_time.isoformat(),
            "budget_spent": state.plan.budget_allocation.spent if state.plan else 0.0
        })

    return {"runs": runs}


@app.delete("/api/v1/runs/{run_id}")
async def delete_run(run_id: str):
    """
    Delete a run from storage

    Args:
        run_id: Run identifier

    Returns:
        Confirmation message
    """
    if run_id in active_runs:
        del active_runs[run_id]
        return {"message": f"Run {run_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")


@app.post("/api/v1/config")
async def update_config(config: Dict[str, Any]):
    """
    Update agent configuration

    Args:
        config: Configuration updates

    Returns:
        Updated configuration
    """
    global agent_config
    agent_config.update(config)
    return {"config": agent_config}


@app.get("/api/v1/config")
async def get_config():
    """
    Get current agent configuration

    Returns:
        Current configuration
    """
    return {"config": agent_config}


async def run_agent_background(orchestrator: AgentOrchestrator, request: AgentRequest):
    """
    Run agent in background task

    Args:
        orchestrator: Agent orchestrator
        request: Agent request
    """
    try:
        state = await orchestrator.run(request)
        active_runs[state.run_id] = state
    except Exception as e:
        print(f"Background agent error: {str(e)}")


# For development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
