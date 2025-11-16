"""
Chat API - Conversational interface for drug discovery planning
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.integrations.claude_ai import ClaudeAIClient

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    stream: bool = False


class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int]


class ExtractParamsRequest(BaseModel):
    conversation_history: List[ChatMessage]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with Claude AI about drug discovery planning
    """
    try:
        client = ClaudeAIClient()

        # Convert ChatMessage objects to dicts
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

        if request.stream:
            # Streaming not supported in sync endpoint, redirect to /chat/stream
            raise HTTPException(status_code=400, detail="Use /chat/stream for streaming responses")

        response = client.chat(
            message=request.message,
            conversation_history=history,
            stream=False
        )

        return ChatResponse(
            content=response["content"],
            model=response["model"],
            usage=response["usage"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from Claude AI
    """
    try:
        client = ClaudeAIClient()

        # Convert ChatMessage objects to dicts
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

        async def generate():
            for chunk in client.chat(
                message=request.message,
                conversation_history=history,
                stream=True
            ):
                import json
                yield f"data: {json.dumps(chunk)}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/extract-params")
async def extract_params(request: ExtractParamsRequest):
    """
    Extract structured discovery parameters from conversation
    """
    try:
        client = ClaudeAIClient()

        # Convert ChatMessage objects to dicts
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

        params = client.extract_discovery_params(history)

        return params

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
