# Worker Brief — Issue 8: POST /chat Endpoint with Multi-Turn Session Management

**Working directory:** `/workspace`
**Issue:** Issue 8 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-chat-endpoint-report.md`

---

## Context

Issues 1–7 built everything except the chat endpoint itself. The LangGraph graph is compiled and stored at `app.state.graph`. Session history lives at `app.state.sessions`. You have one job: add `POST /chat` to `backend/api/routes.py`.

You touch exactly ONE file: `backend/api/routes.py`. No other files.

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest`. PATH includes `/home/claude/.local/bin`.

---

## What Already Exists

**`backend/api/routes.py`** — current state:
```python
"""
API route handlers for docuFetch.
...
"""
import os
from fastapi import APIRouter, Request
from backend.ingestion.pipeline import run_ingestion

router = APIRouter()

@router.post("/ingest")
def ingest(request: Request): ...

@router.get("/ingest/status")
def ingest_status(request: Request): ...
```

**`app.state.graph`** — the compiled LangGraph graph. Invoke it with:
```python
result = app.state.graph.invoke({"query": str, "messages": list})
```
The result dict contains:
- `result["messages"]` — updated list of HumanMessage + AIMessage objects
- `result["messages"][-1].content` — the answer string (last AIMessage)
- `result["sources"]` — `list[str]` of unique source filenames (e.g. `["policy.pdf"]`)

**`app.state.sessions`** — plain dict: `{session_id: list[messages]}`. Already initialized to `{}` in the server lifespan. History is the same list of LangChain message objects that the graph uses.

---

## What to Build

Add `POST /chat` to `backend/api/routes.py`. Two additions:
1. A `ChatRequest` Pydantic model
2. The `chat` route handler

```python
from pydantic import BaseModel

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
```

That is the complete implementation. Do not add anything beyond this.

---

## Acceptance Criteria (verify all before reporting done)

- [ ] `POST /chat` with `{"query": "...", "session_id": "uuid"}` returns HTTP 200 with `{"answer": "...", "sources": [...], "session_id": "uuid"}`
- [ ] Two requests with the same `session_id` — the second is contextually aware of the first (same session history used)
- [ ] Two requests with different `session_ids` — treated as independent conversations
- [ ] `session_id` in the response matches the `session_id` sent in the request
- [ ] `sources` is a list (may be empty if no relevant documents found)

---

## How to Verify

Write a scratch test using FastAPI's TestClient (no live server needed):

```python
from fastapi.testclient import TestClient
from backend.api.server import app

client = TestClient(app)

# Test: basic schema
resp = client.post("/chat", json={"query": "hello", "session_id": "test-session-1"})
print(f"Status: {resp.status_code}")
print(f"Body: {resp.json()}")
assert resp.status_code == 200
body = resp.json()
assert "answer" in body
assert "sources" in body
assert isinstance(body["sources"], list)
assert body["session_id"] == "test-session-1"
print("Schema test passed")

# Test: different session IDs are independent
resp_a = client.post("/chat", json={"query": "My name is Alice", "session_id": "session-a"})
resp_b = client.post("/chat", json={"query": "What is 2+2?", "session_id": "session-b"})
assert resp_a.status_code == 200
assert resp_b.status_code == 200
print("Session isolation test passed")

print("All chat endpoint tests passed")
```

Run: `cd /workspace && python3 scratch_chat.py`

Note: TestClient will start the full app including the scheduler lifespan. If `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY` are not set, the server may raise on startup. If keys are unavailable, test by running the server manually and using curl, OR verify by code inspection and note this in your report.

---

## Coding Standards

- Add docstrings to all new functions and classes
- Do not touch any other file
- Keep the implementation minimal — exactly what's specified

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-chat-endpoint-report.md` with:
1. Status: DONE or FAILED
2. Exact lines added to routes.py
3. Verification output (TestClient output or curl output)
4. Any deviations and why
5. What Issue 9 (CLI client) needs to know:
   - POST /chat request body format: `{"query": str, "session_id": str}`
   - POST /chat response format: `{"answer": str, "sources": list[str], "session_id": str}`
   - The session_id is echoed back unchanged
