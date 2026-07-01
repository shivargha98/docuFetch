# Worker Brief — Issue 9: CLI Client

**Working directory:** `/workspace`
**Issue:** Issue 9 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-cli-report.md`

---

## Context

All 8 backend issues are complete. The FastAPI server is running with POST /chat, GET /health, POST /ingest, and GET /ingest/status. You are building the standalone CLI client that lets a user interact with the running server from the terminal.

You create exactly ONE file: `/workspace/cli.py` at the project root (not inside backend/).

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest`. PATH includes `/home/claude/.local/bin`.

---

## Server Endpoints (already built)

| Method | Path | Request | Response |
|--------|------|---------|----------|
| `POST` | `/chat` | `{"query": str, "session_id": str}` | `{"answer": str, "sources": list[str], "session_id": str}` |
| `GET` | `/health` | — | `{"status": "ok", "initial_ingestion_complete": bool}` |
| `POST` | `/ingest` | — | `{"message": str, "doc_count": int}` |
| `GET` | `/ingest/status` | — | `{"doc_count": int, "last_run_at": str|null, "last_error": str|null}` |

Server runs at `http://localhost:8000` by default.

---

## What to Build: `/workspace/cli.py`

```python
"""
Interactive CLI client for docuFetch.

Connects to a running docuFetch FastAPI server at http://localhost:8000.
Generates a UUID4 session ID on startup and reuses it for the entire session
to support multi-turn conversation.

Usage:
    python cli.py

Commands:
    /ingest   — trigger an immediate ingestion run on the server
    /status   — display current ingestion status (doc count, last run, errors)
    /quit     — exit the CLI cleanly
    <text>    — send any other input as a query to POST /chat
"""
import sys
import uuid

import httpx

SERVER_URL = "http://localhost:8000"


def main() -> None:
    """Entry point: generate session ID, run the prompt loop."""
    session_id = str(uuid.uuid4())
    print(f"docuFetch CLI — session {session_id[:8]}... (type /quit to exit)")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if not user_input:
            continue

        if user_input == "/quit":
            sys.exit(0)
        elif user_input == "/ingest":
            _handle_ingest()
        elif user_input == "/status":
            _handle_status()
        else:
            _handle_chat(user_input, session_id)


def _handle_chat(query: str, session_id: str) -> None:
    """Send a query to POST /chat and print the answer and sources."""
    try:
        resp = httpx.post(
            f"{SERVER_URL}/chat",
            json={"query": query, "session_id": session_id},
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"\n{data['answer']}")
        if data.get("sources"):
            sources_fmt = ", ".join(f"[source: {s}]" for s in data["sources"])
            print(f"Sources: {sources_fmt}")
        print()
    except httpx.ConnectError:
        print(f"Server not reachable at {SERVER_URL}. Is the server running?")
    except httpx.HTTPStatusError as exc:
        print(f"Server returned error {exc.response.status_code}: {exc.response.text}")
    except Exception as exc:
        print(f"Unexpected error: {exc}")


def _handle_ingest() -> None:
    """Call POST /ingest and print the confirmation message."""
    try:
        resp = httpx.post(f"{SERVER_URL}/ingest", timeout=120.0)
        resp.raise_for_status()
        data = resp.json()
        print(f"Ingestion triggered: {data.get('message', 'done')} ({data.get('doc_count', 0)} documents)")
    except httpx.ConnectError:
        print(f"Server not reachable at {SERVER_URL}. Is the server running?")
    except Exception as exc:
        print(f"Error: {exc}")


def _handle_status() -> None:
    """Call GET /ingest/status and print the result in readable format."""
    try:
        resp = httpx.get(f"{SERVER_URL}/ingest/status", timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        print(f"Documents indexed: {data.get('doc_count', 0)}")
        last_run = data.get("last_run_at") or "never"
        print(f"Last run: {last_run}")
        err = data.get("last_error")
        if err:
            print(f"Last error: {err}")
        else:
            print("Last error: none")
    except httpx.ConnectError:
        print(f"Server not reachable at {SERVER_URL}. Is the server running?")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
```

Implement this exactly as shown. No additional features.

---

## Acceptance Criteria (verify all before reporting done)

