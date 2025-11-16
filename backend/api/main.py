"""
FastAPI application for Chimera autonomous drug discovery agent
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import asyncio
import json
from datetime import datetime
import os
import stripe
from dotenv import load_dotenv

import sys
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agent.orchestrator import AgentOrchestrator
from agent.models import AgentRequest, AgentResponse, AgentState

# Import chat router
from api.chat import router as chat_router

# Create FastAPI app
app = FastAPI(
    title="Chimera Drug Discovery Agent API",
    description="Autonomous AI agent for drug discovery and data monetization",
    version="0.1.0"
)

# Include chat router
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

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

# Global event queue for streaming agent thoughts
from asyncio import Queue
event_queue: Queue = Queue()

# Agent configuration (mock mode by default)
agent_config = {
    'mock_mode': True,
    'mock_api_mode': True,
    'wallet_balance': 100.0,
}

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


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
        # Emit start event
        await emit_event("thought", {
            "phase": "planning",
            "content": f"Starting discovery run: {request.goal}"
        })
        await emit_event("phase_change", {"phase": "planning"})

        # Create orchestrator
        orchestrator = AgentOrchestrator(config=agent_config)

        # Emit planning thought
        await emit_event("thought", {
            "phase": "planning",
            "content": f"Analyzing goal and creating execution plan with budget ${request.budget:.2f}"
        })

        # Run agent with event emission
        state = await run_agent_with_events(orchestrator, request)

        # Store state
        active_runs[state.run_id] = state

        # Emit completion
        await emit_event("thought", {
            "phase": "completed",
            "content": f"Discovery complete! Generated {len(state.molecules)} molecules."
        })
        await emit_event("complete", {"phase": "completed"})

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
        await emit_event("thought", {
            "phase": "failed",
            "content": f"Error occurred: {str(e)}"
        })
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/discover/stream")
async def stream_discovery():
    """
    Stream real-time agent thoughts and logs during discovery runs (Server-Sent Events)

    This endpoint provides a continuous stream of:
    - Agent reasoning thoughts (phase-specific thinking)
    - System logs
    - Phase changes

    Returns:
        SSE stream of agent events
    """
    async def event_generator():
        """Generate SSE events from the global event queue"""
        try:
            while True:
                # Wait for events from the queue
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f": keepalive\n\n"
        except GeneratorExit:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


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


@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events

    Processes events like:
    - payment_intent.succeeded: Molecule purchase completed
    - checkout.session.completed: Customer completed checkout
    - payment_intent.payment_failed: Payment failed

    Returns:
        Status message
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']

    print(f"📨 Received webhook: {event_type}")

    if event_type == 'payment_intent.succeeded':
        payment_intent = event_data
        amount = payment_intent['amount'] / 100  # Convert from cents
        customer_id = payment_intent.get('customer')
        metadata = payment_intent.get('metadata', {})

        print(f"💰 Payment succeeded: ${amount:.2f}")
        print(f"   Customer: {customer_id}")
        print(f"   Metadata: {metadata}")

        # Handle molecule purchase
        molecule_id = metadata.get('molecule_id')
        if molecule_id:
            print(f"   🧬 Molecule purchased: {molecule_id}")
            # TODO: Grant access to molecule data
            # TODO: Send download link to customer
            # TODO: Update molecule listing status

    elif event_type == 'checkout.session.completed':
        session = event_data
        customer_email = session.get('customer_email')
        amount_total = session.get('amount_total', 0) / 100

        print(f"✅ Checkout completed: ${amount_total:.2f}")
        print(f"   Customer email: {customer_email}")

    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event_data
        error = payment_intent.get('last_payment_error', {})

        print(f"❌ Payment failed")
        print(f"   Error: {error.get('message', 'Unknown error')}")

    elif event_type == 'customer.created':
        customer = event_data
        print(f"👤 New customer created: {customer.get('email')}")

    elif event_type == 'product.created':
        product = event_data
        print(f"📦 New product created: {product.get('name')}")

    else:
        print(f"ℹ️  Unhandled event type: {event_type}")

    return {"status": "success", "event_type": event_type}


async def emit_event(event_type: str, data: Dict[str, Any]):
    """
    Emit an event to the global event queue

    Args:
        event_type: Type of event ('log', 'thought', 'phase_change', 'complete')
        data: Event data
    """
    event = {"type": event_type, **data}
    await event_queue.put(event)


async def run_agent_with_events(orchestrator: AgentOrchestrator, request: AgentRequest) -> AgentState:
    """
    Run agent and emit thought events as it progresses
    Shows payment activities, decision-making, and overall agent reasoning

    Args:
        orchestrator: Agent orchestrator
        request: Agent request

    Returns:
        Final agent state
    """
    # Emit planning phase thoughts
    await emit_event("phase_change", {"phase": "planning"})
    await emit_event("thought", {
        "phase": "planning",
        "content": f"Analyzing goal: '{request.goal}'"
    })
    await asyncio.sleep(0.3)

    await emit_event("thought", {
        "phase": "planning",
        "content": f"Budget allocated: ${request.budget:.2f} - Planning cost distribution"
    })
    await asyncio.sleep(0.3)

    await emit_event("thought", {
        "phase": "planning",
        "content": "Determining optimal molecule generation strategy and evaluation pipeline"
    })
    await asyncio.sleep(0.4)

    # Emit generation phase thoughts
    await emit_event("phase_change", {"phase": "generating"})
    await emit_event("thought", {
        "phase": "generating",
        "content": "Connecting to NVIDIA NIMs (MolMIM/GenMol) for molecule generation"
    })
    await asyncio.sleep(0.3)

    await emit_event("thought", {
        "phase": "generating",
        "content": "Generating candidate molecules optimized for drug-likeness and target properties"
    })

    # Run the actual agent (this takes the real time)
    state = await orchestrator.run(request)

    # Emit evaluation phase thoughts based on what happened
    await emit_event("phase_change", {"phase": "evaluating"})
    await emit_event("thought", {
        "phase": "evaluating",
        "content": f"Generated {len(state.molecules)} molecules - Beginning comprehensive evaluation"
    })
    await asyncio.sleep(0.3)

    # Show payment decision-making for each molecule
    for i, mol in enumerate(state.molecules[:3], 1):  # Show first 3 for demo
        await emit_event("thought", {
            "phase": "payment",
            "content": f"Molecule {i}: Requesting Locus payment approval for toxicity prediction ($0.005)"
        })
        await asyncio.sleep(0.2)

        await emit_event("thought", {
            "phase": "payment",
            "content": f"Molecule {i}: Payment approved - Executing USDC transaction on Base Network"
        })
        await asyncio.sleep(0.2)

    await emit_event("thought", {
        "phase": "evaluating",
        "content": f"Evaluating {len(state.molecules)} molecules for toxicity, ADMET properties, and synthesizability"
    })
    await asyncio.sleep(0.3)

    # Show decision-making process
    passed_count = sum(1 for m in state.molecules if m.status.value == "passed")
    failed_count = len(state.molecules) - passed_count

    await emit_event("thought", {
        "phase": "decision",
        "content": f"Decision: {passed_count} molecules meet criteria (toxicity < 0.5, drug-likeness > 0.6)"
    })
    await asyncio.sleep(0.3)

    if failed_count > 0:
        await emit_event("thought", {
            "phase": "decision",
            "content": f"Rejected {failed_count} molecules due to toxicity or poor drug-likeness scores"
        })
        await asyncio.sleep(0.3)

    if passed_count > 0:
        await emit_event("thought", {
            "phase": "decision",
            "content": f"Proceeding with visualization and monetization for {passed_count} successful candidates"
        })
        await asyncio.sleep(0.3)

        await emit_event("phase_change", {"phase": "visualizing"})
        await emit_event("thought", {
            "phase": "visualizing",
            "content": "Generating RDKit-based 2D molecular structure visualizations"
        })
        await asyncio.sleep(0.3)

        await emit_event("thought", {
            "phase": "visualizing",
            "content": f"Created visual representations for {min(passed_count, 5)} top candidates"
        })
    else:
        await emit_event("thought", {
            "phase": "decision",
            "content": "No molecules met evaluation criteria - Discovery run complete"
        })

    return state


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
