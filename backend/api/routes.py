"""
API route handlers for docuFetch.

Exposes: POST /ingest (manual trigger), GET /ingest/status, and POST /chat
for multi-turn conversational Q&A backed by LangGraph session history.
"""
import os
from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.ingestion.pipeline import run_ingestion

router = APIRouter()


@router.post("/ingest")
def ingest(request: Request):
    """Trigger an immediate ingestion run over WATCH_FOLDER."""
    result = run_ingestion(
        os.getenv("WATCH_FOLDER", ""),
        request.app.state.chroma_store,
        request.app.state.embedder,
        os.getenv("HASH_STORE_PATH", "./hash_store.json"),
    )
    request.app.state.ingestion_status = result
    return {"message": "Ingestion complete", "doc_count": result["doc_count"]}


@router.get("/ingest/status")
def ingest_status(request: Request):
    """Return doc_count, last_run_at, and last_error from the last ingestion run."""
    if not hasattr(request.app.state, "ingestion_status"):
        return {"doc_count": 0, "last_run_at": None, "last_error": None}
    return request.app.state.ingestion_status


class ChatRequest(BaseModel):
    """Request body for the POST /chat endpoint."""

    query: str
    session_id: str


@router.post("/chat")
def chat(req: ChatRequest, request: Request):
    """
    Accept a query and session_id, invoke the LangGraph pipeline with the
    session's conversation history, update the history, and return the answer,
    source filenames, and session_id.

    Session history is capped at 20 messages before the LLM call (the graph
    handles trimming internally, but we also enforce it here when loading history).
    """
    # Load or create session history
    sessions = request.app.state.sessions
    history = sessions.get(req.session_id, [])

    # Trim to 20 before passing to graph
    trimmed_history = history[-20:] if len(history) > 20 else history

    # Invoke graph
    result = request.app.state.graph.invoke({
        "query": req.query,
        "messages": trimmed_history,
    })

    # Update session history
    sessions[req.session_id] = result["messages"]

    # Extract answer from last message
    answer = result["messages"][-1].content if result.get("messages") else ""
    sources = result.get("sources", [])

    return {
        "answer": answer,
        "sources": sources,
        "session_id": req.session_id,
    }