- [ ] Running `python3 cli.py` displays a `>` prompt
- [ ] Typing `/quit` exits the process with code 0
- [ ] The same `session_id` is used for all `/chat` calls in one CLI session
- [ ] `/ingest` calls `POST /ingest` and prints the confirmation
- [ ] `/status` calls `GET /ingest/status` and prints doc count, last run, last error
- [ ] If the server is not running, a readable error is printed (not a traceback)

---

## How to Verify

### Test 1 — code-only: session_id reuse and /quit behavior

Write a scratch test that imports the CLI's internals and simulates input (no live server needed for /quit and session_id verification):

```python
import sys, uuid

# Test 1: session_id is a valid UUID4
session_id = str(uuid.uuid4())
parsed = uuid.UUID(session_id, version=4)
assert str(parsed) == session_id
print("Test 1 passed: session_id is valid UUID4")

# Test 2: /quit exits with code 0
import subprocess
result = subprocess.run(
    ["python3", "/workspace/cli.py"],
    input="/quit\n",
    capture_output=True,
    text=True,
    timeout=5
)
assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
print("Test 2 passed: /quit exits cleanly")

# Test 3: server unreachable gives readable error (no traceback)
# Start CLI with a query to a non-running server (use a bogus port to ensure no server)
result = subprocess.run(
    ["python3", "-c",
     "import httpx; from backend.ingestion.pipeline import *; "
     # Actually test the CLI's error handling directly
    ],
    capture_output=True, text=True
)

# Simpler: test _handle_chat error handling directly
import importlib.util, io, unittest.mock

spec = importlib.util.spec_from_file_location("cli", "/workspace/cli.py")
cli_mod = importlib.util.load_from_spec(spec)
spec.loader.exec_module(cli_mod)

# Patch httpx.post to raise ConnectError
with unittest.mock.patch("httpx.post", side_effect=httpx.ConnectError("refused")):
    import io
    output = io.StringIO()
    sys.stdout = output
    cli_mod._handle_chat("test query", "fake-session-id")
    sys.stdout = sys.__stdout__
    out = output.getvalue()
    assert "not reachable" in out.lower() or "server" in out.lower()
    assert "Traceback" not in out
    print(f"Test 3 passed: readable error printed: {out.strip()}")

print("All CLI tests passed")
```

Actually the import approach is fragile. Use the simpler subprocess approach:

```python
import subprocess, sys

# Test /quit exits 0
result = subprocess.run(
    ["python3", "/workspace/cli.py"],
    input="/quit\n",
    capture_output=True,
    text=True,
    timeout=5,
    cwd="/workspace"
)
assert result.returncode == 0, f"Got exit code {result.returncode}. stderr: {result.stderr}"
print(f"Test: /quit exits 0 — PASSED")
print(f"stdout: {repr(result.stdout)}")
```

For the server-unreachable test (change SERVER_URL in the module to a bad port, or run a quick subprocess test):
```python
# Test: query to unavailable server shows readable error
test_script = '''
import sys
sys.path.insert(0, "/workspace")
# Temporarily override the server URL to a port with no server
import cli
cli.SERVER_URL = "http://localhost:19999"
import io
out = io.StringIO()
sys.stdout = out
cli._handle_chat("test", "session-x")
sys.stdout = sys.__stdout__
output = out.getvalue()
assert "not reachable" in output or "Server" in output, f"Got: {output}"
assert "Traceback" not in output, "Got a traceback!"
print("Unreachable server test PASSED:", output.strip())
'''
result = subprocess.run(["python3", "-c", test_script], capture_output=True, text=True, cwd="/workspace")
print(result.stdout)
if result.returncode != 0:
    print("FAILED:", result.stderr)
```

---

## Coding Standards

- Module-level docstring at the top of cli.py (already written above)
- Every function must have a docstring
- Simplicity — the implementation above is complete; do not add features

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-cli-report.md` with:
1. Status: DONE or FAILED
2. `/workspace/cli.py` line count and confirmation it was created
3. Verification outputs:
   - `/quit` exit code 0 test result
   - Server-unreachable error handling test result
   - Session ID UUID4 validity
4. Any deviations and why
