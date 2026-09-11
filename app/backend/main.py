"""
CareerBridge AI - FastAPI Application Server
Provides REST API endpoints for chat, session resets, and system health.
"""
import uuid
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.backend.chatbot import process_chat_message
from app.backend.memory import memory_store

app = FastAPI(
    title="CareerBridge AI API",
    description=(
        "Production-ready backend API for CareerBridge AI — specialized for UN Sustainable "
        "Development Goal 8: Decent Work and Economic Growth. Provides intelligent career guidance, "
        "skill-gap roadmaps, interview simulation, resume critique, and persistent session memory."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local Streamlit frontend and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's query or conversational input.")
    session_id: Optional[str] = Field(default=None, description="Unique session identifier for conversation memory.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The assistant's markdown-formatted response.")
    session_id: str = Field(..., description="The active session identifier.")
    readiness_snapshot: Optional[Dict[str, Any]] = Field(default=None, description="Structured Career Readiness Snapshot.")

class ResetRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier to reset.")

class ResetResponse(BaseModel):
    status: str
    session_id: str
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    sdg: str
    version: str

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensures no raw Python tracebacks are exposed to users."""
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong while generating the response. Please try again."}
    )

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint to verify backend service status and SDG 8 readiness."""
    return HealthResponse(
        status="ok",
        service="CareerBridge AI",
        sdg="SDG 8: Decent Work & Economic Growth",
        version="1.0.0"
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Main conversational endpoint:
    - Enforces message presence
    - Injects and preserves session memory & extracted profile
    - Checks Responsible AI guardrails (SDG 8 alignment)
    - Returns structured answer and optional Career Readiness Snapshot
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    # Use provided session_id or auto-generate a new one
    active_session_id = request.session_id.strip() if request.session_id and request.session_id.strip() else str(uuid.uuid4())

    result = process_chat_message(active_session_id, request.message)

    if result.get("status_code", 200) != 200:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result.get("error", "Error processing request")
        )

    return ChatResponse(
        response=result["response"],
        session_id=result["session_id"],
        readiness_snapshot=result.get("readiness_snapshot")
    )

@app.post("/reset", response_model=ResetResponse, tags=["Session"])
async def reset_endpoint(request: ResetRequest):
    """Resets conversational history and profile memory for the specified session ID."""
    if not request.session_id or not request.session_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id cannot be empty"
        )
    memory_store.reset_session(request.session_id)
    return ResetResponse(
        status="ok",
        session_id=request.session_id,
        message="Session memory reset successfully"
    )
