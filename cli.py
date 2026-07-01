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
